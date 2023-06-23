#include "common.h"
#include "log.h"
#include <stdarg.h>
#include <stdlib.h>

/** functions *************************************************************************************/

/**
 * safe `malloc()` wrapper. instead of returning `nullptr` on error, this function will crash the
 * program. returns a pointer to the allocated memory.
 */
void *
__smalloc (const usize nmemb, /* number of elements to allocate */
           const usize size   /* size of each element */
#ifdef DEBUG_ALLOC
           ,
           char *file, /* __FILE__ */
           usize line  /* __LINE__ */
#endif
)
{
  void *ptr;

  ptr = malloc (nmemb * size);
  if (ptr == nullptr) {
#ifdef DEBUG_ALLOC
    log_die ("\x1b[90m(\x1b[35m%s\x1b[90m:\x1b[34m%zu\x1b[90m)\x1b[0m "
             "failed to allocate %zu bytes of memory.\n",
             file, line, nmemb * size);
#else
    log_die ("failed to allocate %zu bytes of memory.\n", nmemb * size);
#endif
  }

  return ptr;
}

/**
 * safe `calloc()` wrapper. instead of returning `nullptr` on error, this function will crash the
 * program. returns a pointer to the allocated memory.
 */
void *
__scalloc (const usize nmemb, /* number of elements to allocate */
           const usize size   /* size of each element */
#ifdef DEBUG_ALLOC
           ,
           char *file, /* __FILE__ */
           usize line  /* __LINE__ */
#endif
)
{
  void *ptr;

  ptr = calloc (nmemb, size);
  if (ptr == nullptr) {
#ifdef DEBUG_ALLOC
    log_die ("\x1b[90m(\x1b[35m%s\x1b[90m:\x1b[34m%zu\x1b[90m)\x1b[0m "
             "failed to allocate %zu bytes of memory.\n",
             file, line, nmemb * size);
#else
    log_die ("failed to allocate %zu bytes of memory.\n", nmemb * size);
#endif
  }

  return ptr;
}

/**
 * safe `realloc()` wrapper. instead of returning `nullptr` on error, this function will crash the
 * program. returns a pointer to the reallocated memory.
 */
void *
__srealloc (void *ptr,         /* the pointer to reallocate */
            const usize nmemb, /* number of elements to allocate */
            const usize size   /* size of each element */
#ifdef DEBUG_ALLOC
            ,
            char *file, /* __FILE__ */
            usize line  /* __LINE__ */
#endif
)
{
  ptr = realloc (ptr, nmemb * size);
  if (ptr == nullptr) {
#ifdef DEBUG_ALLOC
    log_die ("\x1b[90m(\x1b[35m%s\x1b[90m:\x1b[34m%zu\x1b[90m)\x1b[0m "
             "failed to allocate %zu bytes of memory.\n",
             file, line, nmemb * size);
#else
    log_die ("failed to allocate %zu bytes of memory.\n", nmemb * size);
#endif
  }

  return ptr;
}

/**
 * wrapper for `free()`. will not call `free()` on pointers that are `nullptr`. this is technically
 * not necessary according to the c standard, but you never know.
 */
void
sfree (void *ptr) /* the pointer to free */
{
  if (ptr != nullptr) {
    free (ptr);
  }
}
