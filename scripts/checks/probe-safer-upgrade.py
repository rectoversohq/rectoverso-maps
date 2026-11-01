"""Isolated research: compare package settings with field-only text import.

This never opens an existing Anki profile and is not a user migration tool.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import tempfile
from anki.collection import Collection
from anki.cards_pb2 import FsrsMemoryState
from anki.import_export_pb2 import (
    ImportAnkiPackageOptions,
    ImportAnkiPackageRequest,
    ImportCsvRequest,
)

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("original", type=Path)
p.add_argument("candidate", type=Path)
p.add_argument("output", type=Path)
a = p.parse_args()
a.output = a.output.resolve()
if a.output.is_relative_to(Path(__file__).resolve().parents[2]):
    p.error("Evidence must be outside the source repository")
a.output.mkdir(parents=True, exist_ok=False)


def load(col, path, merge=True, notes=0, types=0):
    result = col.import_anki_package(
        ImportAnkiPackageRequest(
            package_path=str(path.resolve()),
            options=ImportAnkiPackageOptions(
                merge_notetypes=merge,
                with_scheduling=True,
                update_notes=notes,
                update_notetypes=types,
            ),
        )
    )
    col.models._clear_cache()
    return {
        "new": len(result.log.new),
        "updated": len(result.log.updated),
        "duplicate": len(result.log.duplicate),
        "conflicting": len(result.log.conflicting),
    }


def notes(col):
    return {
        n.guid: {
            "id": n.id,
            "mid": n.mid,
            "fields": dict(n.items()),
            "tags": sorted(n.tags),
        }
        for n in (col.get_note(nid) for nid in col.find_notes(""))
    }


def cards(col):
    return {
        c.id: [
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
        ]
        for c in (col.get_card(cid) for cid in col.find_cards(""))
    }


results = []
with tempfile.TemporaryDirectory(prefix="isolated-", dir=a.output) as td:
    root = Path(td)
    (root / "target").mkdir()
    target = Collection(str(root / "target" / "collection.anki2"))
    try:
        load(target, a.candidate)
        expected = notes(target)
    finally:
        target.close()
    for key, merge, types, passes, csv_patch in [
        ("merge-disabled", False, 0, 1, False),
        ("merge-if-newer", True, 0, 1, False),
        ("merge-types-never", True, 2, 1, False),
        ("merge-types-always", True, 1, 1, False),
        ("repeat-default", True, 0, 2, False),
        ("guid-field-only-csv", True, 0, 1, True),
    ]:
        (root / key).mkdir()
        col = Collection(str(root / key / "collection.anki2"))
        try:
            load(col, a.original)
            original = notes(col)
            mids = {v["mid"] for v in original.values()}
            assert len(mids) == 1
            mid = next(iter(mids))
            model = col.models.get(mid)
            original_field_ids = {f["name"]: f["id"] for f in model["flds"]}
            field = col.models.new_field("My personal notes")
            col.models.add_field(model, field)
            model["css"] += "\n/* local style retained */\n"
            col.models.update_dict(model)
            for index, nid in enumerate(col.find_notes("")):
                n = col.get_note(nid)
                n["My personal notes"] = f"Personal note {index}"
                n.tags.append("personal::keep")
                if index % 17 == 0:
                    n.fields[0] += " — my learner wording"
                col.update_note(n)
            for index, cid in enumerate(col.find_cards("")):
                c = col.get_card(cid)
                c.type = 2
                c.queue = 2
                c.ivl = 17 + index % 9
                c.due = 30 + index % 7
                c.factor = 2500
                c.reps = 4 + index % 5
                c.lapses = index % 3
                c.memory_state = FsrsMemoryState(
                    stability=12.25 + index % 5, difficulty=5.125
                )
                c.desired_retention = 0.9
                col.update_card(c)
            before = notes(col)
            schedule = cards(col)
            logs = [
                load(col, a.candidate, merge=merge, types=types) for _ in range(passes)
            ]
            fields_after = {f["name"] for f in col.models.get(mid)["flds"]}
            if csv_patch:
                tsv = a.output / "metadata-only.tsv"
                with tsv.open("w", newline="") as f:
                    f.write("#separator:tab\n#html:true\n#guid column:1\n")
                    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
                    for guid, n in expected.items():
                        writer.writerow(
                            [
                                guid,
                                n["fields"]["Continent"],
                                n["fields"]["RectoVerso search"],
                            ]
                        )
                meta = col.get_csv_metadata(str(tsv), None)
                meta.guid_column = 1
                meta.global_notetype.id = mid
                del meta.global_notetype.field_columns[:]
                for field in col.models.get(mid)["flds"]:
                    meta.global_notetype.field_columns.append(
                        {"Continent": 2, "RectoVerso search": 3}.get(field["name"], 0)
                    )
                meta.global_tags.clear()
                meta.updated_tags.clear()
                result = col.import_csv(ImportCsvRequest(path=str(tsv), metadata=meta))
                logs.append(
                    {
                        "csvNew": len(result.log.new),
                        "csvUpdated": len(result.log.updated),
                        "csvDuplicate": len(result.log.duplicate),
                        "csvConflicting": len(result.log.conflicting),
                    }
                )
            actual = notes(col)
            roster_same = set(actual) == set(before)
            personal_preserved = roster_same and all(
                actual[g]["id"] == n["id"]
                and actual[g]["mid"] == n["mid"]
                and actual[g]["tags"] == n["tags"]
                and all(actual[g]["fields"].get(k) == v for k, v in n["fields"].items())
                for g, n in before.items()
            )
            applied = sum(
                all(
                    actual[g]["fields"].get(k) == expected[g]["fields"][k]
                    for k in ["Continent", "RectoVerso search"]
                )
                for g in before
            )
            model = col.models.get(mid)
            field_ids = {f["name"]: f["id"] for f in model["flds"]}
            report = {
                "case": key,
                "cards": col.card_count(),
                "metadataApplied": applied,
                "rosterPreserved": roster_same,
                "personalFieldsAnswersAndTagsPreserved": personal_preserved,
                "schedulingAndFSRSPreserved": cards(col) == schedule,
                "originalFieldIDsPreserved": all(
                    field_ids.get(k) == v for k, v in original_field_ids.items()
                ),
                "personalStylePreserved": "/* local style retained */" in model["css"],
                "appendedFields": sorted(
                    fields_after - set(before[next(iter(before))]["fields"])
                ),
                "logs": logs,
            }
            if csv_patch:
                assert applied == 288 and all(
                    report[k]
                    for k in [
                        "rosterPreserved",
                        "personalFieldsAnswersAndTagsPreserved",
                        "schedulingAndFSRSPreserved",
                        "originalFieldIDsPreserved",
                        "personalStylePreserved",
                    ]
                ), report
            results.append(report)
            print(json.dumps(report), flush=True)
        finally:
            col.close()
(a.output / "report.json").write_text(
    json.dumps(
        {
            "anki": "26.09.3",
            "packages": {
                key: {
                    "file": path.name,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
                for key, path in [("published", a.original), ("candidate", a.candidate)]
            },
            "researchOnly": True,
            "defaultSafeAPKG": False,
            "cases": results,
            "limitation": "The field-only text import is a separate explicit migration. It must not be run blindly if target metadata fields already contain personal content; no desktop operation or release approval is claimed.",
        },
        indent=2,
    )
    + "\n"
)
