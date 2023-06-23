COMPILER      = 'gcc'
FLAGS         = '-std=c11'
FLAGS_WARN    = '-Wall -Wextra -Wconversion -Wdouble-promotion -Wshadow -Wcast-qual -Wmissing-prototypes -Wmissing-noreturn -Wredundant-decls -Wdisabled-optimization -Wunsafe-loop-optimizations -Wcast-align=strict -Winline -Wvla -Wlogical-op -Wdate-time -Werror -pedantic'
FLAGS_DEBUG   = '-O0 -ggdb3 -fsanitize=address -fsanitize=undefined -fno-omit-frame-pointer -fstack-protector -DDEBUG'
FLAGS_RELEASE = '-O3 -march=native -DNDEBUG'
LIBS          = ''

SRC_DIR       = 'src'
OBJ_DIR       = 'obj'
BIN_DIR       = 'bin'
TEST_DIR      = 'test'

SRC_MAIN      = 'main.c'
TARGET        = 'c-template'
