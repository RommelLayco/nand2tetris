"""Translate VM Commands into hack assembly."""

from parser import CommandType


class CodeWriter(object):
    """Translate VM Commands into hack assembly."""

    def __init__(self, filepath):
        """Create an instance of the code writer."""
        self.filestream = Filestream(open(filepath, 'w'))

    def writeInit(self):
        """Write bootstrap code."""
        self.filestream.write("@256")
        self.filestream.write("D=A")
        self.filestream.write("@SP")
        self.filestream.write("M=D")
        self.writeCall("Sys.init", 0)

    def setFileName(self, filename):
        """Close current filestream and open a new one to filepath."""
        self.filename = filename

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
            elif segment == "local":
                self._push_segment_index("LCL", index, "M")
            elif segment == "argument":
                self._push_segment_index("ARG", index, "M")
            elif segment == "this":
                self._push_segment_index("THIS", index, "M")
            elif segment == "that":
                self._push_segment_index("THAT", index, "M")
            elif segment == "pointer":
                self._push_segment_index("R3", index, "A")
            elif segment == "temp":
                self._push_segment_index("R5", index, "A")
            elif segment == "static":
                self._push_segment_index("16", index, "A")

        else:
            if segment == "local":
                self._pop_segment_index("LCL", index, "M")
            elif segment == "argument":
                self._pop_segment_index("ARG", index, "M")
            elif segment == "this":
                self._pop_segment_index("THIS", index, "M")
            elif segment == "that":
                self._pop_segment_index("THAT", index, "M")
            elif segment == "pointer":
                self._pop_segment_index("R3", index, "A")
            elif segment == "temp":
                self._pop_segment_index("R5", index, "A")
            elif segment == "static":
                self._pop_segment_index("16", index, "A")

    def writeLabel(self, label):
        """Write label."""
        self.filestream.write(f"({label})")
        self.filestream.global_counter -= 1

    def writeGoto(self, label):
        """Do an unconditional jump to the given label."""
        self.filestream.write(f"@{label}")
        self.filestream.write("0;JMP")

    def writeIf(self, label):
        """Write conditional jump."""
        self._pop_to_D()
        self.filestream.write(f"@{label}")
        self.filestream.write(f"D;JNE")

    def writeCall(self, functioname, number_of_args):
        """Save state of stack and set up args."""
        # Push return address to stack
        self._save_segement_address(f"{functioname}.return", "A")
        self._save_segement_address("LCL", "M")
        self._save_segement_address("ARG", "M")
        self._save_segement_address("THIS", "M")
        self._save_segement_address("THAT", "M")

        # Reposition ARG
        # Set ARG to SP - n -5
        self.filestream.write("@SP")
        self.filestream.write("D=M")
        self.filestream.write("@ARG")
        self.filestream.write("M=D")
        # less n arg positions
        self._set_D_to_index(number_of_args)
        self.filestream.write("@ARG")
        self.filestream.write("M=M-D")
        # less saved segments
        self._set_D_to_index(5)
        self.filestream.write("@ARG")
        self.filestream.write("M=M-D")

        # Set local to SP
        self.filestream.write("@SP")
        self.filestream.write("D=M")
        self.filestream.write("@LCL")
        self.filestream.write("M=D")

        # go to function
        self.filestream.write(f"@{functioname}")
        self.filestream.write("0;JMP")

        # Create label for return address
        self.filestream.write(f"({functioname}.return)")

    def writeFunction(self, label, number_of_locals):
        """Declare a label and initliaze locals to zero."""
        self.filestream.write(f"({label})")
        self.filestream.global_counter -= 1

        # Initialze locals to error

        # get index of local and add to base
        for index in range(0, number_of_locals):
            self._set_D_to_index(index)
            self.filestream.write("@LCL")
            self.filestream.write("D=M+D")
            self.filestream.write("A=D")
            self.filestream.write("M=0")

    def writeReturn(self):
        """Return the calling function."""
        # local is the address imediately after the saved state.
        self.filestream.write("@LCL")
        self.filestream.write("D=M")
        self.filestream.write("@FRAME")
        self.filestream.write("M=D")

        # Relocate the top of the stack to current arg
        self._pop_to_D()
        self.filestream.write("@ARG")
        self.filestream.write("A=M")
        self.filestream.write("M=D")

        # Set stack pointer to arg plus 1
        self.filestream.write("@ARG")
        self.filestream.write("D=M+1")
        self.filestream.write("@SP")
        self.filestream.write("M=D")

        # Repoistion segements
        self._reposition_segments("THAT")
        self._reposition_segments("THIS")
        self._reposition_segments("ARG")
        self._reposition_segments("LCL")

        # go to return address
        self._set_D_to_index(5)
        self.filestream.write("@FRAME")
        self.filestream.write("D=M-D")
        self.filestream.write("A=D")
        self.filestream.write("0;JMP")

    def _save_segement_address(self, segement, AM):
        """Save the current segementa address to the top of the stack."""
        self.filestream.write(f"@{segement}")
        self.filestream.write(f"D={AM}")
        self._push_D_to_stack()

    def _reposition_segments(self, segment):
        """Reposition a segement when returning from a function."""
        positions_from_frame = {
            "THAT": 1,
            "THIS": 2,
            "ARG": 3,
            "LCL": 4
        }

        position = positions_from_frame[segment]
        self._set_D_to_index(position)
        self.filestream.write("@FRAME")
        # Get Address of saved segement
        self.filestream.write("D=M-D")
        # store the saved segement value in D
        self.filestream.write("A=D")
        self.filestream.write("D=M")

        self.filestream.write(f"@{segment}")
        self.filestream.write("M=D")

    def _push_constant(self, index):
        """Push constant to top of stack."""
        self._set_D_to_index(index)
        self._push_D_to_stack()

    def _push_segment_index(self, segment, index, AM):
        """Push the value of the segment at index to top of the stack."""
        # Load the address of segement[index]
        self._set_D_to_index(index)
        self.filestream.write(f"@{segment}")
        self.filestream.write(f"A={AM}+D")

        # read value of segement[index]
        self.filestream.write("D=M")
        self._push_D_to_stack()

    def _pop_segment_index(self, segment, index, AM):
        """Pop the top of the stack to segment[index].

        AM = whether to add A or M to the index
        """
        # Load the address of segement[index]
        self._set_D_to_index(index)
        self.filestream.write(f"@{segment}")
        self.filestream.write(f"D={AM}+D")

        # Save address of segement[index]
        self.filestream.write("@R13")
        self.filestream.write("M=D")

        # Load top of the stack to segement[index]
        self._pop_to_D()
        self.filestream.write("@R13")
        self.filestream.write("A=M")
        self.filestream.write("M=D")

    def _set_D_to_index(self, index):
        """Set D register to value of the index."""
        self.filestream.write(f"@{index}")
        self.filestream.write("D=A")

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

    def _push_D_to_stack(self):
        """Push the value of the D register to top of the stack."""
        self.filestream.write("@SP")
        self.filestream.write("A=M")
        self.filestream.write("M=D")
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
