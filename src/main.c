#include "common.h"
#include "log.h"
#include <stdlib.h>

int
main (const int argc, const char *const argv[])
{
  (void) argc;
  (void) argv;

  log_debug ("Hello, World!\n");

  return EXIT_SUCCESS;
}
