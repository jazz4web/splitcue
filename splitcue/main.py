"""
===================================
name: splitcue
description: a simple CDDA splitter
license: MIT
author: jazz4web
contacts: avm4dev@yandex.ru
===================================
"""

import argparse

DESC = '''SPLITCUE is a pack of tools to split CDDA images and convert them to
tracks. It contains three simple tools: splitcue, splitflac and convcue.
SPLICUE can split CDDA images if there is a separate cue sheet file.
SPLITFLAC can split CDDA FLAC images if the FLAC file contains cue
sheet in its metadata tag.
CONVCUE can convert separate FLAC tracks to one of available formats.'''

def parse_args(version, flac=False):
    name = 'splitcue'
    if flac:
        name = 'splitflac'
    args = argparse.ArgumentParser(
        prog=name,
        description=DESC,
        epilog='SPLITCUE was developed just for fun, it is free, use it...')
    args.add_argument(
        '-v', '--version', action='version', version=version)
    args.add_argument(
        '-g', '--gaps',
        action='store',
        dest='gaps',
        default='split',
        choices=('append', 'prepend', 'split'),
        help='control gaps, default is `split`')
    args.add_argument(
        '-m', '--mode',
        action='store',
        dest='media_type',
        default='opus',
        choices=('flac', 'opus', 'vorbis', 'mp3', 'aac'),
        help='the output media type, default is `opus`')
    args.add_argument(
        '-o', '--opts',
        action='store',
        dest='enc_opts',
        help='control some options while encoding tracks')
    args.add_argument(
        '-r', '--rename',
        action='store_true',
        dest='rename',
        default=False,
        help='rename tracks')
    args.add_argument(
        '-s', '--show',
        action='store_true',
        dest='show',
        default=False,
        help='just print a report, no splitting')
    if not flac:
        args.add_argument(
            'cue_file', action='store', help='the cuesheet file name')
    else:
        args.add_argument(
            'flac_file', action='store', help='the FLAC file name')
    return args.parse_args()


def parse_cargs(version):
    args = argparse.ArgumentParser(
        prog='convcue',
        description=DESC,
        epilog='SPLITCUE was developed just for fun, it is free, use it...')
    args.add_argument(
        '-v', '--version', action='version', version=version)
    args.add_argument(
        '-i',
        action='store',
        dest='input_dir',
        required=True,
        help='input directory')
    args.add_argument(
        '-d',
        action='store',
        dest='output_dir',
        required=True,
        help='output directory')
    args.add_argument(
        '-m', '--mode',
        action='store',
        dest='media_type',
        default='opus',
        choices=('opus', 'vorbis', 'mp3', 'aac'),
        help='the output media type, default is `opus`')
    args.add_argument(
        '-o', '--opts',
        action='store',
        dest='enc_opts',
        help='control some options while encoding tracks')
    args.add_argument(
        '-p',
        action='store_true',
        dest='picture',
        default=False,
        help='get the picture if there is one')
    return args.parse_args()
