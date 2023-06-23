#include "log.h"
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>


/** functions *****************************************************************/

/**
 * print a formatted message to stderr using printf formatting and a given log
 * level. this functions is not intended to be used directly. the `log_*` macros
 * should be used instead.
 */
__attribute__ ((format (printf, 2, 3)))
void
__log_print (enum __Log_Level level, /* log level */
             const char *const fmt,  /* format string */
             ...)                    /* format parameters */
{
  va_list ap;

  switch (level) {
    case __Log_Level_Debug: { fprintf (stderr, "\x1b[90m[\x1b[35mdebug\x1b[90m]\x1b[0m "); break; }
    case __Log_Level_Info:  { fprintf (stderr, "\x1b[90m[\x1b[34minfo\x1b[90m]\x1b[0m " ); break; }
    case __Log_Level_Ok:    { fprintf (stderr, "\x1b[90m[\x1b[32mok\x1b[90m]\x1b[0m "   ); break; }
    case __Log_Level_Warn:  { fprintf (stderr, "\x1b[90m[\x1b[33mwarn\x1b[90m]\x1b[0m " ); break; }
    case __Log_Level_Err:   { fprintf (stderr, "\x1b[90m[\x1b[31merr\x1b[90m]\x1b[0m "  ); break; }
  }

  va_start (ap, fmt);
  vfprintf (stderr, fmt, ap);
  va_end (ap);
}
