#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

void print_demangled(const char* s) {
  if (char* itanium = __cxa_demangle(s, NULL, NULL, NULL)) {
    printf("%s\n", itanium);
    free(itanium);
  } else if (char* ms = __unDName(NULL, s, 0, &malloc, &free, 0)) {
    printf("%s\n", ms);
    free(ms);
  } else {
    printf("%s\n", s);
  }
}

int main(int argc, char* argv[]) {
  for (int i = 1; i < argc; ++i)
    print_demangled(argv[i]);
  if (argc == 1) {  // Read stdin instead.
    char buf[1024];
    while (fgets(buf, sizeof(buf), stdin)) {
      char* nl = strrchr(buf, '\n');  // chomp trailing newline.
      if (nl && !nl[1])
        *nl = '\0';
      print_demangled(buf);
    }
  }
}
