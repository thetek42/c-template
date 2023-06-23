#ifndef LOG_H_
#define LOG_H_

#include <stdlib.h>

/** macros ****************************************************************************************/

#define log_debug(...) __log_print (__Log_Level_Debug, __VA_ARGS__)
#define log_info(...)  __log_print (__Log_Level_Info, __VA_ARGS__)
#define log_ok(...)    __log_print (__Log_Level_Ok, __VA_ARGS__)
#define log_warn(...)  __log_print (__Log_Level_Warn, __VA_ARGS__)
#define log_err(...)   __log_print (__Log_Level_Err, __VA_ARGS__)

#define log_die(...)                                                                               \
  do {                                                                                             \
    __log_print (__Log_Level_Err, __VA_ARGS__);                                                    \
    exit (EXIT_FAILURE);                                                                           \
  } while (0)

/** enums *****************************************************************************************/

enum __Log_Level {
  __Log_Level_Debug,
  __Log_Level_Info,
  __Log_Level_Ok,
  __Log_Level_Warn,
  __Log_Level_Err,
};

/** functions *****************************************************************/

void __log_print (enum __Log_Level level, const char *const fmt, ...)
  __attribute__ ((format (printf, 2, 3)));

#endif // LOG_H_
