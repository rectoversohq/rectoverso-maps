"""Render each SVG in a fresh WebKit process, with bounded recovery.

Usage: python3 render-pngs.py <converter> <drawing-directory> <height>
The caller's final drawing comparison remains the authority for image content.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile


def render(converter, source, destination, height, *, attempts=3, timeout=60):
    if destination.exists():
        raise FileExistsError(f'Refusing to reuse or overwrite {destination}')
    failures = []
    for attempt in range(1, attempts + 1):
        # A failed process may leave a partial PNG. Only a successful attempt's
        # isolated output can become the final drawing.
        with tempfile.TemporaryDirectory(prefix='.render-', dir=destination.parent) as temporary:
            candidate = Path(temporary) / destination.name
            try:
                result = subprocess.run(
                    [str(converter), temporary, str(height), str(source)],
                    capture_output=True, text=True, timeout=timeout,
                )
                detail = (result.stdout + result.stderr).strip()
                if result.returncode == 0 and candidate.is_file() and candidate.stat().st_size:
                    candidate.replace(destination)
                    if detail:
                        print(detail, flush=True)
                    print(f'Rendered {source.name} (attempt {attempt}/{attempts})', flush=True)
                    return
                reason = detail or ("missing or empty PNG" if result.returncode == 0 else "converter failed without diagnostics")
                failure = f'exit {result.returncode}; {reason}'
            except subprocess.TimeoutExpired:
                failure = f'timed out after {timeout:g}s'
            failures.append(f'attempt {attempt}/{attempts}: {failure}')
            print(f'Failed {source.name}: {failures[-1]}', flush=True)
    raise RuntimeError(f'{source.name}: no accepted PNG after {attempts} fresh processes; ' + '; '.join(failures))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('converter', type=Path)
    parser.add_argument('directory', type=Path)
    parser.add_argument('height', type=int)
    args = parser.parse_args()
    files = sorted(args.directory.glob('*.svg'))
    if not files or args.height <= 0:
        parser.error('Supply a directory containing SVGs and a positive height')
    for source in files:
        render(args.converter.resolve(), source.resolve(), source.with_suffix('.png'), args.height)


if __name__ == '__main__':
    main()
