"""
===================================
name: splitcue
description: a simple CDDA splitter
license: MIT
author: jazz4web
contacts: avm4dev@yandex.ru
===================================
"""
import base64
import os
import re
import shlex
import sys

from subprocess import Popen, PIPE

from mutagen import flac, id3, mp3, mp4, oggopus, oggvorbis, MutagenError

from . import version
from .checker import cue_to_seconds


class AbsTrack:
    def _set_enc_part(self, opts):
        fo = opts or '-8'
        oo = opts or ''
        vo = opts or '-q 4'
        mo = opts or '-V 0'
        lame = f'-o "cust ext=mp3 lame {mo} --noreplaygain --lowpass -1 - %f"'
        faac = f'-o "cust ext=m4a faac {oo} -v 0 -X -P -w -o %f -"'
        encs = {'flac': f'-o "cust ext=flac flac {fo} - -o %f"',
                'lame': lame,
                'faac': faac,
                'oggenc': f'-o "cust ext=ogg oggenc {vo} - -o %f"',
                'opusenc': f'-o "cust ext=opus opusenc {oo} - %f"'}
        return encs.get(self.enc)

    def _set_mp3_meta(self, fname, picture=None):
        song = mp3.MP3(fname)
        song['TPE1'] = id3.TPE1(encoding=3, text=[self.artist])
        song['TALB'] = id3.TALB(encoding=3, text=[self.album])
        if self.genre:
            song['TCON'] = id3.TCON(encoding=3, text=[self.genre])
        song['TIT2'] = id3.TIT2(encoding=3, text=[self.title])
        number = '{0}/{1}'.format(int(self.num), self.total)
        song['TRCK'] = id3.TRCK(encoding=3, text=[number])
        if self.date:
            song['TDRC'] = id3.TDRC(encoding=3, text=[self.date])
        song['COMM::XXX'] = id3.COMM(
            encoding=3, lang='XXX', desc='', text=[self.commentary or version])
        if picture:
            song['APIC'] = id3.APIC(
                data=picture.data,
                type=id3.PictureType.COVER_FRONT,
                desc="cover",
                mime=picture.mime)
        song.save(fname)

    def _set_mp4_meta(self, fname, picture=None):
        song = mp4.MP4(fname)
        song['\xa9ART'] = [self.artist]
        song['\xa9alb'] = [self.album]
        if self.genre:
            song['\xa9gen'] = [self.genre]
        song['\xa9nam'] = [self.title]
        song['trkn'] = [(int(self.num), self.total)]
        if self.date:
            song['\xa9day'] = [self.date]
        song['\xa9cmt'] = [self.commentary or version]
        if picture:
            p = mp4.MP4Cover(picture.data)
            song['covr'] = [p]
        song.save(fname)

    def _set_vorbis_meta(self, fname, picture=None):
        act = {'flac': flac.FLAC,
               'opusenc': oggopus.OggOpus,
               'oggenc': oggvorbis.OggVorbis,}
        song = act[self.enc](fname)
        song['artist'] = self.artist
        song['album'] = self.album
        if self.genre:
            song['genre'] = self.genre
        song['title'] = self.title
        song['tracknumber'] = self.num.lstrip('0')
        song['tracktotal'] = str(self.total)
        if self.date:
            song['date'] = self.date
        song['comment'] = self.commentary or version
        if picture:
            if self.enc == 'opusenc' or self.enc == 'oggenc':
                p = base64.b64encode(picture.write()).decode('ascii')
                song['metadata_block_picture'] = p
            else:
                song.add_picture(picture)
        song.save(fname)



class FlacTrack(AbsTrack):
    def __init__(self, fname: str, enc: str, odir: str, tracks: int) -> None:
        self.file = fname
        self.odir = odir
        self.album = ''
        self.date = ''
        self.genre = ''
        self.commentary = version
        self.artist = ''
        self.title = ''
        self.num = ''
        self.total = tracks
        self.enc = enc
        self.rfile = ''

    def convert(self, opts):
        cmd = '{0} {1} "{2}"'.format(
            self._set_shn_part(),
            self._set_enc_part(opts),
            self.file)
        cmd = shlex.split(cmd)
        with Popen(cmd) as p:
            p.communicate()
        if p.returncode:
            print('ERROR: somethin bad happened...')
            sys.exit(1)

    def extract(self, song):
        if a := song.get('album'):
            self.album = a[0]
        if d := song.get('date'):
            self.date = d[0]
        if g := song.get('genre'):
            self.genre = g[0]
        if c := song.get('comment'):
            self.commentary = c[0]
        if ar := song.get('artist'):
            self.artist = ar[0]
        if t := song.get('title'):
            self.title = t[0]
        if n := song.get('tracknumber'):
            self.num = '{:0>2}'.format(n[0])
        if tt := song.get('tracktotal'):
            self.total = int(tt[0])

    def pprint(self, block):
        exts = {'lame': '.mp3', 'faac': '.m4a',
                'opusenc': '.opus', 'oggenc': '.ogg'}
        name, ext = os.path.splitext(os.path.basename(self.file))
        self.rfile = os.path.join(self.odir, f'{name}{exts.get(self.enc)}')
        file = os.path.basename(self.file)
        rfile = os.path.basename(self.rfile)
        b = 0
        if self.enc != 'opusenc':
            b = 1
        print('{0:<{2}}  ->  {1}'.format(
            file, rfile, block - len(file) + b + len(rfile)))

    def write_meta(self, picture=None):
        methods = {'lame': self._set_mp3_meta,
                   'faac': self._set_mp4_meta,
                   'oggenc': self._set_vorbis_meta,
                   'opusenc': self._set_vorbis_meta}
        if os.path.exists(self.rfile):
            try:
                methods[self.enc](self.rfile, picture=picture)
            except (OSError, MutagenError):
                print('ERROR: {0}: metadata cannot be written...'.format(
                    os.path.basename(self.rfile)))
        return None


    def _set_shn_part(self):
        return f'shnconv -O always -q -d "{self.odir}"'


class Track(AbsTrack):
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
        self.set_length(points)
        self.pprint(ablock, tblock)
        cmd = '{0} {1} "{2}"'.format(
            self._set_shn_part(gaps),
            self._set_enc_part(opts),
            self.file)
        cmd = shlex.split(cmd)
        with Popen(cmd, stdin=PIPE) as p:
            p.communicate(input=points.encode('utf-8'))
        if p.returncode:
            print('ERROR: something bad happened...')
            sys.exit(1)

    def pprint(self, ablock, tblock):
        print('{0}  {1}{2:>{4}}{3:>{5}}'.format(
            self.num, self.artist, self.title, self.length,
            ablock - len(self.artist) + len(self.title),
            tblock - len(self.title) + len(self.length)))

    def rename(self, fname):
        ext = os.path.splitext(fname)[1]
        artist = re.sub(r'[\\/|?<>*:]', '~', self.artist)
        title = re.sub(r'[\\/|?<>*:]', '~', self.title)
        new = f'{self.num} - {artist} - {title}{ext}'
        try:
            os.rename(fname, new)
        except OSError:
            print(f'ERROR: {fname} cannot be renamed...')

    def set_length(self, points):
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

    def write_meta(self, picture=None):
        exts = {'flac': '.flac', 'lame': '.mp3', 'faac': '.m4a',
                'opusenc': '.opus', 'oggenc': '.ogg'}
        methods = {'flac': self._set_vorbis_meta,
                   'lame': self._set_mp3_meta,
                   'faac': self._set_mp4_meta,
                   'oggenc': self._set_vorbis_meta,
                   'opusenc': self._set_vorbis_meta}
        fname = f'{self.num}{exts.get(self.enc)}'
        if os.path.exists(fname):
            try:
                methods[self.enc](fname, picture=picture)
            except (OSError, MutagenError):
                print(f'ERROR: {fname}: metadata cannot be written...')
            return fname
        return None

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
