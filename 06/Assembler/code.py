"""Translate Hack assembly mnemonics into binary."""


class Code(object):
    """Translate Hack assembly mnemonics into binary."""

    def __init__(self):
        """Create a code object."""
        self.dest_dict = {
            "null": "000",
            "M": "001",
            "D": "010",
            "MD": "011",
            "A": "100",
            "AM": "101",
            "AD": "110",
            "AMD": "111"
        }

        self.jump_dict = {
            "null": "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111"
        }

        self.comp_dict = {
            "0": "101010",
            "1": "111111",
            "-1": "111010",
            "D": "001100",
            "A": "110000",
            "!D": "001101",
            "!A": "110001",
            "-D": "001111",
            "-A": "110011",
            "D+1": "011111",
            "A+1": "110111",
            "D-1": "001110",
            "A-1": "110010",
            "D+A": "000010",
            "D-A": "010011",
            "A-D": "000111",
            "D&A": "000000",
            "D|A": "010101"
        }

    def dest(self, mnemonic):
        """Return binary code of dest mnemonic."""
        return self.dest_dict[mnemonic]

    def comp(self, mnemonic):
        """Return the binary code of the comp mnemonic."""
        # A and M mnemonic are interchangable
        replaced = mnemonic.replace("M", "A")
        return self.comp_dict[replaced]

    def jump(self, mnemonic):
        """Return the binary code of the jump mnemonic."""
        return self.jump_dict[mnemonic]
