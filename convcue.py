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
import glob
import os
import sys

from splitcue import version
from splitcue.converter import FlacTrack
from splitcue.main import parse_cargs
from splitcue.mutagen import get_cover, get_mdata
from splitcue.parser import define_enc
from splitcue.system import check_dep

args = parse_cargs(version)
if not os.path.exists(args.input_dir):
    print('ERROR: input dir does not exist...')
    sys.exit(1)
if not os.path.exists(args.output_dir):
    print('ERROR: output dir does not exist...')
    sys.exit(1)
enc = define_enc(args)
for p in ('shntool', 'flac', enc):
    if not check_dep(p):
        print(f'ERROR: `{p}` is not installed...')
        sys.exit(1)
if importlib.util.find_spec('mutagen') is None:
    print('ERROR: python3-mutagen is not installed...')
    sys.exit(1)
template = os.path.join(os.path.realpath(args.input_dir), '*.flac')
files = glob.glob(template)
if len(files) == 0:
    print('ERROR: input directory contains no FLAC files...')
    sys.exit(1)
elif len(files) > 99:
    print('ERROR: more than 99 tracks at one go...')
    sys.exit(1)
block = max(len(os.path.basename(file)) for file in files)
cover = None
if args.picture:
    cover = get_cover(os.path.realpath(args.input_dir))
for each in sorted(files):
    song, error = get_mdata(each)
    if error:
        print(error)
        continue
    t = FlacTrack(each, enc, os.path.realpath(args.output_dir), len(files))
    t.pprint(block)
    t.extract(song)
    t.convert(args.enc_opts)
    if args.picture:
        if song.pictures:
            cover = song.pictures[0]
        t.write_meta(picture=cover)
    else:
        t.write_meta()
