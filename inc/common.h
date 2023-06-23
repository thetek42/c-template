#ifndef COMMON_H_
#define COMMON_H_


#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <sys/types.h>


/** macros ********************************************************************/

/// define debug macros

#ifdef DEBUG
# define DEBUG_ALLOC
#endif

/// c11 / c23 compatibility. many of these can be removed once the project fully
/// migrates to c23, but for now, some of these will have to be used. when
/// migrating, remember that the usage of macros like `_Noreturn` should be
/// replaced by c23-specific syntax, in this case the `[[noreturn]]` attribute.

// if the program is compiled with c23 or newer, define `STDC23` as a feature
// test macro that is used for enabling features based on if c23 or c11 is used.

#if __STDC_VERSION__ >= 202000L
# define STDC23
#endif

// enable C11-specific features

#if !defined(STDC23)
# define nullptr NULL /* `nullptr` from C23 */
#endif

// enable C23-specific features

#if defined(STDC23)
# define _Noreturn [[noreturn]]
#endif


/// function wrappers

#ifdef DEBUG_ALLOC
# define smalloc(nmemb, size) __smalloc (nmemb, size, __FILE__, __LINE__)
# define scalloc(nmemb, size) __scalloc (nmemb, size, __FILE__, __LINE__)
# define srealloc(ptr, nmemb, size) __srealloc (ptr, nmemb, size, __FILE__, __LINE__)
#else
# define smalloc(nmemb, size) __smalloc (nmemb, size)
# define scalloc(nmemb, size) __scalloc (nmemb, size)
# define srealloc(ptr, nmemb, size) __srealloc (ptr, nmemb, size)
#endif


/** typedefs ******************************************************************/

/// common type abbreviations

typedef signed char schar;
typedef signed long long llong;
typedef unsigned char uchar;
typedef unsigned short ushort;
typedef unsigned int uint;
typedef unsigned long ulong;
typedef unsigned long long ullong;
typedef int8_t i8;
typedef int16_t i16;
typedef int32_t i32;
typedef int64_t i64;
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef ssize_t isize;
typedef size_t usize;
typedef float f32;
typedef double f64;
typedef long double f128;


/** functions *****************************************************************/

/// safe memory allocation

#ifdef DEBUG_ALLOC
void *__smalloc (const usize nmemb, const usize size, const char *const file, const usize line);
void *__scalloc (const usize nmemb, const usize size, const char *const file, const usize line);
void *__srealloc (void *ptr, const usize nmemb, const usize size, const char *const file, const usize line);
void sfree (void *ptr);
#else
void *__smalloc (const usize nmemb, const usize size);
void *__scalloc (const usize nmemb, const usize size);
void *__srealloc (void *ptr, const usize nmemb, const usize size);
void sfree (void *ptr);
#endif


#endif // COMMON_H_
