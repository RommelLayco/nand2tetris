#!/usr/bin/env python
"""Convert hack assembly into hack machine language."""
import os
import sys

from code import Code
from parser import CommandType, Parser
from symbol_table import SymbolTable


def main():
    """Entry point for the assembler."""
    assembly_file = sys.argv[1]

    f = open(assembly_file, 'r')
    p = Parser(f)
    f.close()

    symbol_table = SymbolTable()
    ROM_ADDRESS = -1
    while p.hasMoreCommands():
        p.advance()
        if p.commandType() == CommandType.L_COMMAND:
            symbol = p.symbol()
            if not symbol_table.contains(symbol):
                address = ROM_ADDRESS + 1
                symbol_table.addEntry(symbol, address)
        else:
            ROM_ADDRESS += 1

    # 2nd Pass
    code = Code()
    p.reset()

    # Write lines to a file
    file_name = os.path.splitext(assembly_file)[0] + ".hack"
    hack = open(file_name, "w")

    while p.hasMoreCommands():
        machine_code = ""
        p.advance()
        COMMAND_TYPE = p.commandType()
        if COMMAND_TYPE == CommandType.A_COMMAND:
            symbol = p.symbol()
            # Get Decimal Address
            try:
                decimal = int(symbol)
            except ValueError:
                if not symbol_table.contains(symbol):
                    address = symbol_table.getNextVariableAddress()
                    symbol_table.addEntry(symbol, address)
                    symbol_table.incrementNextVariableAddress()

                decimal = symbol_table.getAddress(symbol)
            machine_code = convertDecimalToBinary(decimal)

        elif p.commandType() == CommandType.C_COMMAND:
            machine_code = "111"
            command = p.comp()

            # Determine if we are reading from A or M
            if "M" in command:
                machine_code += "1"
            else:
                machine_code += "0"

            machine_code += code.comp(command)
            machine_code += code.dest(p.dest())
            machine_code += code.jump(p.jump())

        if machine_code != "":
            hack.write(machine_code + "\n")

    hack.close()


def convertDecimalToBinary(decimal):
    """Convert a decimal string to a 16 bit binary."""
    binary = bin(decimal)[2:]
    return binary.zfill(16)


if __name__ == "__main__":
    main()
