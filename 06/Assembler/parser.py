"""Parsers assembly language file."""

from enum import Enum, auto


class Parser(object):
    """Parser assembly language file."""

    def __init__(self, filestream):
        """Create a parser object."""
        # Filter out comments
        lines = list(filter(
            lambda x: not x.startswith("//"), filestream.readlines()
        ))

        # Remove new line character and emtpy strings
        self.commands = list(filter(
            None, [line.strip() for line in lines]
        ))
        self.current_command = None
        self.current_index = -1
        self.current_command_address = -1

    def reset(self):
        """Set current command position to the beginning."""
        self.current_index = -1

    def getNextCommandAddress(self):
        """Return the next command Address."""
        return self.current_command_address + 1

    def hasMoreCommands(self):
        """Check if there is more commands to parse."""
        if self.current_index < len(self.commands) - 1:
            return True
        else:
            return False

    def advance(self):
        """Read next command and makes it the current."""
        self.current_index += 1
        command = self.commands[self.current_index]

        # remove inline comments
        self.current_command = command.split("//")[0].strip()

    def commandType(self):
        """Return the type of the current command."""
        if self.current_command.startswith("@"):
            return CommandType.A_COMMAND
        elif self.current_command.startswith("("):
            return CommandType.L_COMMAND
        else:
            return CommandType.C_COMMAND

    def symbol(self):
        """Return Symbol or decimal of current command."""
        if self.current_command.startswith("@"):
            return self.current_command[1:]
        else:
            return self.current_command[1:-1]

    def dest(self):
        """Return Destination Mnemonic."""
        # The left side of the equal sign is the detination
        if "=" in self.current_command:
            return self.current_command.split("=")[0]
        else:
            return "null"

    def comp(self):
        """Return the Mnemonic comp."""
        if "=" in self.current_command and ";" in self.current_command:
            return self.current_command.split("=")[1].split(";")[0]
        elif "=" in self.current_command:
            return self.current_command.split("=")[1]
        else:
            return self.current_command.split(";")[0]

    def jump(self):
        """Return the Jump Mnemonic."""
        # The right side of ; contains the jump
        if ";" in self.current_command:
            return self.current_command.split(";")[1]
        else:
            return "null"

    def _contains(self, string, char):
        """Return the string 1 if command contains char."""
        if char in string:
            return "1"
        else:
            return "0"


class AutoName(Enum):
    """Override Auto Enum Name generation."""

    def _generate_next_value_(name, start, count, last_values):
        return name


class CommandType(AutoName):
    """Enum for Command Types."""

    A_COMMAND = auto()
    C_COMMAND = auto()
    L_COMMAND = auto()
