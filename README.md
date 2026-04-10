**splitcue** is a simple CDDA splitter.

The program is being written just for fun. I already have **cuetoolkit**, **ffcuesplit**, **cuesplit**.., actually I do not need anything else, but still...

Available input formats are: WAV, FLAC, WavPack, Monkey's Audio.

The proper usage you can see with this command:

```
$ splitcue -h
splitcue v0.1.1
usage: splitcue [-h] [-v] [-g {append,prepend,split}]
                [-m {flac,opus,vorbis,mp3,aac}] [-o ENC_OPTS] [-r]
                cue_file

positional arguments:
  cue_file              the cuesheet file name

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -g {append,prepend,split}
                        control gaps, default is `split`
  -m {flac,opus,vorbis,mp3,aac}
                        the output media type, default is `opus`
  -o ENC_OPTS           control some options while encoding tracks
  -r                    rename tracks
```

It works fine on ***Debian sid*** and, I think, on ***Debian stable*** too, it is ***trixie*** currently. About other versions of Linux I cannot say, I did not try.

This code is free... If you want to make it better, do it.
