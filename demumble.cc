#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

extern "C" {
char* __cxa_demangle(const char* mangled_name,
                     char* buf,
                     size_t* n,
                     int* status);

typedef void* (*malloc_func_t)(size_t);
typedef void (*free_func_t)(void*);
char* __unDName(char* buffer,
                const char* mangled,
                int buflen,
                malloc_func_t memget,
                free_func_t memfree,
                unsigned short int flags);
}

int main(int argc, char* argv[]) {
  for (int i = 1; i < argc; ++i) {
    if (char* itanium = __cxa_demangle(argv[i], NULL, NULL, NULL)) {
      printf("%s\n", itanium);
      free(itanium);
    } else if (char* ms = __unDName(NULL, argv[i], 0, &malloc, &free, 0)) {
      printf("%s\n", ms);
      free(ms);
    } else {
      printf("%s\n", argv[i]);
    }
  }
}
