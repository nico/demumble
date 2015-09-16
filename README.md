# demumble

`demumble` demangles both POSIX and Visual Studio symbols. It runs on both
POSIX and Windows.

    $ ./demumble _Z4funcPci
    func(char*, int)
    $ ./demumble "?Fx_i@@YAHP6AHH@Z@Z"
    int __cdecl Fx_i(int (__cdecl*)(int))

## Build instructions

Use cmake to build: `cmake -G Ninja && ninja`

`cxa_demangle.cpp` needs more C++11 than Visual Studio 2013 supports, so
to build on Windows you need to use clang-cl as C++ compiler like so:

    cmake -G Ninja -DCMAKE_CXX_COMPILER=path/to/llvm-build/bin/clang-cl.exe
