#!/usr/bin/env python

# Builds demumble for Mac, Linux, Windows.  Must run on a Mac.
# Needs a chromium checkout at ~/src/chrome/src that was synced with
# target_os=['win'] to get the Windows toolchain. You must run
# `build/linux/sysroot_scripts/install-sysroot.py --arch amd64` once to
# get the linux toolchain.

# Also needs a GN build of llvm at ~/src/llvm-project/out/gn for llvm-strip
# for stripping the Linux binary.

# Doesn't run tests, so make sure to run `./demumble_test.py` on all 3 platforms
# before running this script.

# After this script finishes successfully, the cwd will contain
# demumble-mac.zip, demumble-linux.zip, demumble-windows.zip which each contain
# a demumble binary built for that OS, ready for releasing (assuming the script
# was run on the release branch).

# https://gitlab.kitware.com/cmake/community/wikis/doc/cmake/CrossCompiling has
# some documentation on cross builds with cmake.

import contextlib
import json
import glob
import os
import subprocess
import sys

crsrc = os.path.join(os.path.expanduser('~'), 'src/chrome/src')
if len(sys.argv) > 1:
  crsrc = os.path.abspath(sys.argv[1])
clangcl = crsrc + '/third_party/llvm-build/Release+Asserts/bin/clang-cl'
clangxx = crsrc + '/third_party/llvm-build/Release+Asserts/bin/clang++'
lldlink = crsrc + '/third_party/llvm-build/Release+Asserts/bin/lld-link'

# FIXME: https://chromium-review.googlesource.com/c/chromium/src/+/1214943
# has a way to build eu-strip on macOS, which is arguably a smaller dep
# than llvm-strip.
linux_strip = os.path.join(os.path.expanduser('~'),
                           'src/llvm-project/out/gn/bin/llvm-strip')

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

subprocess.check_call(['rm', '-rf', 'buildlinux', 'buildmac', 'buildwin'])
devnull = open(os.devnull,"w")

# Linux.
linux_sysroot = crsrc + '/build/linux/debian_jessie_amd64-sysroot'
cflags = [ '--sysroot', linux_sysroot, '--target=x86_64-linux-gnu', ]
ldflags = ['-fuse-ld=lld'] + cflags
with buildir('buildlinux'):
    print 'building linux'
    subprocess.check_call(call_cmake + [
        '-DCMAKE_CXX_COMPILER=' + clangxx,
        '-DCMAKE_CXX_FLAGS=' + ' '.join(cflags),
        '-DCMAKE_EXE_LINKER_FLAGS=' + ' '.join(ldflags),
        '-DCMAKE_SYSTEM_NAME=Linux',
        ], stdout=devnull)
    subprocess.check_call(['ninja', 'demumble'])
    subprocess.check_call([linux_strip, 'demumble'])
    subprocess.check_call(['zip', '-q9', 'demumble-linux.zip', 'demumble'])
    subprocess.check_call(['mv', 'demumble-linux.zip', '..'])

# Mac.
with buildir('buildmac'):
    print 'building mac'
    subprocess.check_call(call_cmake + [
        '-DCMAKE_CXX_COMPILER=' + clangxx,
        ], stdout=devnull)
    subprocess.check_call(['ninja', 'demumble'])
    subprocess.check_call(['strip', 'demumble'])
    subprocess.check_call(['zip', '-q9', 'demumble-mac.zip', 'demumble'])
    subprocess.check_call(['mv', 'demumble-mac.zip', '..'])

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
    print 'building windows'
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
        ], stdout=devnull)
    subprocess.check_call(['ninja', 'demumble'])
    # No stripping on Windows.
    subprocess.check_call(['zip', '-q9', 'demumble-win.zip', 'demumble.exe'])
    subprocess.check_call(['mv', 'demumble-win.zip', '..'])

# Copy over mac binary and run tests.
print 'running tests (on mac)'
subprocess.check_call(['cp', 'buildmac/demumble', '.'])
subprocess.check_call(['./demumble_test.py'])

# Show zip files.
subprocess.check_call('ls -hl *.zip', shell=True)
subprocess.check_call(['./demumble', '--version'])
