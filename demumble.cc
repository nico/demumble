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
    int status;
    char* itanium_demangled = __cxa_demangle(argv[i], NULL, NULL, &status);
    if (status == 0)
      printf("%s\n", itanium_demangled);
    free(itanium_demangled);

    char* ms_demangled = __unDName(NULL, argv[i], 0, &malloc, &free, 0);
    if (ms_demangled)
      printf("%s\n", ms_demangled);
    free(ms_demangled);
  }
}
