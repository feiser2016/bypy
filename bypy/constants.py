#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPLv3 Copyright: 2019, Kovid Goyal <kovid at kovidgoyal.net>

import os
import sys
import tempfile

_plat = sys.platform.lower()
iswindows = 'win32' in _plat or 'win64' in _plat
ismacos = 'darwin' in _plat
islinux = not iswindows and not ismacos
del _plat


def uniq(vals):
    ''' Remove all duplicates from vals, while preserving order.  '''
    vals = vals or ()
    seen = set()
    seen_add = seen.add
    return list(x for x in vals if x not in seen and not seen_add(x))


def base_dir():
    ans = getattr(base_dir, 'ans', None)
    if ans is None:
        ans = base_dir.ans = os.path.abspath('bypy')
    return ans


ROOT = os.environ.get('BYPY_ROOT', '/')
is64bit = sys.maxsize > (1 << 32)
SW = os.path.join(ROOT, 'sw')
PKG = os.path.join(SW, 'pkg')
if iswindows:
    is64bit = os.environ['BUILD_ARCH'] == '64'
    SW += '64' if is64bit else '32'
BYPY = os.path.join(ROOT, 'bypy')
SRC = os.path.join(ROOT, 'src')
OS_NAME = 'windows' if iswindows else ('macos' if ismacos else 'linux')
SOURCES = os.path.join(ROOT, 'sources')
PATCHES = os.path.join(BYPY, 'patches')
if iswindows:
    tempfile.tempdir = 'C:\\t\\t'
PREFIX = os.path.join(SW, 'sw')
BIN = os.path.join(PREFIX, 'bin')
PYTHON = os.path.join(
    PREFIX, 'private', 'python', 'python.exe') if iswindows else os.path.join(
            BIN, 'python')
cpu_count = os.cpu_count
MAKEOPTS = f'-j{cpu_count()}'
worker_env = {}
cygwin_paths = []
PKG_CONFIG_PATH = worker_env['PKG_CONFIG_PATH'] = os.path.join(
        PREFIX, 'lib', 'pkgconfig')
CMAKE = 'cmake'

if iswindows:
    CFLAGS = CPPFLAGS = LIBDIR = LDFLAGS = ''
    from vcvars import query_vcvarsall
    env = query_vcvarsall(is64bit)
    # Remove cygwin paths from environment
    paths = [p.replace('/', os.sep) for p in env['PATH'].split(os.pathsep)]
    cygwin_paths = [p for p in paths if 'cygwin64' in p.split(os.sep)]
    paths = [p for p in paths if 'cygwin64' not in p.split(os.sep)]
    # Add the bindir to the PATH, needed for loading DLLs
    paths.insert(0, os.path.join(PREFIX, 'bin'))
    paths.insert(0, os.path.join(PREFIX, 'qt', 'bin'))
    # Needed for pywintypes27.dll which is used by the win32api module
    paths.insert(0, os.path.join(
        PREFIX, r'private\python\Lib\site-packages\pywin32_system32'))
    os.environ['PATH'] = os.pathsep.join(uniq(paths))
    for k in env:
        if k != 'PATH':
            worker_env[k] = env[k]
else:
    CFLAGS = worker_env['CFLAGS'] = '-I' + os.path.join(PREFIX, 'include')
    CPPFLAGS = worker_env['CPPFLAGS'] = '-I' + os.path.join(PREFIX, 'include')
    LIBDIR = os.path.join(PREFIX, 'lib')
    if ismacos:
        LDFLAGS = worker_env['LDFLAGS'] = \
                f'-headerpad_max_install_names -L{LIBDIR}'
        CMAKE = os.path.join(BIN, 'cmake')
    else:
        LDFLAGS = worker_env['LDFLAGS'] = \
                f'-L{LIBDIR} -Wl,-rpath-link,{LIBDIR}'


def mkdtemp(prefix=''):
    tdir = getattr(mkdtemp, 'tdir', None)
    if tdir is None:
        if iswindows:
            tdir = tempfile.tempdir
        else:
            tdir = os.path.join(tempfile.gettempdir(), 't')
        from .utils import ensure_clear_dir
        ensure_clear_dir(tdir)
        mkdtemp.tdir = tdir
    return tempfile.mkdtemp(prefix=prefix, dir=tdir)


def build_dir(newval=None):
    if newval is not None:
        build_dir.ans = newval
    return getattr(build_dir, 'ans', None)


def python_major_minor_version():
    from .download_sources import read_deps, ok_dep
    read_deps()
    return ok_dep.major_version, ok_dep.minor_version
