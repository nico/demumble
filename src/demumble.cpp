#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <algorithm>

#include "llvm/Demangle/Demangle.h"

#if defined(_MSC_VER)
    //  Microsoft
    #define EXPORT extern "C" __declspec(dllexport)
    #define IMPORT __declspec(dllimport)
#elif defined(__GNUC__)
    //  GCC
    #define EXPORT extern "C" __attribute__((visibility("default")))
    #define IMPORT
#else
    //  do nothing and hope for the best?
    #define EXPORT
    #define IMPORT
    #pragma warning Unknown dynamic link import/export semantics.
#endif

const char kDemumbleVersion[] = "1.2.17";

EXPORT bool demangle(const char* s, char* out) {
  if (char* itanium = llvm::itaniumDemangle(s, NULL, NULL, NULL)) {
    snprintf(out, 1024, "%s", itanium);
    free(itanium);
	return true;
  } else if (char* ms = llvm::microsoftDemangle(s, NULL, NULL, NULL)) {
	snprintf(out, 1024, "%s", ms);
    free(ms);
	return true;
  } else {
	snprintf(out, 1024, "%s", s);
  }
  return false;
}

EXPORT bool is_mangle_char_itanium(char c) {
  return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
         (c >= '0' && c <= '9') || c == '_' || c == '$';
}

EXPORT bool is_mangle_char_win(char c) {
  return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
         (c >= '0' && c <= '9') || strchr("?_@$", c);
}

EXPORT void get_version(char* out) {
	snprintf(out, 1024, "%s", kDemumbleVersion);
}

int main(int argc, char* argv[]) {
	return 1;
}
