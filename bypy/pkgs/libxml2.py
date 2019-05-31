#!/usr/bin/env python2
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2016, Kovid Goyal <kovid at kovidgoyal.net>


import os
import re

from bypy.constants import PREFIX, build_dir, iswindows
from bypy.utils import (install_binaries, install_tree, replace_in_file, run,
                        simple_build, walk)


def main(args):
    if iswindows:
        run(*('cscript.exe configure.js include={0}/include'
            ' lib={0}/lib prefix={0} zlib=yes iconv=no'.format(
                PREFIX.replace(os.sep, '/')).split()), cwd='win32')
        run('nmake /f Makefile.msvc', cwd='win32')
        install_tree('include/libxml', 'include/libxml2')
        for f in walk('.'):
            if f.endswith('.dll'):
                install_binaries(f, 'bin')
            elif f.endswith('.lib'):
                install_binaries(f)
    else:
        simple_build(
            '--disable-dependency-tracking --disable-static --enable-shared'
            ' --without-python --without-debug --with-iconv={0}'
            ' --with-zlib={0}'.format(PREFIX))
        for path in walk(build_dir()):
            if path.endswith('/xml2-config'):
                replace_in_file(
                    path, re.compile(b'(?m)^prefix=.+'),
                    f'prefix={PREFIX}')
