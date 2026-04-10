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


def parse_args(version):
    args = argparse.ArgumentParser()
    args.add_argument(
        '-v', '--version', action='version', version=version)
    args.add_argument(
        '-g',
        action='store',
        dest='gaps',
        default='split',
        choices=('append', 'prepend', 'split'),
        help='control gaps, default is `split`')
    args.add_argument(
        '-m',
        action='store',
        dest='media_type',
        default='opus',
        choices=('flac', 'opus', 'vorbis', 'mp3', 'aac'),
        help='the output media type, default is `opus`')
    args.add_argument(
        '-o',
        action='store',
        dest='enc_opts',
        help='control some options while encoding tracks')
    args.add_argument(
        '-r',
        action='store_true',
        dest='rename',
        default=False,
        help='rename tracks')
    args.add_argument(
        'cue_file', action='store', help='the cuesheet file name')
    return args.parse_args()
