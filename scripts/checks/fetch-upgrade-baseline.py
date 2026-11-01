"""Fetch an explicitly pinned, checksum-verified prior release for Anki CI."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = 'https://github.com/rectoversohq/rectoverso-maps'


def validate(baseline):
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[a-z0-9.]+)?', baseline['version']):
        raise ValueError('Invalid baseline version')
    if set(baseline['languages']) != {'en', 'fr'}:
        raise ValueError('Baseline must cover both languages')
    for package in baseline['languages'].values():
        filename = package['file']
        if Path(filename).name != filename or not filename.endswith('.apkg'):
            raise ValueError('Invalid baseline filename')
        expected = f'{REPOSITORY}/releases/download/v{baseline["version"]}/{filename}'
        if (package['url'] != expected or not re.fullmatch('[0-9a-f]{64}', package['sha256'])
                or type(package['bytes']) is not int or package['bytes'] <= 0):
            raise ValueError('Baseline URL/hash/size differs from the pinned release')
    return baseline


def download(package, destination):
    path = destination / package['file']
    temporary = path.with_suffix('.download')
    digest = hashlib.sha256()
    size = 0
    started = time.monotonic()
    with urllib.request.urlopen(package['url'], timeout=60) as response, temporary.open('wb') as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > package['bytes'] or time.monotonic() - started > 180:
                raise ValueError('Baseline transfer exceeded size/time limit')
            output.write(chunk)
            digest.update(chunk)
    if size != package['bytes'] or digest.hexdigest() != package['sha256']:
        raise ValueError('Baseline download checksum/size mismatch')
    temporary.replace(path)
    return {'file': path.name, 'sha256': digest.hexdigest(), 'bytes': size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    destination = args.output.resolve()
    if destination.is_relative_to(ROOT):
        raise ValueError('Baseline output must be outside source')
    baseline = validate(json.loads((ROOT / 'rectoverso.json').read_text())['upgradeBaseline'])
    destination.mkdir(parents=True, exist_ok=False)
    results = [{'language': language, **download(package, destination)}
               for language, package in baseline['languages'].items()]
    report = {'version': baseline['version'], 'packages': results, 'passed': True}
    (destination / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Verified both frozen published upgrade-baseline packages.')


if __name__ == '__main__':
    main()
