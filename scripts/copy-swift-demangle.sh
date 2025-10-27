#!/bin/bash

# Swift's demangler is much less hermetic than LLVM's. This copies all the
# code needed by Swift's demangler into this repository.

set -eu

# Adopt these three to match your local swift checkout and your local
# llvm checkout and build dir:

LLVM_SRC=$HOME/src/llvm-project/llvm
SWIFT_SRC=$HOME/src/swift
LLVM_HEADER_GEN_SRC=$HOME/src/llvm-project/out/gn/gen/llvm/include/llvm

# The rest only needs updating if the set of needed files changes:

cd "$(dirname "$0")"/..

LLVM_INC_SRC=$LLVM_SRC/include/llvm
LLVM_DST=third_party/llvm
LLVM_INC_DST=$LLVM_DST/include/llvm

SWIFT_INC_SRC=$SWIFT_SRC/include/swift
SWIFT_DST=third_party/swift
SWIFT_INC_DST=$SWIFT_DST/include/swift

rm -rf $LLVM_INC_DST/ADT
rm -rf $LLVM_INC_DST/Config
rm -rf $LLVM_INC_DST/Support
rm -rf $LLVM_DST/include/llvm-c
rm -rf $SWIFT_DST

mkdir -p $LLVM_INC_DST/ADT
cp "$LLVM_INC_SRC"/ADT/ADL.h $LLVM_INC_DST/ADT
cp "$LLVM_INC_SRC"/ADT/DenseMapInfo.h $LLVM_INC_DST/ADT
cp "$LLVM_INC_SRC"/ADT/Hashing.h $LLVM_INC_DST/ADT
cp "$LLVM_INC_SRC"/ADT/PointerIntPair.h $LLVM_INC_DST/ADT
cp "$LLVM_INC_SRC"/ADT/STLExtras.h $LLVM_INC_DST/ADT
cp "$LLVM_INC_SRC"/ADT/STLForwardCompat.h $LLVM_INC_DST/ADT
cp "$LLVM_INC_SRC"/ADT/STLFunctionalExtras.h $LLVM_INC_DST/ADT
cp "$LLVM_INC_SRC"/ADT/StringRef.h $LLVM_INC_DST/ADT
cp "$LLVM_INC_SRC"/ADT/StringSwitch.h $LLVM_INC_DST/ADT
cp "$LLVM_INC_SRC"/ADT/bit.h $LLVM_INC_DST/ADT
cp "$LLVM_INC_SRC"/ADT/iterator.h $LLVM_INC_DST/ADT
cp "$LLVM_INC_SRC"/ADT/iterator_range.h $LLVM_INC_DST/ADT

mkdir -p $LLVM_INC_DST/Config
cp "$LLVM_HEADER_GEN_SRC"/Config/abi-breaking.h $LLVM_INC_DST/Config
cp "$LLVM_HEADER_GEN_SRC"/Config/llvm-config.h $LLVM_INC_DST/Config

mkdir -p $LLVM_INC_DST/Support
cp "$LLVM_INC_SRC"/Support/Casting.h $LLVM_INC_DST/Support
cp "$LLVM_INC_SRC"/Support/Compiler.h $LLVM_INC_DST/Support
cp "$LLVM_INC_SRC"/Support/DataTypes.h $LLVM_INC_DST/Support
cp "$LLVM_INC_SRC"/Support/ErrorHandling.h $LLVM_INC_DST/Support
cp "$LLVM_INC_SRC"/Support/MathExtras.h $LLVM_INC_DST/Support
cp "$LLVM_INC_SRC"/Support/PointerLikeTypeTraits.h $LLVM_INC_DST/Support
cp "$LLVM_INC_SRC"/Support/SwapByteOrder.h $LLVM_INC_DST/Support
cp "$LLVM_INC_SRC"/Support/type_traits.h $LLVM_INC_DST/Support

mkdir -p $LLVM_DST/include/llvm-c
cp "$LLVM_SRC"/include/llvm-c/DataTypes.h $LLVM_DST/include/llvm-c

mkdir -p $SWIFT_DST
cp "$SWIFT_SRC"/LICENSE.txt $SWIFT_DST

mkdir -p $SWIFT_INC_DST
cp -R "$SWIFT_INC_SRC"/Demangling $SWIFT_INC_DST
cp "$SWIFT_INC_SRC"/Strings.h $SWIFT_INC_DST

mkdir -p $SWIFT_INC_DST/ABI
cp "$SWIFT_INC_SRC"/ABI/InvertibleProtocols.def $SWIFT_INC_DST/ABI

mkdir -p $SWIFT_INC_DST/AST
cp "$SWIFT_INC_SRC"/AST/Ownership.h $SWIFT_INC_DST/AST
cp "$SWIFT_INC_SRC"/AST/ReferenceStorage.def $SWIFT_INC_DST/AST

mkdir -p $SWIFT_INC_DST/Basic
cp "$SWIFT_INC_SRC"/Basic/Assertions.h $SWIFT_INC_DST/Basic
cp "$SWIFT_INC_SRC"/Basic/InlineBitfield.h $SWIFT_INC_DST/Basic
cp "$SWIFT_INC_SRC"/Basic/LLVM.h $SWIFT_INC_DST/Basic
cp "$SWIFT_INC_SRC"/Basic/MacroRoles.def $SWIFT_INC_DST/Basic
cp "$SWIFT_INC_SRC"/Basic/STLExtras.h $SWIFT_INC_DST/Basic

mkdir -p $SWIFT_DST/lib
cp -R "$SWIFT_SRC"/lib/Demangling $SWIFT_DST/lib
rm $SWIFT_DST/lib/Demangling/CMakeLists.txt
