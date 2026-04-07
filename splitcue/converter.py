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
import sys

from subprocess import Popen, PIPE

from mutagen import flac, MutagenError

from . import version
from .checker import cue_to_seconds


class Track:
    def __init__(self, i: int, mdata: dict,) -> None:
        self.total = len(mdata['tracks'])
        self.album = mdata.get('album')
        self.date = mdata.get('date')
        self.genre = mdata.get('genre')
        self.commentary = mdata.get('commentary')
        self.artist = mdata['tracks'][i].get('performer')
        self.title = mdata['tracks'][i].get('title')
        self.num = mdata['tracks'][i].get('num')
        self.index0 = mdata['tracks'][i].get('index0')
        self.index1 = mdata['tracks'][i].get('index1')
        self.first = True if not i else False
        self.last = True if i == len(mdata['tracks']) - 1 else False
        self.inext = None
        if not self.last:
            self.inext = (mdata['tracks'][i+1].get('index0'),
                          mdata['tracks'][i+1].get('index1'))
        else:
            self.tlength = mdata.get('length')
        self.length = 0.0
        self.enc = mdata['encoder']
        self.file = mdata['couple']

    @staticmethod
    def seconds_to_string(length):
        m, s = int(length) // 60, int(length) % 60
        n = int(round(length - int(length), 1) * 10)
        if n > 9:
            s += 1
            n = 0
            if s > 59:
                m += 1
                s = 0
        return '{:0{w}d}:{:0{w}d}.{}'.format(m, s, n, w=2)

    def convert(self, gaps, opts, ablock, tblock):
        points = self._set_points(gaps)
        self._set_length(points)
        print('{0}  {1}{2:>{4}}{3:>{5}}'.format(
            self.num, self.artist, self.title, self.length,
            ablock - len(self.artist) + len(self.title),
            tblock - len(self.title) + len(self.length)))
        cmd = '{0} {1} "{2}"'.format(
            self._set_shn_part(gaps),
            self._set_enc_part(opts),
            self.file)
        cmd = shlex.split(cmd)
        with Popen(cmd, stdin=PIPE) as p:
            p.communicate(input=points.encode('utf-8'))
        if p.returncode:
            print('ERROR: something bad happend')
            sys.exit(1)

    def write_meta(self):
        exts = {'flac': '.flac', 'lame': '.mp3',
                'opusenc': '.opus', 'oggenc': '.ogg'}
        methods = {'flac': self._set_vorbis_meta}
        fname = f'{self.num}{exts.get(self.enc)}'
        if os.path.exists(fname):
            try:
                methods[self.enc](fname)
            except (OSError, MutagenError):
                print(f'ERROR: {fname}: metadata cannot be written...')
            return fname
        return None

    def rename(self, fname):
        ext = os.path.splitext(fname)[1]
        artist = re.sub(r'[\\/|?<>*:]', '~', self.artist)
        title = re.sub(r'[\\/|?<>*:]', '~', self.title)
        new = f'{self.num} - {artist} - {title}{ext}'
        try:
            os.rename(fname, new)
        except OSError:
            print(f'ERROR: {fname} cannot be renamed...')

    def _set_vorbis_meta(self, fname):
        act = {'flac': flac.FLAC}
        song = act[self.enc](fname)
        song['artist'] = self.artist
        song['album'] = self.album
        song['genre'] = self.genre
        song['title'] = self.title
        song['tracknumber'] = self.num
        song['tracktotal'] = str(self.total)
        song['date'] = self.date
        song['comment'] = self.commentary or version
        song.save(fname)

    def _set_x(self, gaps):
        if gaps == 'split':
            if self.first and self.index1 == 0.0:
                return 1
        else:
            if self.first:
                return 1
        return 2

    def _set_shn_part(self, gaps):
        c = int(self.num.lstrip('0'))
        x = self._set_x(gaps)
        if x > 1:
            c -= 1
        return f'shnsplit -O always -q -c {c} -x {x} -a "" -z ""'

    def _set_enc_part(self, opts):
        fo = opts or '-8'
        encs = {'flac': f'-o "cust ext=flac flac {fo} - -o %f"'}
        return encs.get(self.enc)

    def _set_length(self, points):
        p = points.split('\n')
        if self.first:
            if len(p) == 1:
                l = cue_to_seconds(p[0])
            else:
                l = cue_to_seconds(p[1]) - cue_to_seconds(p[0])
        if self.last:
            l = self.tlength - cue_to_seconds(p[0])
        if not self.first and not self.last:
            l = cue_to_seconds(p[1]) - cue_to_seconds(p[0])
        self.length = self.seconds_to_string(l)

    def _set_points(self, gaps):
        if gaps == 'split':
            if self.first and self.index1 == '00:00.00':
                self.index1 = 0.0
            if self.last:
                return f'{self.index1}'
            return '{0}\n{1}'.format(
                self.index1 or '',
                self.inext[0] or self.inext[1]).lstrip()
        elif gaps == 'append':
            if self.first:
                return f'{self.inext[1]}'
            if self.last:
                return f'{self.index1}'
            return '{0}\n{1}'.format(
                self.index1,
                self.inext[1])
        elif gaps == 'prepend':
            if self.first:
                return self.inext[0] or self.inext[1]
            if self.last:
                return self.index0 or self.index1
            return '{}\n{}'.format(
                self.index0 or self.index1,
                self.inext[0] or self.inext[1])
