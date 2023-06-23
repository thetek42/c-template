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


class CompilationMode(enum.Enum):
    '''
    used to specify if the program should be compiled in debug or release mode.
    '''
    Debug = 'debug'
    Release = 'release'


class Color(enum.Enum):
    '''
    common colors used for colorizing terminal output.
    '''
    Reset = '\x1b[0m'
    Red = '\x1b[31m'
    Green = '\x1b[32m'


def get_source_files() -> list[str]:
    '''
    get a list of source files located in the `src/` folder. only matches files
    ending in `*.c`.
    '''
    path = pathlib.Path('src/')
    files = [str(p) for p in path.rglob('*.c')]
    return files


def get_object_location(src_file: str, compilation_mode: CompilationMode) -> str:
    '''
    get the location of the resulting object file. for example, a source file
    `src/foo/bar/baz.c` will have the object location `obj/debug/foo/bar/baz.c`
    if compiled in debug mode.
    '''
    result = src_file.replace('src/', f'obj/{compilation_mode.value}/')
    result = result[:-2] + '.o'
    return result


def get_dependencies(src_file: str) -> list[str]:
    '''
    obtain a list of header dependencies for a source file by running `cc -M`.
    since `cc -M` uses make as its output format, it needs to be converted to a
    regular python list.
    '''
    # obtain raw make-compatible output from `cc -M` and remove linebreaks
    output_raw = subprocess.check_output([config.COMPILER, '-Iinc', '-M', '-MM', src_file])
    output = output_raw.decode('utf-8').replace('\n', '').replace('\\', '')
    # remove make rule to get space-delimited list of dependencies
    deps = output.split(':')[1].split(' ')
    # filter for header files
    deps = list(filter(lambda x: x.endswith('.h'), deps))
    return deps


def get_file_list(compilation_mode: CompilationMode) -> list[File]:
    '''
    get a list of `File` objects that contain information about where source
    files are, where their object files will be located and which headers they
    depend on.
    '''
    src_files = get_source_files()
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


def compile_file(file: File, compilation_mode: CompilationMode) -> int:
    '''
    compile a source file to an object file.
    '''
    if not check_if_need_compile(file):
        return 0

    path = pathlib.Path(file.obj)

    obj_folder = str(path.parent)
    os.makedirs(obj_folder, exist_ok=True)

    if compilation_mode == CompilationMode.Debug:
        mode_specific_flags = config.FLAGS_DEBUG
    elif compilation_mode == CompilationMode.Release:
        mode_specific_flags = config.FLAGS_RELEASE

    log_message(Color.Green, 'cc', file.obj)

    return_code = subprocess.call([
        config.COMPILER,
        *config.FLAGS.split(' '),
        *config.FLAGS_WARN.split(' '),
        *mode_specific_flags.split(' '),
        '-Iinc',
        '-c', file.src,
        '-o', file.obj,
    ])

    return return_code


def link_program(files: list[File], compilation_mode: CompilationMode) -> int:
    '''
    link the generated object files to an executable binary.
    '''
    os.makedirs('bin/', exist_ok=True)

    objs = [file.obj for file in files]

    if compilation_mode == CompilationMode.Debug:
        mode_specific_flags = config.FLAGS_DEBUG
    elif compilation_mode == CompilationMode.Release:
        mode_specific_flags = config.FLAGS_RELEASE

    target = f'bin/{config.TARGET}-{compilation_mode.value}'

    log_message(Color.Green, 'link', target)

    return_code = subprocess.call([
        config.COMPILER,
        *config.FLAGS.split(' '),
        *config.FLAGS_WARN.split(' '),
        *mode_specific_flags.split(' '),
        *config.LIBS,
        '-Iinc',
        *objs,
        '-o', target,
    ])

    return return_code


def main():
    # parse command line arguments
    if len(sys.argv) == 1:
        compilation_mode = CompilationMode.Debug
    elif sys.argv[1] == 'debug':
        compilation_mode = CompilationMode.Debug
    elif sys.argv[1] == 'release':
        compilation_mode = CompilationMode.Release
    elif sys.argv[1] == 'clean':
        subprocess.call(['rm', '-rf', 'bin/', 'obj/'])
        exit(0)
    else:
        log_message(Color.Red, 'err', f'unknown subcommand `{sys.argv[1]}`')
        exit(1)

    # obtain source files
    files = get_file_list(compilation_mode)

    # compile object files
    for file in files:
        success = compile_file(file, compilation_mode)
        if success != 0:
            log_message(Color.Red, 'err', f'failed to compile {file.obj}')
            exit(success)

    # generate executable
    success = link_program(files, compilation_mode)
    if success != 0:
        log_message(Color.Red, 'err', f'failed to link program')
        exit(success)


if __name__ == '__main__':
    main()