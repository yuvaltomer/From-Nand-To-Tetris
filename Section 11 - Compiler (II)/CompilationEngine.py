import JackTokenizer as Jt
import SymbolTable as St
import VMWriter as VMw

THIS = "this"
THAT = "that"
POINTER = "pointer"
TEMP = "temp"
CONSTANT = "constant"
CONSTRUCTOR = "constructor"
FUNCTION = "function"
METHOD = "method"
LET = "let"
IF = "if"
DO = "do"
WHILE = "while"
RETURN = "return"
ADD = "add"
SUB = "sub"
NEG = "neg"
EQ = "eq"
GT = "gt"
LT = "lt"
AND = "and"
OR = "or"
NOT = "not"


class CompilationEngine:
    '''Compiles the input Jack code into a VM file'''

    def __init__(self, inputName):
        '''Creates a new compilation engine with the given input and output'''
        self.tokenizer = Jt.JackTokenizer(inputName)
        self.writer = VMw.VMWriter(inputName)
        self.classTable = St.SymbolTable()
        self.subroutineTable = St.SymbolTable()
        self.className = ""
        self.subroutineName = ""
        self.labelIndex = 1
        self.subroutineType = ""
        self.nLocalVars = 0


    def compileClass(self):
        '''Compiles a complete class'''

        if self.tokenizer.hasMoreTokens():

            self.tokenizer.advance()
            self.classTable.reset()

            self._eat("class")
            self.className = self._eat(self.tokenizer.identifier())
            self._eat("{")

            while self.tokenizer.keyWord() == St.STATIC or self.tokenizer.keyWord() == St.FIELD:
                self.compileClassVarDec()

            while self.tokenizer.keyWord() == CONSTRUCTOR or self.tokenizer.keyWord() == FUNCTION or self.tokenizer.keyWord() == METHOD:
                self.compileSubroutine()

            self._eat("}")

            self.writer.close()


    def compileClassVarDec(self):
        '''Compiles a static variable declaration or a field declaration'''

        kind = self._eat(self.tokenizer.keyWord())

        if self.tokenizer.tokenType() == Jt.KEYWORD: # 'int', 'char' or 'boolean'
            type = self._eat(self.tokenizer.keyWord())
        elif self.tokenizer.tokenType() == Jt.IDENTIFIER:    # className
            type = self._eat(self.tokenizer.identifier())

        name = self._eat(self.tokenizer.identifier())

        self.classTable.define(name, type, kind)

        while self.tokenizer.symbol() == ",":
            self._eat(",")
            name = self._eat(self.tokenizer.identifier())
            self.classTable.define(name, type, kind)

        self._eat(";")


    def compileSubroutine(self):
        '''Compiles a complete method, function, or constructor'''

        self.subroutineTable.reset()
        
        self.subroutineType = self._eat(self.tokenizer.keyWord())

        if self.tokenizer.tokenType() == Jt.KEYWORD: # 'int', 'char', 'boolean' or 'void'
            self._eat(self.tokenizer.keyWord())
        elif self.tokenizer.tokenType() == Jt.IDENTIFIER:    # className
            self._eat(self.tokenizer.identifier())

        self.subroutineName = self._eat(self.tokenizer.identifier())
        self._eat("(")
        self.compileParameterList()
        self._eat(")")
        self.compileSubroutineBody()


    def compileParameterList(self):
        '''Compiles a (possibly empty) parameter list, not including the enclosing "()"'''

        if self.tokenizer.tokenType() != Jt.SYMBOL:  # if the parameterList is not empty
            if self.tokenizer.tokenType() == Jt.KEYWORD: # 'int', 'char', 'boolean'
                type = self._eat(self.tokenizer.keyWord())
            elif self.tokenizer.tokenType() == Jt.IDENTIFIER:    # className
                type = self._eat(self.tokenizer.identifier())
            name = self._eat(self.tokenizer.identifier())
            self.subroutineTable.define(name, type, St.ARG)

            while self.tokenizer.symbol() == ",":
                self._eat(",")
                if self.tokenizer.tokenType() == Jt.KEYWORD: # 'int', 'char', 'boolean'
                    type = self._eat(self.tokenizer.keyWord())
                elif self.tokenizer.tokenType() == Jt.IDENTIFIER:    # className
                    type = self._eat(self.tokenizer.identifier())
                name = self._eat(self.tokenizer.identifier())
                self.subroutineTable.define(name, type, St.ARG)


    def compileSubroutineBody(self):
        '''Compiles a subroutine's body'''

        self._eat("{")

        self.nLocalVars = 0

        while self.tokenizer.keyWord() == "var":
            self.compileVarDec()

        self.writer.writeFunction(f"{self.className}.{self.subroutineName}", self.nLocalVars)

        if self.subroutineType == CONSTRUCTOR:
            self.writer.writePush(CONSTANT, self.classTable.varCount(St.FIELD))
            self.writer.writeCall("Memory.alloc", 1)
            self.writer.writePop(POINTER, 0)

        elif self.subroutineType == METHOD:
            self.writer.writePush(St.ARG, 0)
            self.writer.writePop(POINTER, 0)

        
        if not(self.tokenizer.tokenType() == Jt.SYMBOL and self.tokenizer.symbol() == "}"):
            self.compileStatements()

        self._eat("}")


    def compileVarDec(self):
        '''Compiles a var declaration'''

        self._eat("var")

        if self.tokenizer.tokenType() == Jt.KEYWORD: # 'int', 'char' or 'boolean'
            type = self._eat(self.tokenizer.keyWord())
        elif self.tokenizer.tokenType() == Jt.IDENTIFIER:    # className
            type = self._eat(self.tokenizer.identifier())

        name = self._eat(self.tokenizer.identifier())
        self.subroutineTable.define(name, type, St.VAR)
        self.nLocalVars += 1

        while self.tokenizer.symbol() == ",":
            self._eat(",")
            name = self._eat(self.tokenizer.identifier())
            self.subroutineTable.define(name, type, St.VAR)
            self.nLocalVars += 1

        self._eat(";")


    def compileStatements(self):
        '''Compiles a sequence of statements, not including the enclosing "{}"'''

        statement = self.tokenizer.keyWord()
        while statement == LET or statement == IF or statement == WHILE or statement == DO or statement == RETURN:
            if statement == LET:
                self.compileLet()
            elif statement == IF:
                self.compileIf()
            elif statement == WHILE:
                self.compileWhile()
            elif statement == DO:
                self.compileDo()
            elif statement == RETURN:
                self.compileReturn()
            statement = self.tokenizer.keyWord()


    def compileLet(self):
        '''Compiles a let statement'''

        self._eat(LET)
        varName = self._eat(self.tokenizer.identifier())
        segment = self.subroutineTable.kindOf(varName)
        if not segment:
            segment = self.classTable.kindOf(varName)
        if segment == St.FIELD:
            segment = THIS
        index = self.subroutineTable.indexOf(varName)
        if index is None:
            index = self.classTable.indexOf(varName)

        if self.tokenizer.symbol() == "[":
            self._eat("[")
            self.writer.writePush(segment, index)
            self.compileExpression()
            self.writer.writeArithmetic(ADD)
            self._eat("]")
            self._eat("=")
            self.compileExpression()
            self.writer.writePop(TEMP, 0)
            self.writer.writePop(POINTER, 1)
            self.writer.writePush(TEMP, 0)
            self.writer.writePop(THAT, 0)

        else:
            self._eat("=")
            self.compileExpression()
            self.writer.writePop(segment, index)

        self._eat(";")


    def compileIf(self):
        '''Compiles an if statement, possibly with a trailing else clause'''

        self._eat(IF)
        self._eat("(")
        self.compileExpression()
        self._eat(")")

        self.writer.writeArithmetic(NOT)

        firstLabel = f"L{self.labelIndex}"
        self.labelIndex += 1
        self.writer.writeIf(firstLabel)

        self._eat("{")
        self.compileStatements()
        self._eat("}")

        secondLabel = f"L{self.labelIndex}"
        self.labelIndex += 1
        self.writer.writeGoto(secondLabel)

        self.writer.writeLabel(firstLabel)

        if self.tokenizer.keyWord() == "else":
            self._eat("else")
            self._eat("{")
            self.compileStatements()
            self._eat("}")

        self.writer.writeLabel(secondLabel)


    def compileWhile(self):
        '''Compiles a while statement'''

        firstLabel = f"L{self.labelIndex}"
        self.labelIndex += 1
        self.writer.writeLabel(firstLabel)

        self._eat(WHILE)
        self._eat("(")
        self.compileExpression()
        self._eat(")")

        self.writer.writeArithmetic(NOT)

        secondLabel = f"L{self.labelIndex}"
        self.labelIndex += 1
        self.writer.writeIf(secondLabel)

        self._eat("{")
        self.compileStatements()
        self._eat("}")

        self.writer.writeGoto(firstLabel)
        self.writer.writeLabel(secondLabel)


    def compileDo(self):
        '''Compiles a do statement'''

        self._eat(DO)
        self.compileExpression()
        self.writer.writePop(TEMP, 0)

        self._eat(";")


    def compileReturn(self):
        '''Compiles a return statement'''

        self._eat(RETURN)

        if self.tokenizer.symbol() != ";":
            self.compileExpression()
        else:
            self.writer.writePush(CONSTANT, 0)

        self.writer.writeReturn()

        self._eat(";")


    def compileExpression(self):
        '''Compiles an expression'''

        self.compileTerm()

        while self.tokenizer.tokenType() == Jt.SYMBOL and self.tokenizer.symbol() in ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]:    # adapted to comply with XML notations

            operator = self._eat(self.tokenizer.symbol())
            self.compileTerm()

            if operator == "+":
                self.writer.writeArithmetic(ADD)
            elif operator == "-":
                self.writer.writeArithmetic(SUB)
            elif operator == "*":
                self.writer.writeCall("Math.multiply", 2)
            elif operator == "/":
                self.writer.writeCall("Math.divide", 2)
            elif operator == "/":
                self.writer.writeCall("Math.divide", 2)
            elif operator == "&amp;":
                self.writer.writeArithmetic(AND)
            elif operator == "|":
                self.writer.writeArithmetic(OR)
            elif operator == "&lt;":
                self.writer.writeArithmetic(LT)
            elif operator == "&gt;":
                self.writer.writeArithmetic(GT)
            elif operator == "=":
                self.writer.writeArithmetic(EQ)


    def compileTerm(self):
        '''Compiles a term'''

        if self.tokenizer.tokenType() == Jt.IDENTIFIER:
            name = self._eat(self.tokenizer.identifier())
            segment = self.subroutineTable.kindOf(name)
            if not segment:
                segment = self.classTable.kindOf(name)
            if segment == St.FIELD:
                segment = THIS
            index = self.subroutineTable.indexOf(name)
            if index is None:
                index = self.classTable.indexOf(name)

            if self.tokenizer.tokenType() == Jt.SYMBOL and self.tokenizer.symbol() in ["[", "(", "."]:

                if self.tokenizer.symbol() == "[":  # resolve into an array entry
                    self._eat("[")
                    self.writer.writePush(segment, index)
                    self.compileExpression()
                    self.writer.writeArithmetic(ADD)
                    self.writer.writePop(POINTER, 1)
                    self.writer.writePush(THAT, 0)
                    self._eat("]")

                elif self.tokenizer.symbol() == "(":    # term is "f(exp1, exp2, ...)"
                    self._eat("(")
                    self.writer.writePush(POINTER, 0)
                    nVars = self.compileExpressionList() + 1
                    self.writer.writeCall(f"{self.className}.{name}", nVars)  # should be thisClassName.subroutineName
                    self._eat(")")

                elif self.tokenizer.symbol() == ".":    # term is "c.f(exp1, exp2, ...)"

                    self._eat(".")

                    if segment:
                        functionName = self._eat(self.tokenizer.identifier())
                        type = self.subroutineTable.typeOf(name)
                        if not type:
                            type = self.classTable.typeOf(name)
                        name = f"{type}.{functionName}"
                        self._eat("(")
                        self.writer.writePush(segment, 0)
                        nVars = self.compileExpressionList() + 1
                        self.writer.writeCall(name, nVars)
                        self._eat(")")

                    else:
                        functionName = self._eat(self.tokenizer.identifier())
                        name = f"{name}.{functionName}"
                        self._eat("(")
                        nVars = self.compileExpressionList()
                        self.writer.writeCall(name, nVars)
                        self._eat(")")

            else:   # term is a variable
                segment = self.subroutineTable.kindOf(name)
                if not segment:
                    segment = self.classTable.kindOf(name)
                if segment == St.FIELD:
                    segment = THIS
                index = self.subroutineTable.indexOf(name)
                if index is None:
                    index = self.classTable.indexOf(name)
                self.writer.writePush(segment, index)

        elif self.tokenizer.tokenType() == Jt.INT_CONST: # term is a constant
            number = self._eat(self.tokenizer.intVal())
            self.writer.writePush(CONSTANT, number)

        elif self.tokenizer.tokenType() == Jt.STRING_CONST:
            string = self._eat(self.tokenizer.stringVal())
            self.writer.writePush(CONSTANT, len(string))
            self.writer.writeCall("String.new", 1)

            for letter in string:
                self.writer.writePush(CONSTANT, ord(letter))
                self.writer.writeCall("String.appendChar", 2)

        elif self.tokenizer.tokenType() == Jt.KEYWORD:   # term is a keyword constant
            constant = self._eat(self.tokenizer.keyWord())

            if constant == "true":
                self.writer.writePush(CONSTANT, 1)
                self.writer.writeArithmetic(NEG)

            elif constant == "false" or constant == "null":
                self.writer.writePush(CONSTANT, 0)

            elif constant == THIS:
                self.writer.writePush(POINTER, 0)

        elif self.tokenizer.tokenType() == Jt.SYMBOL:

            if self.tokenizer.symbol() == "(":  # term is "(exp)"
                self._eat("(")
                self.compileExpression()
                self._eat(")")

            elif self.tokenizer.symbol() in ["-", "~"]: # term is "unaryOp term"
                symbol = self._eat(self.tokenizer.symbol())
                self.compileTerm()

                if symbol == "-":
                    self.writer.writeArithmetic(NEG)
                else:
                    self.writer.writeArithmetic(NOT)


    def compileExpressionList(self):
        '''Compiles a (possibly empty) comma-seperated list of expressions. Returns the number of expressions in the list'''
        
        numberOfExpressions = 0

        if self.tokenizer.tokenType() != Jt.SYMBOL or (self.tokenizer.tokenType() == Jt.SYMBOL and self.tokenizer.symbol() != ")"):   # if the list is not empty
            self.compileExpression()
            numberOfExpressions += 1

            while self.tokenizer.symbol() == ",":
                self._eat(",")
                self.compileExpression()
                numberOfExpressions += 1

        return numberOfExpressions


    def _eat(self, str):
        '''Private function used to process the tokens'''

        currentTokenType = self.tokenizer.tokenType()

        # Set currentToken according to currentTokenType
        if currentTokenType == Jt.KEYWORD:
            currentToken = self.tokenizer.keyWord()
        elif currentTokenType == Jt.SYMBOL:
            currentToken = self.tokenizer.symbol()
        elif currentTokenType == Jt.IDENTIFIER:
            currentToken = self.tokenizer.identifier()
        elif currentTokenType == Jt.INT_CONST:
            currentToken = self.tokenizer.intVal()
        elif currentTokenType == Jt.STRING_CONST:
            currentToken = self.tokenizer.stringVal()

        if str != currentToken:
            raise Exception("Error")    # consider changing the message
        else:
            self.tokenizer.advance()
            return currentToken