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

import sys
import importlib.util

from splitcue import version
from splitcue.main import parse_args
from splitcue.checker import check_couple, check_cue, print_report
from splitcue.converter import Track
from splitcue.parser import (
    define_dec, define_enc, extract_metadata,
    find_couple, find_couple_b, get_files, read_file)
from splitcue.system import check_dep, detect_f_type


print(version)
args = parse_args(version)
meta = dict()
meta['encoder'] = define_enc(args)
if not find_couple(args.cue_file, meta):
    print('ERROR: cue file is not found...')
    sys.exit(0)
for p in ('file', 'shntool', meta['encoder']):
    if not check_dep(p):
        print(f'ERROR: `{p}` is not installed...')
        sys.exit(0)
if detect_f_type(meta['cue']) != 'text/plain':
    print('ERROR: bad cue file...')
    sys.exit(0)
if importlib.util.find_spec('charset_normalizer') is None:
    print('ERROR: python3-charset-normalizer is not installed...')
    sys.exit(0)
if importlib.util.find_spec('mutagen') is None:
    print('ERROR: python3-mutagen is not installed...')
    sys.exit(0)
if read_file(meta['cue'], meta) is None:
    print('ERROR: bad cue file...')
    sys.exit(0)
files = get_files(meta)
if len(files) > 1:
    print('ERROR: bad cue, use convcue instead of splitcue...')
    sys.exit(0)
if meta.get('couple', None) is None:
    if not check_couple_b(files[0], meta):
        print('ERROR: there is no couple...')
        sis.exit(0)
define_dec(meta)
if meta['decoder'] != 'empty':
    if not check_dep(meta['decoder']):
        print(f'ERROR: `{dec}` is not installed...')
        sys.exit(0)
extract_metadata(meta)
ch = check_cue(meta)
del meta['content']
if ch[0] is None:
    print(f'ERROR: {ch[1]}')
    sys.exit(0)
cc = check_couple(meta)
if not cc[0]:
    print(f'ERROR: {cc[1]}')
    sys.exit(0)
print_report(meta, Track.seconds_to_string)
for i in range(len(meta['tracks'])):
    t = Track(i, meta)
    t.convert(args.gaps, args.enc_opts, meta.get('ablock'), meta.get('tblock'))
    fname = t.write_meta()
    if fname and args.rename:
        t.rename(fname)
