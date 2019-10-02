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

    if not os.path.exists(path):
        print("invalid file path")
        sys.exit(1)

    if os.path.isdir(path):
        dirname = os.path.dirname(path)
        name = os.path.basename(dirname)
        path = f"{dirname}/{name}"
        isdir = True
    else:
        path = os.path.splitext(path)[0]
        isdir = False

    # Create single code write module
    code_writer = CodeWriter(f"{path}.asm")

    if isdir:
        code_writer.writeInit()

    for vm_file_path in vm_files_paths:
        filestream = open(vm_file_path, "r")
        parser = Parser(filestream)
        filestream.close()

        # write to assembly file
        code_writer.setFileName(os.path.basename(vm_file_path))

        while parser.hasMoreCommands():
            parser.advance()
            command_type = parser.commandType()

            if (command_type == CommandType.C_PUSH or
                    command_type == CommandType.C_POP):
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
            elif command_type == CommandType.C_LABEL:
                label = parser.arg1()
                code_writer.writeLabel(label)
            elif command_type == CommandType.C_GOTO:
                label = parser.arg1()
                code_writer.writeGoto(label)
            elif command_type == CommandType.C_IF:
                label = parser.arg1()
                code_writer.writeIf(label)
            elif command_type == CommandType.C_FUNCTION:
                label = parser.arg1()
                number_of_locals = int(parser.arg2())
                code_writer.writeFunction(label, number_of_locals)
            elif command_type == CommandType.C_RETURN:
                code_writer.writeReturn()
            elif command_type == CommandType.C_CALL:
                functioname = parser.arg1()
                number_of_args = int(parser.arg2())
                code_writer.writeCall(functioname, number_of_args)

        print(code_writer.filestream.get_global_counter())
    code_writer.close()


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
