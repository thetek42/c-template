#ifndef TEST_H_
#define TEST_H_


#include <stdlib.h>
#include "common.h"
#include "log.h"


/** structs *******************************************************************/

typedef struct {
    usize success;
    usize failure;
} Test_Result;


/** macros ********************************************************************/

#define t_start()                                                              \
  Test_Result __test_result = { .success = 0u, .failure = 0u }

#define t_assert(check, msg)                                                   \
  do {                                                                         \
    if (check) {                                                               \
      __test_result.success += 1;                                              \
    } else {                                                                   \
      log_err ("\x1b[90m(\x1b[35m" __FILE__ "\x1b[90m:\x1b[34m%d\x1b[90m)"     \
               "\x1b[0m assertion '" msg "' (" #check ") failed\n", __LINE__); \
      __test_result.failure += 1;                                              \
    }                                                                          \
  } while (0)

#define t_end()                                                                \
  return __test_result

#define t_run(func)                                                            \
  do {                                                                         \
    Test_Result res = func ();                                                 \
    __test_results.success += res.success;                                     \
    __test_results.failure += res.failure;                                     \
  } while (0)

#define t_start_tests()                                                        \
  Test_Result __test_results = { .success = 0u, .failure = 0u }

#define t_end_tests()                                                          \
  do {                                                                         \
    if (__test_results.failure == 0u) {                                        \
      log_ok ("successfully executed %zu tests.\n", __test_results.success);   \
    } else {                                                                   \
      log_err ("%zu out of %zu tests failed.\n", __test_results.failure,       \
              __test_results.success + __test_results.failure);                \
    }                                                                          \
  } while (0)

#define t_exit()                                                               \
  do {                                                                         \
    exit (__test_results.failure == 0u ? EXIT_SUCCESS : EXIT_FAILURE);         \
  } while (0)

#endif // TEST_H_
