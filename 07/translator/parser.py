"""Parsers jack vm files."""
from enum import auto, Enum


class Parser(object):
    """Handles tha parsering of a single jack vm file."""

    ARITHMETIC_COMMANDS = [
        "add",
        "sub",
        "neg",
        "eq",
        "gt",
        "lt",
        "and",
        "or",
        "not"
    ]

    def __init__(self, filestream):
        """Create an instance of Parser."""
        # Filter out comments
        lines = list(filter(
            lambda x: not x.startswith("//"), filestream.readlines()
        ))

        # Remove new line character and emtpy strings
        commands = list(filter(
            None, [line.strip() for line in lines]
        ))

        # remove any inline comments
        self.commands = list(map(
            lambda x: x.split("//")[0].strip(), commands
        ))

        self.current_index = -1
        self.command = None

    def hasMoreCommands(self):
        """Check if there are any more commands."""
        if self.current_index < len(self.commands) - 1:
            return True
        else:
            return False

    def advance(self):
        """Read next command and sets it to the current command."""
        self.current_index += 1
        self.command = self.commands[self.current_index]

    def commandType(self):
        """Return the type of the VM command."""
        if self.command.startswith("push"):
            c_type = CommandType.C_PUSH
        elif self.command.startswith("pop"):
            c_type = CommandType.C_POP
        elif self.command in Parser.ARITHMETIC_COMMANDS:
            c_type = CommandType.C_ARITHMETIC
        elif self.command.startswith("label"):
            c_type = CommandType.C_LABEL
        elif self.command.startswith("goto"):
            c_type = CommandType.C_GOTO
        elif self.command.startswith("if-goto"):
            c_type = CommandType.C_IF
        elif self.command.startswith("function"):
            c_type = CommandType.C_FUNCTION
        elif self.command.startswith("call"):
            c_type = CommandType.C_CALL
        elif self.command.startswith("return"):
            c_type = CommandType.C_RETURN

        self.command_type = c_type
        return c_type

    def arg1(self):
        """Return first argument of current command."""
        if self.command_type == CommandType.C_RETURN:
            raise ValueError(
                (f"Cannot call method arg1 when current command type is"
                 f" {CommandType.C_RETURN}")
            )
        elif self.command_type == CommandType.C_ARITHMETIC:
            return self.command.strip()
        else:
            return self.command.split()[1]

    def arg2(self):
        """Return second argument of current command."""
        valid_command_types = [
            CommandType.C_PUSH,
            CommandType.C_POP,
            CommandType.C_FUNCTION,
            CommandType.C_CALL
        ]
        if self.command_type in valid_command_types:
            return self.command.split()[2]
        else:
            raise ValueError(
                (f"Cannot call method arg2 when current command type is"
                 f" {CommandType.C_RETURN}")
            )


class CommandType(Enum):
    """Enum for command types."""

    C_ARITHMETIC = auto()
    C_PUSH = auto()
    C_POP = auto()
    C_LABEL = auto()
    C_GOTO = auto()
    C_IF = auto()
    C_RETURN = auto()
    C_FUNCTION = auto()
    C_CALL = auto()
