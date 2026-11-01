"""Read shared Maps source and materialize one language's Anki inputs."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    resolved = (ROOT / path).resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError(f'Source path leaves the repository: {path}')
    return json.loads(resolved.read_text())


def metadata(language):
    shared = read('rectoverso.json')
    if shared['schemaVersion'] != 2:
        raise ValueError('Unsupported Maps metadata schema')
    languages = shared.pop('languages')
    if language not in languages:
        raise ValueError(f'Unsupported language: {language}')
    localized = languages[language]
    shared.update(id=localized['id'], deckID=shared['id'], language=language,
                  package=localized['package'],
                  sourceFiles=shared['sourceFiles'] | localized['sourceFiles'])
    return shared


def inputs(language):
    meta = metadata(language)
    source = meta['sourceFiles']
    translation = read(source['translation'])
    fields = translation['fields']
    places = read(source['places'])
    codes = {place['code'] for place in places}
    if not set(translation['boundaryNotes']) <= codes:
        raise ValueError('Boundary note names an unknown place')
    model, deck = read(source['noteType']), read(source['deck'])
    style = (ROOT / source['style']).resolve()
    if not style.is_relative_to(ROOT):
        raise ValueError('Style path leaves the repository')
    model['css'] = style.read_text()
    if set(fields.values()) != set(model['fields']) or len(fields) != 6:
        raise ValueError('Translation fields differ from note type')
    continents = read(source['continents'])
    if set(continents['assignments']) != codes:
        raise ValueError('Continent coverage differs from place roster')
    def search_fields(place):
        memberships = continents['assignments'][place['code']]
        if not memberships or len(set(memberships)) != len(memberships) or any(c not in continents['labels'] for c in memberships):
            raise ValueError('Invalid continent memberships')
        values = [continents['labels'][c][language] for c in memberships]
        aliases = sorted({continents['labels'][c][lang] for c in memberships for lang in ('en', 'fr')})
        region = json.loads(place['field'])['region']
        fields = [
            {'name': 'Continent', 'values': values, 'aliases': aliases},
            {'name': 'Region' if language == 'en' else 'Région', 'values': [region[language]], 'aliases': sorted(set(region.values()))},
            {'name': 'Place' if language == 'en' else 'Lieu', 'values': [place['name'][language]], 'aliases': sorted(set(place['name'].values()))},
        ]
        return '; '.join(values), json.dumps({'v': 1, 'fields': fields}, ensure_ascii=False, separators=(',', ':'))
    notes = [{
        'guid': place['guid'][language],
        'fields': {
            fields['answer']: place['name'][language],
            fields['picture']: f'<img src="{html.escape(place["picture"], quote=True)}" alt="{html.escape(translation["pictureAlt"], quote=True)}">',
            fields['place']: place['field'],
            fields['boundary']: translation['boundaryNotes'].get(place['code'], ''),
            fields['continent']: search_fields(place)[0],
            fields['search']: search_fields(place)[1],
        },
        'tags': translation['tags'] + (['place::regional', 'place::parent::' + place['parentCode']] if place.get('parentCode') else []),
    } for place in places]
    return meta, notes, model, deck
