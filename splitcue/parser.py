"""
===================================
name: splitcue
description: a simple CDDA splitter
license: MIT
author: jazz4web
contacts: avm4dev@yandex.ru
===================================
"""

import os
import re

from charset_normalizer import from_path


def extract_metadata(res):
    res['album performer'] = get_value(res['content'], r'^PERFORMER +(.+)')
    res['album'] = get_value(res['content'], r'^TITLE +(.+)')
    res['genre'] = get_value(res['content'], r'^REM GENRE +(.+)')
    res['disc ID'] = get_value(res['content'], r'^REM DISCID +(.+)')
    res['date'] = get_value(res['content'], r'^REM DATE +(.+)')
    res['comment'] = get_value(res['content'], r'^REM COMMENT +(.+)')
    res['tracks'] = get_tracks(res)
    if res['tracks']:
        get_tracks_meta(res)


def get_tracks_meta(res):
    title = r'^ +TITLE +(.+)'
    perf = r'^ +PERFORMER +(.+)'
    index0 = r'^ +INDEX 00 +(\d{2}:\d{2}:\d{2})'
    index1 = r'^ +INDEX 01 +(\d{2}:\d{2}:\d{2})'
    content, tracks = res['content'], res['tracks']
    for i in range(len(tracks)):
        first = tracks[i].get('this')
        second = tracks[i].get('next')
        tracks[i]['title'] = get_value(content[first:second], title)
        tracks[i]['performer'] = get_value(content[first:second], perf)
        if tracks[i].get('performer') is None:
            tracks[i]['performer'] = res['album performer']
        tracks[i]['index0'] = get_value(
            content[first:second], index0, index=True)
        tracks[i]['index1'] = get_value(
            content[first:second], index1, index=True)
        if first:
            del tracks[i]['this']
        if second:
            del tracks[i]['next']


def get_tracks(res):
    l = list()
    i = 0
    pattern = re.compile(r'^ +TRACK +(\d+) +(.+)')
    for step, item in enumerate(res['content']):
        box = pattern.match(item)
        if box:
            track = dict()
            track['num'] = box.group(1)
            track['this'] = step
            if i:
                l[i - 1]['next'] = step
            l.append(track)
            i += 1
    return l


def get_value(content, expression, index=False):
    pattern = re.compile(expression)
    for line in content:
        box = pattern.match(line)
        if box:
            if index:
                return box.group(1)
            return box.group(1).strip('"')


def define_enc(args):
    encs = {'mp3': 'lame',
            'opus': 'opusenc',
            'vorbis': 'oggenc',
            'aac': 'faac',
            'flac': 'flac'}
    return encs[args.media_type]


def get_files(res):
    l = list()
    pattern = re.compile(r'^FILE +(.+) (.+)')
    for each in res['content']:
        box = pattern.match(each)
        if box:
            l.append(box.group(1).strip('"'))
    return tuple(l)


def read_file(name, res):
    if o := from_path(name).best():
        l = []
        for i, each in enumerate(o.raw.decode(o.encoding).split('\n')):
            s = each.rstrip()
            if not i and s.startswith('\ufeff'):
                s = s[1:]
            if s:
                l.append(s)
        res['content'] = tuple(l)
        return True


def find_couple_b(filename, res):
    if os.path.exists(filename):
        res['couple'] = os.path.realpath(filename)
        return True


def define_dec(res):
    decs = {'.ape': 'mac',
            '.wv': 'wvunpack',
            '.flac': 'flac'}
    name, ext = os.path.splitext(os.path.basename(res.get('couple')))
    res['decoder'] = decs.get(ext, 'empty')


def find_couple(filename, res):
    medias = ('.wav', '.flac', '.ape', '.wv')
    cues = ('.cue', '.cue~')
    res['couple'] = None
    if os.path.exists(filename):
        source = os.path.realpath(filename)
        hd = os.path.dirname(source)
        name, ext = os.path.splitext(os.path.basename(source))
        if ext in cues:
            res['cue'] = source
            for each in medias:
                m = os.path.join(hd, name + each)
                if os.path.exists(m):
                    res['couple'] = m
                    return True
            return True
