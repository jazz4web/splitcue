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
import shlex

from subprocess import Popen, PIPE


def print_report(res, fun):
    res['tblock'] = max(len(track.get('title'))
                        for track in res['tracks']) + 2
    res['ablock'] = max(len(track.get('performer'))
                        for track in res['tracks']) + 2
    cue = res.get('cue')
    caps = ('genre:', 'year:', 'disc ID:', 'commentary:',
            'artist:', 'album:', 'cuesheet file:',
            'media file:', 'total length:', 'tracks:')
    vals = (res.get('genre'),
            res.get('date'),
            res.get('disc ID'),
            res.get('comment'),
            res.get('album performer'),
            res.get('album'),
            os.path.basename(cue) if cue else 'none',
            os.path.basename(res.get('couple')),
            fun(res.get('length')),
            str(len(res['tracks'])))
    for (caption, value) in zip(caps, vals):
        if value:
            print('{0}{1:>{2}}'.format(
                caption, value,
                max(map(len, caps)) + 2 - len(caption) + len(value)))


def check_index(timestamp):
    if timestamp:
        mm, ss, ff = re.split(r'[:.]', timestamp)
        if int(ss) > 59 or int(ff) > 74:
            return None
    return True


def format_index(s):
    mm, ss, ff = re.split(r'[:.]', s)
    return f'{mm}:{ss}.{ff}'


def cue_to_seconds(s):
    mm, ss, ff = re.split(r'[:.]', s)
    return int(mm) * 60 + int(ss) + int(ff) / 75


def check_couple(res):
    cmd = shlex.split('shnlen -ct "{}"'.format(res['couple']))
    with Popen(cmd, stdout=PIPE, stderr=PIPE) as p:
        r = p.communicate()
    if p.returncode:
        return None, 'sorry, something unexpected happened...'
    r = r[0].decode('utf-8').split()
    if r[3] != '---':
        return None, 'bad media file...'
    last = cue_to_seconds(res['tracks'][-1]['index1'])
    length = cue_to_seconds(r[0])
    res['length'] = length
    if length - last < 4:
        return None, 'media file is shorter than last point...'
    return True, None


def check_cue(res):
    summary = [bool(res.get('album')),
               bool(res.get('album performer')),
               bool(res.get('tracks'))]
    if not all(summary):
        return None, 'this cuesheet is not valid'
    for track in res.get('tracks', list()):
        num = track.get('num')
        if check_index(track['index0']) is None:
            return None, f'track {num} invalid timestamp'
        if check_index(track['index1']) is None:
            return None, f'track {num} invalid timestamp'
        if track.get('title') is None:
            return None, f'bad title for track {num}'
        if num != '01' and track['index1'] is None:
            return None, f'bad index for track {num}'
        if track['index0']:
            track['index0'] = format_index(track['index0'])
        if track['index1']:
            track['index1'] = format_index(track['index1'])
    slash = '/' if res.get('comment') and res.get('disc ID') else ''
    res['commentary'] = '{0}{1}{2}'.format(
        res.get('comment') or '', slash, res.get('disc ID') or '')
    return True, None
