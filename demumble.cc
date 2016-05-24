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

enum PrintMode { kPrintAll, kPrintMatching };
static bool print_demangled(const char* s, PrintMode print_mode) {
  const char* cxa_in = s;
  if (starts_with(s, "__Z") || starts_with(s, "____Z"))
    cxa_in += 1;
  if (char* itanium = __cxa_demangle(cxa_in, NULL, NULL, NULL)) {
    printf("%s", itanium);
    free(itanium);
    return true;
  } else if (char* ms = __unDName(NULL, s, 0, &malloc, &free, 0)) {
    printf("%s", ms);
    free(ms);
    return true;
  } else if (print_mode == kPrintAll) {
    printf("%s", s);
    return true;
  }
  return false;
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
  PrintMode print_mode = kPrintAll;
  if (argc > 1 && strcmp(argv[1], "-m") == 0) {
    print_mode = kPrintMatching;
    --argc;
    ++argv;
  }
  for (int i = 1; i < argc; ++i) {
    if (print_demangled(argv[i], print_mode))
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
      bool need_separator = false;
      char* cur = buf;
      char* end = cur + strlen(cur);

      while (cur != end) {
        size_t special = strcspn(cur, "_?");
        if (print_mode == kPrintAll)
          printf("%.*s", static_cast<int>(special), cur);
        else if (need_separator)
          printf("\n");
        need_separator = false;
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
        need_separator = print_demangled(cur, print_mode);
        cur[n_sym] = tmp;

        cur += n_sym;
      }
    }
  }
}
