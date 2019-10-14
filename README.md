# demumble

`demumble` demangles both Itanium and Visual Studio symbols. It runs on both
POSIX and Windows.

    $ demumble _Z4funcPci
    func(char*, int)
    $ demumble '?Fx_i@@YAHP6AHH@Z@Z'
    int __cdecl Fx_i(int (__cdecl *)(int))

## Download

There are prebuilt x64 binaries for Linux, Mac (10.9+), and Windows on the
[releases page](https://github.com/nico/demumble/releases).

## But why

It has several nice features that c++filt lacks (and lacks many of c++filt's
features I never use).

Smart about underscores: C++ symbols have an additional leading underscore on
OS X. `operator new` is mangled as `_Znw` on Linux but `__Znw` on Mac. OS X's
c++filt automatically strips one leading underscore, but Linux's c++filt
doesn't. So if you want to demangle a Linux symbol on OS X, you need to pass
`-n` to tell it to not strip the underscore, and if you want to demangle an OS
X symbol on Linux you likewise need to pass `-_`. demumble just does the right
thing:

    $ c++filt _Znw
    _Znw
    $ c++filt __Znw
    operator new
    $ demumble _Znw
    operator new
    $ demumble __Znw
    operator new

Smart about filtering: Both c++filt and demumble can work as a stdin filter.
demumble only demangles function symbols (which never look like other words),
while c++filt on macOS defaults to demangling type names too, which are likely
to look like regular words. demumble does demangle types when they're passed
as args without requiring the `--types` switch that c++filt needs on Linux:

    # on macOS:
    $ echo 'I like Pi and _Znw' | c++filt
    I like int* and _Znw
    $ echo 'I like Pi and _Znw' | demumble
    I like Pi and operator new
    $ c++filt Pi
    int*
    $ demumble Pi
    int*
    # on Linux:
    $ c++filt Pi
    Pi

Cross-platform: demumble runs on Windows. demumble can demangle Windows-style
symbols (also when running on non-Windows).

    $ demumble '??2@YAPEAX_K@Z'
    void * __cdecl operator new(unsigned __int64)
    $ c++filt '??2@YAPEAX_K@Z'
    ??2@YAPEAX_K@Z

Optionally print _only_ demangled things: For example, print demangled names of
all functions defined in a bitcode file:

    $ grep '^define' bitcode-win.ll  | demumble -m | head -1
    unsigned int __cdecl v8::RoundUpToPowerOfTwo32(unsigned int)

Optionally print both mangled and demangled names:

    $ echo _ZN3fooC1Ev _ZN3fooC2Ev | ./demumble -b
    "foo::foo()" (_ZN3fooC1Ev) "foo::foo()" (_ZN3fooC2Ev)

## Python Usage

The python script is a simple wrapper around the C++ library. There are 4 APIs

    demangle(mangled_name): Demangle a msvc, itanium, or RTTI style name
    is_mangle_char_itanium(c): Is the given character within the valid range for itanium, and RTTI style names
    is_mangle_char_win(c): Is the given character within the valid range for windows, and RTTI style names
    version(): Get the library version

The script may also be invoked on the command line directly
```
$ python demumble.py ?Fx_i@@YAHP6AHH@Z@Z
Loaded demumble version: 1.2.2
int __cdecl Fx_i(int (__cdecl *)(int))
```

## Build instructions

This is a cmake project, the windows build requires Visual Studio. You may build with the two included scripts:
`build_unix.sh` and `build_win.bat`. To create the python `.whl` run the respective build scripts on windows and linux machines and copy the build `.so` and `.dll` to the same machine. On that machine run `python3 setup.py bdist_wheel`. Alternatively just run `python3 setup.py install` for a local installation.