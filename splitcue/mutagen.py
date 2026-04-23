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
import os.path

from mutagen import flac, id3, mp3, mp4, oggopus, oggvorbis, MutagenError

from . import version


def get_cover(directory, res=None):
    for each in ('cover.jpg', 'folder.jpg'):
        f = os.path.join(directory, each)
        if os.path.exists(f):
            with open(f, 'rb') as pic:
                picture = flac.Picture()
                picture.data = pic.read()
                picture.type = id3.PictureType.COVER_FRONT
                picture.desc = 'cover front'
                picture.mime = 'image/jpeg'
                if res:
                    res['cover'] = picture
                    return None
                else:
                    return picture


class AbsMutagen:
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
        if image.pictures:
            res['cover'] = image.pictures[0]
        return True, None
    return None, 'flac file does not contain cue sheet tag...'
