cmake_minimum_required(VERSION 3.1.0 FATAL_ERROR)
project(demumble C CXX)
add_definitions(-D_LIBCXXABI_FUNC_VIS=)

# TODO: Also do this for gcc once gcc 4.9 is common.
if (UNIX AND CMAKE_GENERATOR STREQUAL "Ninja" AND
    CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  set(CMAKE_C_FLAGS "$CMAKE_C_FLAGS -fdiagnostics-color")
  set(CMAKE_CXX_FLAGS "$CMAKE_CXX_FLAGS -fdiagnostics-color")
endif()

add_executable(demumble
               demumble.cc
               third_party/wine/undname.c
               third_party/libcxxabi/cxa_demangle.cpp
)
set_target_properties(demumble PROPERTIES CXX_STANDARD 11
                                          CXX_STANDARD_REQUIRED ON)
