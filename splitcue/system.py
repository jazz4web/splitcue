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
import shlex

from subprocess import Popen, PIPE


def check_dep(dependency):
    for path in os.getenv('PATH').split(':'):
        depbin = os.path.join(path, dependency)
        if os.path.exists(depbin):
            return True


def detect_f_type(name):
    cmd = shlex.split(f'file -b --mime-type "{name}"')
    with Popen(cmd, stdout=PIPE, stderr=PIPE) as p:
        result = p.communicate()
    if p.returncode:
        return None
    return result[0].decode('utf-8').strip()

