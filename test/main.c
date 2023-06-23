#include "common.h"
#include "test.h"
#include <stdio.h>
#include <stdlib.h>

/** declarations **************************************************************/

static Test_Result test_add (void);
static u64 add (u64 a, u64 b);

/** functions *****************************************************************/

int
main (const int argc, const char *const argv[])
{
  (void) argc;
  (void) argv;

  t_start_tests ();
  t_run (test_add);
  t_end_tests ();

  t_exit ();
}

/** static functions **********************************************************/

static Test_Result
test_add (void)
{
  t_start ();
  t_assert (add (42, 69) == 111, "add_1");
  t_assert (add (43, 69) == 112, "add_2");
  t_assert (add (44, 69) == 113, "add_3");
  t_end ();
}

static u64
add (u64 a, u64 b)
{
  return a + b;
}
