"""Fetch the pinned Natural Earth layers into the directory supplied by the caller."""
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

destination=Path(sys.argv[1]);destination.mkdir(parents=True,exist_ok=True)
expected=json.loads((Path(__file__).resolve().parents[2]/'source/geography/natural-earth-sha256.json').read_text())
for name,checksum in expected.items():
    path=destination/name
    if not path.exists():
        url='https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/'+name
        temporary=path.with_suffix(path.suffix+'.download')
        urllib.request.urlretrieve(url,temporary)
        if hashlib.sha256(temporary.read_bytes()).hexdigest()!=checksum:
            temporary.unlink();raise ValueError('Checksum mismatch: '+name)
        temporary.replace(path)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=checksum:
        raise ValueError('Unexpected existing source: '+str(path))
    print('Verified '+name)
