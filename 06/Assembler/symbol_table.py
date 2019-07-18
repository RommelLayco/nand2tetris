"""The Symbol Table for the hack assembler."""


class SymbolTable(object):
    """The symbopl table for the hack assembler."""

    def __init__(self):
        """Create a symbol table."""
        self.table = {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "SCREEN": 16384,
            "KBD": 24576
        }

        for i in range(0, 16):
            self.table["R" + str(i)] = i

        self._next_variable_address = 16

    def addEntry(self, symbol, address):
        """Add a symbol address pair to the table."""
        self.table[symbol] = address

    def contains(self, symbol):
        """Check if the symbol is present in the table."""
        if symbol in self.table:
            return True
        else:
            return False

    def getAddress(self, symbol):
        """Get the address of the symbol."""
        return self.table[symbol]

    def getNextVariableAddress(self):
        """Return next variable address."""
        return self._next_variable_address

    def incrementNextVariableAddress(self):
        """Increment Next Variable Address."""
        self._next_variable_address += 1
