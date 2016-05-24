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

static bool starts_with(const char* s, const char* prefix) {
  return strncmp(s, prefix, strlen(prefix)) == 0;
}

static void print_demangled(const char* s) {
  const char* cxa_in = s;
  if (starts_with(s, "__Z") || starts_with(s, "____Z"))
    cxa_in += 1;
  if (char* itanium = __cxa_demangle(cxa_in, NULL, NULL, NULL)) {
    printf("%s", itanium);
    free(itanium);
  } else if (char* ms = __unDName(NULL, s, 0, &malloc, &free, 0)) {
    printf("%s", ms);
    free(ms);
  } else {
    printf("%s", s);
  }
}

static bool is_mangle_char_posix(char c) {
  return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
         (c >= '0' && c <= '9') || c == '_';
}

static bool is_mangle_char_win(char c) {
  return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
         (c >= '0' && c <= '9') || strchr("?_@$", c);
}

static char buf[8192];
int main(int argc, char* argv[]) {
  for (int i = 1; i < argc; ++i) {
    print_demangled(argv[i]);
    printf("\n");
  }
  if (argc == 1) {  // Read stdin instead.
    char c;
    size_t num_read = 0;
    // By default, don't demangle types.  Mangled function names are unlikely
    // to appear in text for since they start with _Z (or ___Z) or ?? / ?$ / ?@.
    // But type manglings can be regular words ("Pi" is "int*").
    // (For command-line args, do try to demangle types though.)
    while (fgets(buf, sizeof(buf), stdin)) {
      char* cur = buf;
      char* end = cur + strlen(cur);

      while (cur != end) {
        size_t special = strcspn(cur, "_?");
        printf("%.*s", static_cast<int>(special), cur);
        cur += special;
        if (cur == end)
          break;

        size_t n_sym = 0;
        if (*cur == '?')
          while (cur + n_sym != end && is_mangle_char_win(cur[n_sym]))
            ++n_sym;
        else
          while (cur + n_sym != end && is_mangle_char_posix(cur[n_sym]))
            ++n_sym;

        char tmp = cur[n_sym];
        cur[n_sym] = '\0';
        print_demangled(cur);  // XXX don't print if not match
        cur[n_sym] = tmp;

        cur += n_sym;
      }
    }
  }
}
