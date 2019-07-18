#!/usr/bin/env python
"""Translates VM files to hack assembly."""

import glob
import os
import sys

from parser import CommandType, Parser
from code_writer import CodeWriter


def main(path):
    """Entry point for the vm translator."""
    vm_files_paths = get_vm_files(path)

    # Create single code write module
    code_writer = CodeWriter(None)

    for vm_file_path in vm_files_paths:
        filestream = open(vm_file_path, "r")
        parser = Parser(filestream)
        filestream.close()

        # write to assembly file
        code_writer.setFileName(os.path.splitext(vm_file_path)[0] + ".asm")

        while parser.hasMoreCommands():
            parser.advance()
            command_type = parser.commandType()

            if command_type == CommandType.C_PUSH:
                segment = parser.arg1()
                index = parser.arg2()
                code_writer.writePushPop(
                    command_type,
                    segment,
                    int(index)
                )
            elif command_type == CommandType.C_ARITHMETIC:
                command = parser.arg1()
                code_writer.writeArithmetic(command)

        code_writer.close()

        print(code_writer.filestream.get_global_counter())


def get_vm_files(path):
    """Return a list of vm files."""
    filename, extension = os.path.splitext(path)

    if extension == ".vm":
        return [path]
    else:
        if os.path.isdir(path):
            return glob.glob(path + "*.vm")

    # Not a valid path fail
    print(f"{path} is not a .vm file or a directory")
    exit(1)


if __name__ == "__main__":
    path = sys.argv[1]
    main(path)
