"""Translate VM Commands into hack assembly."""

from parser import CommandType


class CodeWriter(object):
    """Translate VM Commands into hack assembly."""

    def __init__(self, filestream):
        """Create an instance of the code writer."""
        self.filestream = Filestream(filestream)

    def setFileName(self, filepath):
        """Close current filestream and open a new one to filepath."""
        if self.filestream is not None:
            self.filestream.close()
        self.filestream = Filestream(open(filepath, 'w'))

    def writeArithmetic(self, command):
        """Write  assembly code of arithmetic command."""
        if command == "add":
            self._add()
        elif command == "sub":
            self._sub()
        elif command == "eq":
            self._eq()
        elif command == "gt":
            self._gt()
        elif command == "lt":
            self._lt()
        elif command == "and":
            self._and()
        elif command == "or":
            self._or()
        elif command == "neg":
            self._neg()
        elif command == "not":
            self._not()

    def writePushPop(self, command_type, segment, index):
        """Write the asemble code for the push pop."""
        if command_type == CommandType.C_PUSH:
            # push the value from the segment onto the top of stack.
            if segment == "constant":
                # write constant to stack
                self._push_constant(index)

            # increment stack pointer.
            self._increment_SP()

    def _push_constant(self, index):
        """Push constant to top of stack."""
        self.filestream.write(f"@{index}")
        self.filestream.write("D=A")
        self.filestream.write("@SP")
        self.filestream.write("A=M")
        self.filestream.write("M=D")

    def _add(self):
        """Add the top two values of the stack."""
        # M=M+D

        self._pop_to_D()
        self._decrease_SP()
        self._set_A_to_top_of_stack()  # A = value @SP
        self.filestream.write("M=M+D")
        self._increment_SP()

    def _sub(self):
        """Subtract Second value from top value from the stack."""
        # M=M-D
        self._pop_to_D()
        self._decrease_SP()
        self._set_A_to_top_of_stack()  # A = value @SP
        self.filestream.write("M=M-D")
        self._increment_SP()

    def _eq(self):
        # D=M-D;JEQ

        self._pop_to_D()
        self._decrease_SP()
        self._set_A_to_top_of_stack()  # A = value @SP
        self.filestream.write("D=M-D")
        self._jump("JEQ")

    def _lt(self):
        """Compare that the second value in the stack is less than the top."""
        self._pop_to_D()
        self._decrease_SP()
        self._set_A_to_top_of_stack()  # A = value @SP
        self.filestream.write("D=M-D")
        self._jump("JLT")

    def _gt(self):
        """Compare that the second value in the stack is less than the top."""
        self._pop_to_D()
        self._decrease_SP()
        self._set_A_to_top_of_stack()  # A = value @SP
        self.filestream.write("D=M-D")
        self._jump("JGT")

    def _neg(self):
        """Negate the top value of the stack."""
        self._decrease_SP()
        self._set_A_to_top_of_stack()  # A = value @SP
        self.filestream.write("M=-M")
        self._increment_SP()

    def _and(self):
        """Bitwise and top two values of the stack."""
        # M=M&D
        self._pop_to_D()
        self._decrease_SP()
        self._set_A_to_top_of_stack()  # A = value @SP
        self.filestream.write("M=M&D")
        self._increment_SP()

    def _or(self):
        """Bitwise Or top two values of the stack."""
        # M=M|D
        self._pop_to_D()
        self._decrease_SP()
        self._set_A_to_top_of_stack()  # A = value @SP
        self.filestream.write("M=M|D")
        self._increment_SP()

    def _not(self):
        """Bitwise not the top value of the stack."""
        # M=!M
        self._decrease_SP()
        self._set_A_to_top_of_stack()  # A = value @SP
        self.filestream.write("M=!M")
        self._increment_SP()

    def _pop_to_D(self):
        """Pop the top of the stack to the D Register."""
        # Load the top most value of the stack to D
        self._decrease_SP()
        self.filestream.write("@SP")
        self.filestream.write("A=M")  # Load top of stack to A register
        self.filestream.write("D=M")

    def _set_A_to_top_of_stack(self):
        """Set the A register to the address stored at the value of SP."""
        self.filestream.write("@SP")
        self.filestream.write("A=M")

    def _increment_SP(self):
        """Increase address of SP by 1."""
        self.filestream.write("@SP")
        self.filestream.write("M=M+1")

    def _decrease_SP(self):
        """Decrease address of SP by."""
        self.filestream.write("@SP")
        self.filestream.write("M=M-1")

    def _jump(self, jump_type):
        """Set jump address and write jump command."""
        count = self.filestream.get_global_counter() + 10
        self.filestream.write(
            f"@{count}")  # JUMP pass the false commands
        # 7 false command plus the two commands setting up the jump

        self.filestream.write(f"D;{jump_type}")

        self._push_false()
        self._push_true()

    def _push_false(self):
        """Push false -1 to stack."""
        # seven total commands
        self.filestream.write("@SP")
        self.filestream.write("A=M")
        self.filestream.write("M=0")
        self._increment_SP()  # two commands in here

        # Jump pass the true block
        count = self.filestream.get_global_counter() + 8
        self.filestream.write(
            f"@{count}"
        )
        self.filestream.write("0;JMP")

    def _push_true(self):
        """Push false -1 to stack."""
        # five total commands
        self.filestream.write("@SP")
        self.filestream.write("A=M")
        self.filestream.write("M=-1")
        self._increment_SP()  # two commands here

    def close(self):
        """Close file."""
        # Loop at the end forever
        counter = self.filestream.get_global_counter() + 2
        self.filestream.write(f"@{counter}")
        self.filestream.write("0;JMP")
        self.filestream.close()


class Filestream(object):
    """Implements a custom write for a filesteam."""

    def __init__(self, filestream):
        """Create a filestream object."""
        self.filestream = filestream
        self.global_counter = -1

    def getFileStream(self):
        """Return filestream property."""
        return self.filestream

    def get_global_counter(self):
        """Return current global counter."""
        return self.global_counter

    def write(self, string):
        """Write line to file with a newline character."""
        self.filestream.write(f"{string}\n")
        self.global_counter += 1

    def close(self):
        """Close file."""
        if self.filestream is not None:
            self.filestream.close()
