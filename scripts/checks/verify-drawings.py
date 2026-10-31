"""Compare regenerated drawings and place records with the tracked source."""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
source = root / 'source'
drawn = Path(sys.argv[1])
places = json.loads((source / 'places.json').read_text())
if json.loads((drawn / 'places.json').read_text()) != places:
    raise ValueError('Regenerated place records differ')
for place in places:
    for original, regenerated in [(root / 'artwork/svg' / (place['code'] + '.svg'), drawn / (place['code'] + '.svg')),
                                   (source / 'media' / place['picture'], drawn / (place['code'] + '.png'))]:
        if original.read_bytes() != regenerated.read_bytes():
            raise ValueError(f'Regenerated drawing differs: {original.name}')
print(f'{len(places)} SVGs and PNGs byte-identical; place records equal')
