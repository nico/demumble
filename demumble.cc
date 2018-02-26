#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <algorithm>

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

const char kDemumbleVersion[] = "1.0.0.git";

static void print_help(FILE* out) {
  fprintf(out,
"usage: demumble [options] [symbols...]\n"
"\n"
"if symbols are unspecified, reads from stdin.\n"
"\n"
"options:\n"
"  -m         only print mangled names that were demangled, omit other output\n"
"  -u         use unbuffered output\n"
"  --version  print demumble version (\"%s\")\n", kDemumbleVersion);
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

static bool is_plausible_itanium_prefix(char* s) {
  // Itanium symbols start with 1-4 underscores followed by Z.
  // strnstr() is BSD, so use a small local buffer and strstr().
  const int N = 5;  // == strlen("____Z")
  char prefix[N + 1];
  strncpy(prefix, s, N); prefix[N] = '\0';
  return strstr(prefix, "_Z");
}

static char buf[8192];
int main(int argc, char* argv[]) {
  enum { kPrintAll, kPrintMatching } print_mode = kPrintAll;
  while (argc > 1 && argv[1][0] == '-') {
    if (strcmp(argv[1], "-h") == 0 || strcmp(argv[1], "--help") == 0) {
      print_help(stdout);
      return 0;
    } else if (strcmp(argv[1], "-m") == 0) {
      print_mode = kPrintMatching;
    } else if (strcmp(argv[1], "-u") == 0) {
      setbuf(stdout, NULL);
    } else if (strcmp(argv[1], "--version") == 0) {
      printf("%s\n", kDemumbleVersion);
      return 0;
    } else if (strcmp(argv[1], "--") == 0) {
      --argc;
      ++argv;
      break;
    } else {
      fprintf(stderr, "demumble: unrecognized option `%s'\n", argv[1]);
      print_help(stderr);
      return 1;
    }
    --argc;
    ++argv;
  }
  for (int i = 1; i < argc; ++i) {
    print_demangled(argv[i]);
    printf("\n");
  }
  if (argc == 1) {  // Read stdin instead.
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
        else if (is_plausible_itanium_prefix(cur))
          while (cur + n_sym != end && is_mangle_char_posix(cur[n_sym]))
            ++n_sym;
        else {
          if (print_mode == kPrintAll)
            printf("_");
          ++cur;
          continue;
        }

        char tmp = cur[n_sym];
        cur[n_sym] = '\0';
        print_demangled(cur);
        need_separator = true;
        cur[n_sym] = tmp;

        cur += n_sym;
      }
    }
  }
}
