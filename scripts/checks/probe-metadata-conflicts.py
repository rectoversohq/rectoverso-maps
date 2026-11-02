"""Disposable Maps research: field-only import conflicts, refusal and recovery.

Accepts packages, never an existing profile. This is not a migration command.
All guards are research assertions; Anki's ordinary import UI does not provide
these per-field/GUID/schema preconditions or a check-and-import transaction.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import tempfile

from anki import _backend
from anki.collection import Collection
from anki.cards_pb2 import FsrsMemoryState
from anki.import_export_pb2 import (
    ImportAnkiPackageOptions,
    ImportAnkiPackageRequest,
    ImportCsvRequest,
)

TARGETS = ("Continent", "RectoVerso search")


def load(col, package):
    result = col.import_anki_package(
        ImportAnkiPackageRequest(
            package_path=str(package.resolve()),
            options=ImportAnkiPackageOptions(
                merge_notetypes=True,
                with_scheduling=True,
                update_notes=0,
                update_notetypes=0,
            ),
        )
    )
    col.models._clear_cache()
    return {
        key: len(getattr(result.log, key))
        for key in ("new", "updated", "duplicate", "conflicting")
    }


def snapshot(col):
    notes = [col.get_note(nid) for nid in col.find_notes("")]
    models = {n.mid for n in notes}
    review_logs = {
        cid: [entry.SerializeToString().hex() for entry in col.get_review_logs(cid)]
        for cid in col.find_cards("")
    }
    return {
        "notes": sorted(
            (n.id, n.guid, n.mid, dict(n.items()), sorted(n.tags)) for n in notes
        ),
        "cards": sorted(
            (
                c.id,
                c.nid,
                c.did,
                c.ord,
                c.type,
                c.queue,
                c.ivl,
                c.due,
                c.factor,
                c.reps,
                c.lapses,
                c.memory_state.SerializeToString().hex() if c.memory_state else None,
                c.desired_retention,
            )
            for c in (col.get_card(cid) for cid in col.find_cards(""))
        ),
        "reviewLogs": {cid: entries for cid, entries in review_logs.items() if entries},
        "models": {
            mid: {
                "fields": [(f["name"], f["id"]) for f in col.models.get(mid)["flds"]],
                "templates": [
                    (t["id"], t["qfmt"], t["afmt"])
                    for t in col.models.get(mid)["tmpls"]
                ],
                "css": col.models.get(mid)["css"],
            }
            for mid in models
        },
    }


def refusal(col, target, rows):
    expected = {n[1]: n for n in target["notes"]}
    row_guids = [row[0] for row in rows]
    if len(row_guids) != len(set(row_guids)):
        return "duplicate-tsv-guid"
    if set(row_guids) != set(expected):
        return "tsv-guid-coverage"
    if any(
        row[1:] != [expected[row[0]][3][field] for field in TARGETS] for row in rows
    ):
        return "tsv-values-differ-from-reviewed-candidate"
    current = snapshot(col)
    guids = [n[1] for n in current["notes"]]
    if len(guids) != len(set(guids)):
        return "duplicate-collection-guid"
    if set(guids) != set(expected):
        return "collection-guid-coverage"
    for nid, guid, mid, fields, tags in current["notes"]:
        if mid != expected[guid][2]:
            return "wrong-note-type"
        schema = current["models"][mid]["fields"]
        expected_schema = target["models"][mid]["fields"]
        if len({f[0] for f in schema}) != len(schema) or len(
            {f[1] for f in schema}
        ) != len(schema):
            return "ambiguous-field-identities"
        if not all(pair in schema for pair in expected_schema):
            return "field-identity-or-name-mismatch"
        for field in TARGETS:
            if fields[field] not in ("", expected[guid][3][field]):
                return "personal-target-field-conflict"
    return None


def text_import(col, path, rows, mid, preserve=False):
    with path.open("w", newline="") as output:
        output.write("#separator:tab\n#html:true\n#guid column:1\n")
        csv.writer(output, delimiter="\t", lineterminator="\n").writerows(rows)
    meta = col.get_csv_metadata(str(path), None)
    meta.guid_column = 1
    meta.global_notetype.id = mid
    del meta.global_notetype.field_columns[:]
    for field in col.models.get(mid)["flds"]:
        meta.global_notetype.field_columns.append(
            {"Continent": 2, "RectoVerso search": 3}.get(field["name"], 0)
        )
    meta.global_tags.clear()
    meta.updated_tags.clear()
    meta.dupe_resolution = 1 if preserve else 0
    result = col.import_csv(ImportCsvRequest(path=str(path), metadata=meta))
    return {
        key: len(getattr(result.log, key))
        for key in ("new", "updated", "duplicate", "conflicting")
    }


def prepared_collection(path, original, candidate):
    path.mkdir()
    col = Collection(str(path / "collection.anki2"))
    load(col, original)
    study_card = col.get_card(col.find_cards("")[0])
    col.decks.select(study_card.did)
    col.sched.reset()
    studied = col.sched.getCard()
    assert studied is not None
    col.sched.answerCard(studied, 3)
    assert col.get_review_logs(studied.id)
    first = col.get_note(col.find_notes("")[0])
    mid = first.mid
    model = col.models.get(mid)
    col.models.add_field(model, col.models.new_field("My personal notes"))
    model["css"] += "\n/* personal stylesheet */\n"
    col.models.update_dict(model)
    for index, nid in enumerate(col.find_notes("")):
        note = col.get_note(nid)
        note["My personal notes"] = f"Personal field {index}"
        note.tags.append("personal::retain")
        if index % 17 == 0:
            note.fields[0] += " — personal learner wording"
        col.update_note(note)
    for index, cid in enumerate(col.find_cards("")):
        card = col.get_card(cid)
        card.type = card.queue = 2
        card.ivl, card.due, card.factor = 17 + index % 9, 30 + index % 7, 2500
        card.reps, card.lapses = 4 + index % 5, index % 3
        card.memory_state = FsrsMemoryState(
            stability=12.25 + index % 5, difficulty=5.125
        )
        card.desired_retention = 0.9
        col.update_card(card)
    before = snapshot(col)
    load(col, candidate)
    merged = snapshot(col)
    assert (
        before["cards"] == merged["cards"]
        and before["reviewLogs"] == merged["reviewLogs"]
    )
    assert all(n[3][field] == "" for n in merged["notes"] for field in TARGETS)
    return col, mid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output = args.output.resolve()
    if args.output.is_relative_to(Path(__file__).resolve().parents[2]):
        parser.error("Evidence must be outside this source repository")
    args.output.mkdir(parents=True, exist_ok=False)
    results = []
    with tempfile.TemporaryDirectory(
        prefix="disposable-", dir=args.output
    ) as temporary:
        root = Path(temporary)
        (root / "target").mkdir()
        target_col = Collection(str(root / "target/collection.anki2"))
        try:
            load(target_col, args.candidate)
            target = snapshot(target_col)
        finally:
            target_col.close()
        rows = [[n[1], *[n[3][field] for field in TARGETS]] for n in target["notes"]]
        assert len(rows) == 288
        cases = [
            "empty",
            "already-matching",
            "partly-matching",
            "personal-continent",
            "personal-search",
            "renamed-field",
            "wrong-field-id",
            "missing-guid",
            "extra-guid",
            "duplicate-guid",
            "tsv-wrong-guid",
            "tsv-duplicate-guid",
            "tsv-different-values",
            "unguarded-overwrite",
            "preserve-existing",
        ]
        for case in cases:
            col, mid = prepared_collection(root / case, args.original, args.candidate)
            try:
                own_rows = [row.copy() for row in rows]
                first = col.get_note(col.find_notes("")[0])
                expected = {n[1]: n for n in target["notes"]}
                if case in ("already-matching", "partly-matching"):
                    for index, nid in enumerate(col.find_notes("")):
                        if case == "partly-matching" and index % 2:
                            continue
                        note = col.get_note(nid)
                        for field in TARGETS:
                            note[field] = expected[note.guid][3][field]
                        col.update_note(note)
                elif case in (
                    "personal-continent",
                    "unguarded-overwrite",
                    "preserve-existing",
                ):
                    first["Continent"] = "My preferred regional classification"
                    col.update_note(first)
                elif case == "personal-search":
                    first["RectoVerso search"] = (
                        '{"v":1,"fields":[{"name":"Personal topic","values":["Travel"]}]}'
                    )
                    col.update_note(first)
                elif case in ("renamed-field", "wrong-field-id"):
                    model = col.models.get(mid)
                    field = next(f for f in model["flds"] if f["name"] == "Continent")
                    if case == "renamed-field":
                        field["name"] = "My continent"
                    else:
                        field["id"] += 999
                    col.models.update_dict(model)
                elif case == "missing-guid":
                    col.remove_notes([first.id])
                elif case in ("extra-guid", "duplicate-guid"):
                    extra = col.new_note(col.models.get(mid))
                    extra.guid = (
                        first.guid
                        if case == "duplicate-guid"
                        else "maps-research-unknown-guid"
                    )
                    for name, value in first.items():
                        extra[name] = value
                    col.add_note(extra, col.get_card(col.find_cards("")[0]).did)
                elif case == "tsv-wrong-guid":
                    own_rows[0][0] = "maps-research-wrong-guid"
                elif case == "tsv-duplicate-guid":
                    own_rows.append(own_rows[0].copy())
                elif case == "tsv-different-values":
                    own_rows[0][1] = "Changed after review"
                before = snapshot(col)
                reason = refusal(col, target, own_rows)
                assert (
                    snapshot(col) == before
                ), "Read-only refusal check changed collection"
                result = {
                    "case": case,
                    "refusal": reason,
                    "preflightChangedNothing": True,
                }
                if case in ("empty", "already-matching", "partly-matching"):
                    assert reason is None
                    result["import"] = text_import(
                        col, args.output / (case + ".tsv"), own_rows, mid
                    )
                    after = snapshot(col)
                    assert (
                        after["cards"] == before["cards"]
                        and after["models"] == before["models"]
                    )
                    assert after["reviewLogs"] == before["reviewLogs"]
                    for old, new in zip(before["notes"], after["notes"]):
                        assert old[:3] == new[:3] and old[4] == new[4]
                        assert all(
                            new[3][key] == value
                            for key, value in old[3].items()
                            if key not in TARGETS
                        )
                        assert all(
                            new[3][key] == expected[new[1]][3][key] for key in TARGETS
                        )
                    result["all288MetadataApplied"] = True
                    result["personalFieldsTagsModelsAndAllSchedulesPreserved"] = True
                    result["realReviewLogPreserved"] = True
                    again = snapshot(col)
                    result["repeatImport"] = text_import(
                        col, args.output / (case + "-repeat.tsv"), own_rows, mid
                    )
                    assert snapshot(col) == again
                    result["repeatIsIdempotent"] = True
                elif case in ("unguarded-overwrite", "preserve-existing"):
                    assert reason == "personal-target-field-conflict"
                    backup_dir = args.output / (case + "-backups")
                    backup_dir.mkdir()
                    assert col.create_backup(
                        backup_folder=str(backup_dir),
                        force=True,
                        wait_for_completion=True,
                    )
                    backup = next(backup_dir.glob("*.colpkg"))
                    result["import"] = text_import(
                        col,
                        args.output / (case + ".tsv"),
                        own_rows,
                        mid,
                        preserve=case == "preserve-existing",
                    )
                    after = snapshot(col)
                    actual = {n[1]: n for n in after["notes"]}
                    result["personalTargetPreserved"] = (
                        actual[first.guid][3]["Continent"] == first["Continent"]
                    )
                    result["completeMetadataRows"] = sum(
                        all(
                            n[3][field] == expected[n[1]][3][field] for field in TARGETS
                        )
                        for n in after["notes"]
                    )
                    assert result["personalTargetPreserved"] == (
                        case == "preserve-existing"
                    )
                    if case == "unguarded-overwrite":
                        status = col.undo_status()
                        result["undoOperation"] = status.undo
                        col.undo()
                        col.models._clear_cache()
                        assert snapshot(col) == before
                        result["nativeUndoRestoresExactSemanticState"] = True
                    else:
                        assert after == before
                    restored_dir = root / (case + "-restore")
                    restored_dir.mkdir()
                    backend = _backend.RustBackend()
                    backend.import_collection_package(
                        col_path=str(restored_dir / "collection.anki2"),
                        backup_path=str(backup),
                        media_folder=str(restored_dir / "collection.media"),
                        media_db=str(restored_dir / "collection.media.db"),
                    )
                    restored = Collection(str(restored_dir / "collection.anki2"))
                    try:
                        assert snapshot(restored) == before
                    finally:
                        restored.close()
                    result["nativeBackupRestoresNotesModelsAndAllSchedules"] = True
                    result["backupIncludesMedia"] = False
                    result["backupSHA256"] = hashlib.sha256(
                        backup.read_bytes()
                    ).hexdigest()
                else:
                    assert reason is not None, case
                    result["importRefusedWithoutMutation"] = True
                results.append(result)
                (args.output / "progress.json").write_text(
                    json.dumps(results, indent=2) + "\n"
                )
                print(case + ": verified", flush=True)
            finally:
                col.close()
    report = {
        "anki": "26.09.3",
        "researchOnly": True,
        "passed": True,
        "defaultSafeAPKG": False,
        "releaseReady": False,
        "cases": results,
        "limit": "Native TSV UPDATE overwrites nonempty mapped personal metadata. PRESERVE skips whole notes and leaves the intended metadata absent. Normal UI provides no conditional empty-or-equal field guard, exact GUID/schema validation or check-and-import transaction. Research guards require a separate reviewed tool/add-on or explicit manual audit; this is not that tool.",
        "recovery": "Immediate native Undo and isolated automatic-backup restore preserve all checked note/model/card/schedule/FSRS data and the real review log. Automatic backups omit media; TSV does not change media. Full-profile restore discards later work and is not a selective rollback.",
        "desktopUI": "Not operated; equivalent field mappings and GUID support are documented in the official manual.",
    }
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps({key: value for key, value in report.items() if key != "cases"}),
        flush=True,
    )


if __name__ == "__main__":
    main()
