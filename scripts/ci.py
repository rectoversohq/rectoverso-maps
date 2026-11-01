"""Run the deck's CI locally or in Actions; output is never a release approval."""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--base', help='PR base or previous push commit; omitted only for bootstrap/manual rebuilds')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.is_relative_to(ROOT):
        parser.error('Output must be outside the source checkout')
    out.mkdir(parents=True, exist_ok=False)
    temporary = out / 'tmp'
    temporary.mkdir()
    env = os.environ | {'TMPDIR': str(temporary), 'PYTHONDONTWRITEBYTECODE': '1', 'ANKI_PYTHON': sys.executable}
    report = {'passed': False, 'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'python': sys.version, 'platform': platform.platform(),
              'workingTreeDirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT)),
              'baseline': args.base, 'steps': [], 'packageSource': 'source-build-candidate'}

    def run(name, *command):
        with (out / (name + '.log')).open('w') as log:
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        report['steps'].append({'name': name, 'exitCode': result.returncode})
        if result.returncode:
            raise RuntimeError(f'{name} failed; see {out / (name + ".log")}')
        print(f'{name}: passed', flush=True)

    try:
        for name, path in [('verify-coverage', 'scripts/checks/verify-coverage.py'),
                           ('test-source', 'tests/test-source.py'),
                           ('test-render-pngs', 'tests/test-render-pngs.py'),
                           ('test-identities', 'tests/test-identities.py'),
                           ('test-regions', 'tests/test-regions.py'),
                           ('test-upgrade-baseline', 'tests/test-upgrade-baseline.py')]:
            run(name, sys.executable, '-B', str(ROOT / path))
        if args.base:
            run('base-identities', sys.executable, '-B', str(ROOT / 'scripts/checks/check-identities.py'),
                args.base, str(out / 'base-identities.json'))
        for name in ('packages', 'rebuilt'):
            run(name, 'bash', str(ROOT / 'scripts/build.sh'), str(out / name))
        meta = json.loads((ROOT / 'rectoverso.json').read_text())
        for language, artifact in meta['languages'].items():
            filename = artifact['package']['file']
            run('rebuild-' + language, sys.executable, str(ROOT / 'scripts/checks/validate-rebuild.py'),
                str(out / 'packages' / filename), str(out / 'rebuilt' / filename),
                str(out / ('rebuild-' + language + '.json')))
        if meta.get('upgradeBaseline'):
            run('upgrade-baseline', sys.executable, str(ROOT / 'scripts/checks/fetch-upgrade-baseline.py'), str(out / 'upgrade-baseline'))
            for language, artifact in meta['languages'].items():
                old = meta['upgradeBaseline']['languages'][language]['file']
                run('release-upgrade-' + language, sys.executable, str(ROOT / 'scripts/checks/validate-upgrade.py'),
                    str(out / 'upgrade-baseline' / old), str(out / 'packages' / artifact['package']['file']),
                    str(out / ('release-upgrade-' + language + '.json')))
        report['passed'] = True
    finally:
        (out / 'ci.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
