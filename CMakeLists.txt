cmake_minimum_required(VERSION 3.1.0 FATAL_ERROR)
project(demumble C CXX)
add_definitions(-D_LIBCXXABI_FUNC_VIS=)
add_executable(demumble
               demumble.cc
               third_party/wine/undname.c
               third_party/libcxxabi/cxa_demangle.cpp
)
set_target_properties(demumble PROPERTIES CXX_STANDARD 11
                                          CXX_STANDARD_REQUIRED ON)
