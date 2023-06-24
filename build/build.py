#!/usr/bin/env python3

import config
import dataclasses
import datetime
import enum
import os
import pathlib
import subprocess
import sys


@dataclasses.dataclass
class File:
    '''
    stores source file, the path to the generated object file and a list of
    header dependencies.
    '''
    src: str
    obj: str
    deps: list[str]


class Compilation_Mode(enum.Enum):
    '''
    used to specify if the program should be compiled in debug or release mode.
    '''
    Debug = 'debug'
    Release = 'release'
    Test = 'test'


class Color(enum.Enum):
    '''
    common colors used for colorizing terminal output.
    '''
    Reset = '\x1b[0m'
    Red = '\x1b[31m'
    Cyan = '\x1b[36m'


def get_source_files(compilation_mode: Compilation_Mode) -> list[str]:
    '''
    get a list of source files located in the `src/` folder. only matches files
    ending in `*.c`.
    '''
    path = pathlib.Path(config.SRC_DIR)
    files = [str(p) for p in path.rglob('*.c')]
    if compilation_mode == Compilation_Mode.Test:
        test_path = pathlib.Path(config.TEST_DIR)
        files.remove(f'{config.SRC_DIR}/{config.SRC_MAIN}')
        files.extend([str(p) for p in test_path.rglob('*.c')])
    return files


def get_object_location(src_file: str, compilation_mode: Compilation_Mode) -> str:
    '''
    get the location of the resulting object file. for example, a source file
    `src/foo/bar/baz.c` will have the object location `obj/debug/foo/bar/baz.c`
    if compiled in debug mode.
    '''
    # obtain the folder where the object will go. this is used to put object
    # files from debug builds in `obj/debug` and object files from release
    # builds in `obj/release`.
    if compilation_mode == Compilation_Mode.Test:
        subfolder = Compilation_Mode.Debug.value
    else:
        subfolder = compilation_mode.value
    result = src_file
    # replace `src/` and `test/` prefixes from source files with appropriate
    # `obj/...` prefixes for their respective object files
    src_path_parts = pathlib.Path(src_file).parts
    if src_path_parts[0] == config.SRC_DIR:
        result = src_file.replace(config.SRC_DIR, f'{config.OBJ_DIR}/{subfolder}', 1)
    elif src_path_parts[0] == config.TEST_DIR:
        result = src_file.replace(config.TEST_DIR, f'{config.OBJ_DIR}/test', 1)
    result += '.o'
    return result


def get_include_directories(src_file: str) -> list[str]:
    '''
    get a list the directories that header files are located in, to be used as
    compiler flags.
    '''
    if pathlib.Path(src_file).parts[0] == config.TEST_DIR:
        return [f'-I{config.INC_DIR}', f'-I{config.TEST_DIR}']
    else:
        return [f'-I{config.INC_DIR}']


def get_dependencies(src_file: str) -> list[str]:
    '''
    obtain a list of header dependencies for a source file by running `cc -M`.
    since `cc -M` uses make as its output format, it needs to be converted to a
    regular python list.
    '''
    includes = get_include_directories(src_file)
    # obtain raw make-compatible output from `cc -M` and remove linebreaks
    output_raw = subprocess.check_output([config.COMPILER, *includes, '-M', '-MM', src_file])
    output = output_raw.decode('utf-8').replace('\n', '').replace('\\', '')
    # remove make rule to get space-delimited list of dependencies
    deps = output.split(':')[1].split(' ')
    # filter for header files
    deps = list(filter(lambda x: x.endswith('.h'), deps))
    return deps


def get_file_list(compilation_mode: Compilation_Mode) -> list[File]:
    '''
    get a list of `File` objects that contain information about where source
    files are, where their object files will be located and which headers they
    depend on.
    '''
    src_files = get_source_files(compilation_mode)
    files: list[File] = []

    for src in src_files:
        obj = get_object_location(src, compilation_mode)
        deps = get_dependencies(src)
        files.append(File(src, obj, deps))

    return files


def log_message(color: Color, prefix: str, msg: str):
    '''
    print a message to the terminal using a specific color and prefix. the
    message will look like this:
        PRFX message
    where PRFX is the passed prefix. the prefix is colored according to the
    parameter passed to this function.
    '''
    print(f'{color.value}{prefix.ljust(4).upper()}{Color.Reset.value} {msg}')


def check_if_need_compile(file: File) -> bool:
    '''
    checks if an object file needs to be re-compiled based on the modification
    dates of its source file and header dependencies.
    '''
    # if the object file does not exist, it needs to be compiled
    obj_path = pathlib.Path(file.obj)
    if not obj_path.exists():
        return True
    
    # if the object file is older than the source file, it needs to be compiled
    src_path = pathlib.Path(file.src)
    src_mod_time = datetime.datetime.fromtimestamp(src_path.stat().st_mtime, tz=datetime.timezone.utc)
    obj_mod_time = datetime.datetime.fromtimestamp(obj_path.stat().st_mtime, tz=datetime.timezone.utc)
    if obj_mod_time < src_mod_time:
        return True

    # check all headers if they were modified since the object file was created
    for dep in file.deps:
        header_path = pathlib.Path(dep)
        header_mod_time = datetime.datetime.fromtimestamp(header_path.stat().st_mtime, tz=datetime.timezone.utc)
        if obj_mod_time < header_mod_time:
            return True

    # file does not need to be compiled
    return False


def compile_file(file: File, compilation_mode: Compilation_Mode) -> int:
    '''
    compile a source file to an object file.
    '''
    if not check_if_need_compile(file):
        return 0

    path = pathlib.Path(file.obj)
    includes = get_include_directories(file.src)

    obj_folder = str(path.parent)
    os.makedirs(obj_folder, exist_ok=True)

    if compilation_mode == Compilation_Mode.Release:
        mode_specific_flags = config.FLAGS_RELEASE
    else:
        mode_specific_flags = config.FLAGS_DEBUG

    log_message(Color.Cyan, 'cc', file.obj)

    return_code = subprocess.call([
        config.COMPILER,
        *config.FLAGS.split(' '),
        *config.FLAGS_WARN.split(' '),
        *mode_specific_flags.split(' '),
        *includes,
        '-c', file.src,
        '-o', file.obj,
    ])

    return return_code


def get_target_name(compilation_mode: Compilation_Mode) -> str:
    '''
    get the name of the target executable based on the compilation mode.
    '''
    return f'{config.BIN_DIR}/{config.TARGET}-{compilation_mode.value}'


def link_program(files: list[File], compilation_mode: Compilation_Mode) -> int:
    '''
    link the generated object files to an executable binary.
    '''
    os.makedirs(config.BIN_DIR, exist_ok=True)

    objs = [file.obj for file in files]

    if compilation_mode == Compilation_Mode.Release:
        mode_specific_flags = config.FLAGS_RELEASE
    else:
        mode_specific_flags = config.FLAGS_DEBUG

    target = get_target_name(compilation_mode)

    log_message(Color.Cyan, 'link', target)

    return_code = subprocess.call([
        config.COMPILER,
        *config.FLAGS.split(' '),
        *config.FLAGS_WARN.split(' '),
        *mode_specific_flags.split(' '),
        *config.LIBS,
        *objs,
        '-o', target,
    ])

    return return_code


def compile_executable(compilation_mode: Compilation_Mode):
    '''
    compile an executable. the parameter `compilation_mode` describes if it
    should be a debug or release build.
    '''
    # obtain source files
    files = get_file_list(compilation_mode)

    # compile object files
    for file in files:
        return_code = compile_file(file, compilation_mode)
        if return_code != 0:
            log_message(Color.Red, 'err', f'failed to compile {file.obj}')
            exit(return_code)

    # generate executable
    return_code = link_program(files, compilation_mode)
    if return_code != 0:
        log_message(Color.Red, 'err', f'failed to link program')
        exit(return_code)


def clean():
    '''
    remove build artifacts such as object files and binaries.
    '''
    subprocess.call(['rm', '-rf', config.BIN_DIR, config.OBJ_DIR])


def run_tests():
    '''
    compile a test executable and run the tests specified in the `test/`
    directory.
    '''
    compile_executable(Compilation_Mode.Test)
    return_code = subprocess.call([get_target_name(Compilation_Mode.Test)])
    exit(return_code)


def format_files():
    '''
    format all source files.
    '''
    files = []
    files.extend([str(p) for p in pathlib.Path(config.SRC_DIR).rglob('*.c')])
    files.extend([str(p) for p in pathlib.Path(config.INC_DIR).rglob('*.h')])
    files.extend([str(p) for p in pathlib.Path(config.TEST_DIR).rglob('*.c')])
    for file in files:
        subprocess.call(['clang-format', '-i', file])


def show_help():
    '''
    show the help message.
    '''
    print('usage: `build/build.py [subcommand]`.')
    print()
    print('valid subcommands:')
    print('  debug    compile a debug build')
    print('  release  compile a release build')
    print('  test     run tests')
    print('  fmt      format source files')
    print('  clean    clean build files')
    print()
    print('if no subcommand is provided, a debug build will be compiled.')


def main():
    # parse command line arguments
    if len(sys.argv) == 1:
        compile_executable(Compilation_Mode.Debug)
    elif sys.argv[1] == 'debug':
        compile_executable(Compilation_Mode.Debug)
    elif sys.argv[1] == 'release':
        compile_executable(Compilation_Mode.Release)
    elif sys.argv[1] == 'clean':
        clean()
    elif sys.argv[1] == 'test':
        run_tests()
    elif sys.argv[1] == 'fmt':
        format_files()
    elif sys.argv[1] in ('help', '-h', '--help'):
        show_help()
    else:
        log_message(Color.Red, 'err', f'unknown subcommand `{sys.argv[1]}`')
        exit(1)


if __name__ == '__main__':
    main()
