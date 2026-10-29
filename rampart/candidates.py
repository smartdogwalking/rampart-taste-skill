#!/usr/bin/env python3
"""Expose pinned research recipes as unselected, asset-aware candidates."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'skills/taste-skill/library'
PIN = '12af471f627f866411b4bd785b19646d3672784c'
HASHES = {
    'directions.json': 'd71e3824af33a92d9e1ca543e17f80baa5b7a30c815df5125cfe3300a14892c1',
    'motions.json': '51815dd09a823c829897f99ed9ea7dc5c35bd305ac989b8a0632ea6d42a3f08b',
    'app.json': '3678ccbe1e8d05feff6d4f07fa16a0d610aefeea5e697e842a876713ba763cf5',
}


def load(name):
    raw = (LIB / name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != HASHES[name]:
        raise ValueError('Library changed; review the source before updating the pin.')
    return json.loads(raw)


def page_candidates(directions, sector, have):
    accepted, excluded = [], []
    for item in directions:
        if sector not in item['sectors'] and '*' not in item['sectors']:
            continue
        missing = set(item.get('needs', [])) - set(have)
        if item.get('needsPictures') and 'photography' not in have:
            missing.add('photography')
        if missing:
            excluded.append({'id': item['id'], 'missingDeclaredAssets': sorted(missing)})
        else:
            accepted.append(item)
    return accepted, excluded


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode', choices=['page', 'app'], required=True)
    ap.add_argument('--sector', help='Page sector, or app kind, from the pinned source library', required=True)
    ap.add_argument('--have', default='', help='Comma-separated declared asset roles; declarations are not quality or rights checks')
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    directions, motions, app = load('directions.json'), load('motions.json'), load('app.json')
    have = {x.strip() for x in args.have.split(',') if x.strip()}
    if args.mode == 'page':
        sectors = {s for item in directions for s in item['sectors']}
        if args.sector not in sectors:
            ap.error('Unknown page sector')
        choices, excluded = page_candidates(directions, args.sector, have)
        by_motion = {item['id']: item for item in motions}
        choices = [{'recipe': item, 'motionRecipe': by_motion.get(item.get('motion'))} for item in choices]
    else:
        if args.sector not in app['kinds']:
            ap.error('Unknown app kind')
        choices = [{'recipe': item} for item in app['styles'] if args.sector in item.get('suits', [])]
        excluded = []
    report = {
        'sourceCommit': PIN, 'mode': args.mode, 'sector': args.sector,
        'declaredAssets': sorted(have), 'selectionStatus': 'unselected',
        'humanPreferencesApplied': False, 'qualityVerdict': 'not-assessed',
        'candidates': choices, 'excluded': excluded,
        'sceneCatalogPresent': (LIB / 'scenes.json').is_file(),
        'limits': 'Source proposals, not inspected benchmarks or approved identity. Asset availability is declared only. Rank against the real task, existing system and scoped taste. No random fallback, global history write, browser action, asset download or model training.',
    }
    if args.output.resolve().is_relative_to(ROOT):
        ap.error('Write private project proposals outside the public source checkout.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'report': str(args.output.resolve()), 'candidates': len(choices),
                      'excluded': len(excluded), 'selectionStatus': 'unselected',
                      'sceneCatalogPresent': report['sceneCatalogPresent']}))


if __name__ == '__main__':
    main()
