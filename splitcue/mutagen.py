"""
===================================
name: splitcue
description: a simple CDDA splitter
license: MIT
author: jazz4web
contacts: avm4dev@yandex.ru
===================================
"""
import os.path

from mutagen import flac, MutagenError


def get_mdata(fname):
    try:
        song = flac.FLAC(fname)
    except (OSError, MutagenError):
        return None, '{0} is not FLAC or does not exist...'.format(
                os.path.basename(fname))
    return song, None


def extract_cue_sheet(res):
    try:
        image = flac.FLAC(res.get('couple'))
    except (OSError, TypeError, MutagenError):
        return None, 'flac file is not FLAC or does not exist...'
    if s := image.get('cuesheet'):
        s = [line.rstrip() for line in s[0].split('\n')]
        if s[0].startswith('\ufeff'):
            s[0] = s[0][1:]
        res['content'] = tuple(s)
        return True, None
    return None, 'flac file does not contain cue sheet tag...'
