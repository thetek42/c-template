# C Template

A template for C programs. Its features include:

- Sane defaults (especially compiler flags)
- A custom build system written in Python
- Simple custom testing framework
- Formatting using `clang-format`
- Common functions and typedefs included
- Simple logging library

## Usage

```sh
# debug build
build/build.py
build/build.py debug

# release build
build/build.py release

# run tests
build/build.py test

# format source files
build/build.py fmt

# clean build files
build/build.py clean
```

Source files are located in `src/`, header files are located in `inc/` and
anything used for testing goes in `test/`.
