#!/usr/bin/env python

# Builds demumble for Mac, Linux, Windows.  Must run on a Mac.
# Needs a chromium checkout that was synced with target_os=['win'] to get
# the Windows toolchain. You must run
# `build/linux/sysroot_scripts/install-sysroot.py --arch amd64` once to
# get the linux toolchain.

# Doesn't run tests, so make sure to run `./demumble_test.py` on all 3 platforms
# before running this script.

# https://gitlab.kitware.com/cmake/community/wikis/doc/cmake/CrossCompiling has
# some documentation on cross builds with cmake.

import contextlib
import json
import glob
import os
import subprocess
import sys

crsrc = '/Users/thakis/src/chrome/src'
if len(sys.argv) > 1:
  crsrc = os.path.abspath(sys.argv[1])
clangcl = crsrc + '/third_party/llvm-build/Release+Asserts/bin/clang-cl'
clangxx = crsrc + '/third_party/llvm-build/Release+Asserts/bin/clang++'
lldlink = crsrc + '/third_party/llvm-build/Release+Asserts/bin/lld-link'

cmake = '/Applications/CMake.app/Contents/bin/cmake'
call_cmake = [cmake, '-GNinja', '..', '-DCMAKE_BUILD_TYPE=Release']


@contextlib.contextmanager
def buildir(newdir):
    """Creates newdir if it doesn't exist yet and temporarily sets cwd to it."""
    newdir = os.path.join(os.path.dirname(__file__), newdir)
    if not os.path.isdir(newdir):
        os.mkdir(newdir)  # Intentionally not deleted.
    prevdir = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(prevdir)


# Linux.
linux_sysroot = crsrc + '/build/linux/debian_jessie_amd64-sysroot'
cflags = [ '--sysroot', linux_sysroot, '--target=x86_64-linux-gnu', ]
ldflags = ['-fuse-ld=lld'] + cflags
with buildir('buildlinux'):
    subprocess.check_call(call_cmake + [
        '-DCMAKE_CXX_COMPILER=' + clangxx,
        '-DCMAKE_CXX_FLAGS=' + ' '.join(cflags),
        '-DCMAKE_EXE_LINKER_FLAGS=' + ' '.join(ldflags),
        '-DCMAKE_SYSTEM_NAME=Linux',
        ])
    subprocess.check_call(['ninja', 'demumble'])

# Mac.
with buildir('buildmac'):
    subprocess.check_call(call_cmake + [ '-DCMAKE_CXX_COMPILER=' + clangxx ])
    subprocess.check_call(['ninja', 'demumble'])

# Win.
win_sysroot = glob.glob(
    crsrc + '/third_party/depot_tools/win_toolchain/vs_files/*')[0]
win_bindir = win_sysroot + '/win_sdk/bin'
# This json file looks like http://codepad.org/kmfgf0UL
winenv = json.load(open(win_bindir + '/SetEnv.x64.json'))['env']
for k in ['INCLUDE', 'LIB']:
  winenv[k] = [os.path.join(*([win_bindir] + e)) for e in winenv[k]]
win_include = ['-imsvc' + i for i in winenv['INCLUDE']]
win_lib = ['/libpath:' + i for i in winenv['LIB']]
cflags = ['--target=x86_64-pc-windows'] + win_include
with buildir('buildwin'):
    subprocess.check_call(call_cmake + [
        '-DCMAKE_CXX_COMPILER=' + clangcl,
        '-DCMAKE_CXX_FLAGS=' + ' '.join(cflags),
        # Without /manifest:no, cmake creates a default manifest file -- and
        # explicitly calls mt.exe (which we don't have in a cross build).
        # This also removes a dependency on rc.exe -- without this we'd also
        # have to set CMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY.
        '-DCMAKE_EXE_LINKER_FLAGS=' + ' '.join(['/manifest:no'] + win_lib),
        '-DCMAKE_LINKER=' + lldlink,
        '-DCMAKE_SYSTEM_NAME=Windows',
        ])
    subprocess.check_call(['ninja', 'demumble'])
