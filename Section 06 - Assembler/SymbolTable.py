class SymbolTable:
    '''Keeps a correspondence between symbolic labels and numeric addresses.
       Contains a dictionary keyed by predefined symbols, labels and variables'''

    table = {}

    def __init__(self):
        '''Creates a new empty symbol table'''
        self.table = {}

    def addEntry(self, symbol, address):
        '''Adds the pair (symbol, address) to the table'''
        tableEntry = {f"{symbol}": address}
        self.table.update(tableEntry)

    def contains(self, symbol):
        '''Checks whether the symbol table contains the given symbol'''
        if symbol in self.table:
            return True
        return False

    def getAddress(self, symbol):
        '''Returns the address associated with the symbol'''
        return (int)(self.table[symbol])