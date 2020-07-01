#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <algorithm>

#include "llvm/Demangle/Demangle.h"

const char kDemumbleVersion[] = "1.2.2.git";

static int print_help(FILE* out) {
  fprintf(out,
"usage: demumble [options] [symbols...]\n"
"\n"
"if symbols are unspecified, reads from stdin.\n"
"\n"
"options:\n"
"  -b         print both demangled and mangled name\n"
"  -m         only print mangled names that were demangled, omit other output\n"
"  -u         use unbuffered output\n"
"  --version  print demumble version (\"%s\")\n", kDemumbleVersion);
  return out == stdout ? 0 : 1;
}

static void print_demangled(const char* format, const char* s, size_t* n_used) {
  if (char* itanium = llvm::itaniumDemangle(s, NULL, NULL, NULL)) {
    printf(format, itanium, s);
    free(itanium);
  } else if (char* ms = llvm::microsoftDemangle(s, n_used, NULL, NULL, NULL)) {
    printf(format, ms, s);
    free(ms);
  } else {
    printf("%s", s);
  }
}

static bool is_mangle_char_itanium(char c) {
  return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
         (c >= '0' && c <= '9') || c == '_' || c == '$';
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
  const char* print_format = "%s";
  while (argc > 1 && argv[1][0] == '-') {
    if (strcmp(argv[1], "--help") == 0) {
      return print_help(stdout);
    } else if (strcmp(argv[1], "--version") == 0) {
      printf("%s\n", kDemumbleVersion);
      return 0;
    } else if (strcmp(argv[1], "--") == 0) {
      --argc;
      ++argv;
      break;
    } else if (argv[1][0] == '-' && argv[1][1] != '-') {
      for (size_t i = 1; i < strlen(argv[1]); ++i)
        switch (argv[1][i]) {
        case 'b': print_format = "\"%s\" (%s)"; break;
        case 'h': return print_help(stdout);
        case 'm': print_mode = kPrintMatching; break;
        case 'u': setbuf(stdout, NULL); break;
        default:
          fprintf(stderr, "demumble: unrecognized option `%c' in `%s'\n",
                  argv[1][i], argv[1]);
          return print_help(stderr);
        }
    } else {
      fprintf(stderr, "demumble: unrecognized option `%s'\n", argv[1]);
      return print_help(stderr);
    }
    --argc;
    ++argv;
  }
  for (int i = 1; i < argc; ++i) {
    size_t used = strlen(argv[i]);
    print_demangled(print_format, argv[i], &used);
    printf("\n");
    if (used < strlen(argv[i]))
      printf("  unused suffix: %s\n", argv[i] + used);
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
          while (cur + n_sym != end && is_mangle_char_itanium(cur[n_sym]))
            ++n_sym;
        else {
          if (print_mode == kPrintAll)
            printf("_");
          ++cur;
          continue;
        }

        char tmp = cur[n_sym];
        cur[n_sym] = '\0';
        size_t n_used = n_sym;
        print_demangled(print_format, cur, &n_used);
        need_separator = true;
        cur[n_sym] = tmp;

        cur += n_used;
      }
    }
  }
}
