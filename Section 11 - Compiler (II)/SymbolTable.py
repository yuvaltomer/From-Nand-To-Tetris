STATIC = "static"
FIELD = "field"
ARG = "argument"
VAR = "local"


class SymbolTable:
    '''Provides a symbol table abstraction'''

    def __init__(self):
        '''Creates a new empty symbol table'''
        self.table = {}
        self.fieldCounter = 0
        self.staticCounter = 0
        self.argumentCounter = 0
        self.localCounter = 0

    def reset(self):
        '''Starts a new subroutine scope'''
        self.table = {}
        self.fieldCounter = 0
        self.staticCounter = 0
        self.argumentCounter = 0
        self.localCounter = 0

    def define(self, name, type, kind):
        '''Defines a new identifier of a given name, type and kind, and assigns it a running index'''
        if kind == STATIC:
            self.table[f"{name}"] = [type, STATIC, self.staticCounter]
            self.staticCounter += 1
        elif kind == FIELD:
            self.table[f"{name}"] = [type, FIELD, self.fieldCounter]
            self.fieldCounter += 1
        elif kind == ARG:
            self.table[f"{name}"] = [type, ARG, self.argumentCounter]
            self.argumentCounter += 1
        elif kind == VAR:
            self.table[f"{name}"] = [type, VAR, self.localCounter]
            self.localCounter += 1

    def varCount(self, kind):
        '''Returns the number of variables of the given kind already defined in the current scope'''
        if kind == STATIC:
            return self.staticCounter
        elif kind == FIELD:
            return self.fieldCounter
        elif kind == ARG:
            return self.argumentCounter
        elif kind == VAR:
            return self.localCounter
        
    def kindOf(self, name):
        '''Returns the kind of the named identifier in the current scope'''
        value = self.table.get(name)
        if value:
            return value[1]
        return value
    
    def typeOf(self, name):
        '''Returns the type of the named identifier in the current scope'''
        value = self.table.get(name)
        if value:
            return value[0]
        return value
        
    def indexOf(self, name):
        '''Returns the index assigned to the named identifier'''
        value = self.table.get(name)
        if value:
            return value[2]
        return value