#!/usr/bin/env python3

"""
===================================
name: splitcue
description: a simple CDDA splitter
license: MIT
author: jazz4web
contacts: avm4dev@yandex.ru
===================================
"""

import importlib.util
import sys

from splitcue import version
from splitcue.checker import check_couple, check_cue, print_report
from splitcue.converter import Track
from splitcue.main import parse_args
from splitcue.mutagen import extract_cue_sheet
from splitcue.parser import (
    define_enc, define_sequence, extract_metadata, find_couple_b)
from splitcue.system import check_dep

args = parse_args(version, flac=True)
meta = dict()
meta['encoder'] = define_enc(args)
for p in ('flac', 'shntool', meta['encoder']):
    if not check_dep(p):
        print(f'ERROR: `{p}` is not installed...')
        sys.exit(1)
if importlib.util.find_spec('mutagen') is None:
    print('ERROR: python3-mutagen is not installed...')
    sys.exit(1)
find_couple_b(args.flac_file, meta)
ch = extract_cue_sheet(meta)
if ch[0] is None:
    print(f'ERROR: {ch[1]}')
    sys.exit(1)
extract_metadata(meta)
ch = check_cue(meta)
del meta['content']
if ch[0] is None:
    print(f'ERROR: {ch[1]}')
    sys.exit(1)
ch = check_couple(meta)
if not ch[0]:
    print(f'ERROR: {ch[1]}')
    sys.exit(1)
print_report(meta, Track.seconds_to_string)
for i in define_sequence(args, meta):
    t = Track(i, meta)
    if args.show:
        t.set_length(t._set_points(args.gaps))
        t.pprint(meta.get('ablock'), meta.get('tblock'))
    else:
        t.convert(
            args.gaps, args.enc_opts, meta.get('ablock'), meta.get('tblock'))
        if args.picture:
            fname = t.write_meta(picture=meta.get('cover'))
        else:
            fname = t.write_meta()
        if fname and args.rename:
            t.rename(fname)
