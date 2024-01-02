class Parser:
    '''Encapsulates access to the input code.
       Reads an assembly language command, parses it, and provides convenient
       access to command's components (fields and symbols).
       In addition, removes all white space and comments.'''

    file = ""               # .asm file to process
    currentCommand = ""     # current line of the file

    def __init__(self, fileName):
        '''Opens the input file'''
        self.file = open(fileName, "r")
        self.currentCommand = ""

    def hasMoreLines(self):
        '''Checks if there are more commands in the input'''
        currentPos = self.file.tell()
        hasNextLine = bool(self.file.readline())
        self.file.seek(currentPos)
        return hasNextLine

    def advance(self):
        '''Reads the next command from the input (if exists) and makes it the current command'''
        if self.hasMoreLines():
            self.currentCommand = self.file.readline()

    def instructionType(self):
        '''Returns the type of the current command'''
        self.currentCommand = ''.join(self.currentCommand.split())      # remove whitespaces
        self.currentCommand = self.currentCommand.partition("//")[0]    # remove comments
        if not self.currentCommand:     # currentCommand is a comment or an empty line
            return ""
        elif self.currentCommand.startswith('@'):
            return "A_INSTRUCTION"
        elif self.currentCommand.startswith('('):
            return "L_INSTRUCTION"
        else:
            return "C_INSTRUCTION"

    def symbol(self):
        '''Return the symbol or decimal Xxx of the current @Xxx or (Xxx)'''
        if self.instructionType() == "A_INSTRUCTION":
            return self.currentCommand[1:]      # cut first character
        elif self.instructionType() == "L_INSTRUCTION":
            return self.currentCommand[1:-1]    # cut first and last characters

    def dest(self):
        '''Returns the dest mnemonic in the current C-command'''
        if self.instructionType() == "C_INSTRUCTION":
            if "=" in self.currentCommand:
                return self.currentCommand.partition("=")[0]    # left to "="
        return "null"

    def comp(self):
        '''Returns the comp mnemonic in the current C-command'''
        if self.instructionType() == "C_INSTRUCTION":
            if '=' in self.currentCommand:                      # if includes dest then take
                afterEq = self.currentCommand.split('=')[1]     # what's right to "="
                if ';' in afterEq:                              # and if includes jump take
                    return afterEq.split(';')[0]                # what's left to ";"
                return afterEq
            elif ';' in self.currentCommand:                    # if doesn't include dest take
                return self.currentCommand.split(';')[0]        # all that's left to ";"
            else:
                return self.currentCommand
        return "null"
    
    def jump(self):
        '''Returns the jump mnemonic in the current C-command'''
        if self.instructionType() == "C_INSTRUCTION":
            if ';' in self.currentCommand:
                return self.currentCommand.split(';')[1]        # take what's right to ";"
        return "null"