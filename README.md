`cxa_demangle.cpp` needs more C++11 than Visual Studio 2013 supports, so
to build on Windows you need to use clang-cl as C++ compiler like so:

    cmake -G Ninja -DCMAKE_CXX_COMPILER=path/to/llvm-build/bin/clang-cl.exe
