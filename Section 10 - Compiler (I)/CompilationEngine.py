import JackTokenizer as Jt

CONSTRUCTOR = "constructor"
FUNCTION = "function"
METHOD = "method"
LET = "let"
IF = "if"
DO = "do"
WHILE = "while"
RETURN = "return"
STATIC = "static"
FIELD = "field"


class CompilationEngine:
    '''Emits a structured printout of the code wrapped in XML tags'''

    def __init__(self, inputName, outputName):
        '''Creates a new compilation engine with the given input and output'''
        self.tokenizer = Jt.JackTokenizer(inputName)
        self.output = open(f"{outputName}.xml", "w")


    def compileClass(self):
        '''Compiles a complete class'''

        if self.tokenizer.hasMoreTokens():

            self.tokenizer.advance()
            self.output.write("<class>\n")

            self._eat("class")
            self._eat(self.tokenizer.identifier())
            self._eat("{")

            while self.tokenizer.keyWord() == STATIC or self.tokenizer.keyWord() == FIELD:
                self.compileClassVarDec()

            while self.tokenizer.keyWord() == CONSTRUCTOR or self.tokenizer.keyWord() == FUNCTION or self.tokenizer.keyWord() == METHOD:
                self.compileSubroutine()

            self._eat("}")

            self.output.write("</class>\n")
            self.output.close()


    def compileClassVarDec(self):
        '''Compiles a static variable declaration or a field declaration'''

        self.output.write("<classVarDec>\n")

        self._eat(self.tokenizer.keyWord())

        if self.tokenizer.tokenType() == Jt.KEYWORD: # 'int', 'char' or 'boolean'
            self._eat(self.tokenizer.keyWord())
        elif self.tokenizer.tokenType() == Jt.IDENTIFIER:    # className
            self._eat(self.tokenizer.identifier())

        self._eat(self.tokenizer.identifier())

        while self.tokenizer.symbol() == ",":
            self._eat(",")
            self._eat(self.tokenizer.identifier())

        self._eat(";")

        self.output.write("</classVarDec>\n")


    def compileSubroutine(self):
        '''Compiles a complete method, function, or constructor'''

        self.output.write("<subroutineDec>\n")

        self._eat(self.tokenizer.keyWord())

        if self.tokenizer.tokenType() == Jt.KEYWORD: # 'int', 'char', 'boolean' or 'void'
            self._eat(self.tokenizer.keyWord())
        elif self.tokenizer.tokenType() == Jt.IDENTIFIER:    # className
            self._eat(self.tokenizer.identifier())

        self._eat(self.tokenizer.identifier())
        self._eat("(")
        self.compileParameterList()
        self._eat(")")
        self.compileSubroutineBody()

        self.output.write("</subroutineDec>\n")


    def compileParameterList(self):
        '''Compiles a (possibly empty) parameter list, not including the enclosing "()"'''

        self.output.write("<parameterList>\n")

        if self.tokenizer.tokenType() != Jt.SYMBOL:  # if the parameterList is not empty
            if self.tokenizer.tokenType() == Jt.KEYWORD: # 'int', 'char', 'boolean'
                self._eat(self.tokenizer.keyWord())
            elif self.tokenizer.tokenType() == Jt.IDENTIFIER:    # className
                self._eat(self.tokenizer.identifier())

            self._eat(self.tokenizer.identifier())

            while self.tokenizer.symbol() == ",":
                self._eat(",")
                if self.tokenizer.tokenType() == Jt.KEYWORD: # 'int', 'char', 'boolean'
                    self._eat(self.tokenizer.keyWord())
                elif self.tokenizer.tokenType() == Jt.IDENTIFIER:    # className
                    self._eat(self.tokenizer.identifier())
                self._eat(self.tokenizer.identifier())

        self.output.write("</parameterList>\n")


    def compileSubroutineBody(self):
        '''Compiles a subroutine's body'''

        self.output.write("<subroutineBody>\n")

        self._eat("{")

        while self.tokenizer.keyWord() == "var":
            self.compileVarDec()
        
        if not(self.tokenizer.tokenType() == Jt.SYMBOL and self.tokenizer.symbol() == "}"):
            self.compileStatements()

        self._eat("}")

        self.output.write("</subroutineBody>\n")


    def compileVarDec(self):
        '''Compiles a var declaration'''

        self.output.write("<varDec>\n")

        self._eat("var")

        if self.tokenizer.tokenType() == Jt.KEYWORD: # 'int', 'char' or 'boolean'
            self._eat(self.tokenizer.keyWord())
        elif self.tokenizer.tokenType() == Jt.IDENTIFIER:    # className
            self._eat(self.tokenizer.identifier())

        self._eat(self.tokenizer.identifier())

        while self.tokenizer.symbol() == ",":
            self._eat(",")
            self._eat(self.tokenizer.identifier())

        self._eat(";")

        self.output.write("</varDec>\n")


    def compileStatements(self):
        '''Compiles a sequence of statements, not including the enclosing "{}"'''

        self.output.write("<statements>\n")

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

        self.output.write("</statements>\n")


    def compileLet(self):
        '''Compiles a let statement'''

        self.output.write("<letStatement>\n")

        self._eat(LET)
        self._eat(self.tokenizer.identifier())

        if self.tokenizer.symbol() == "[":
            self._eat("[")
            self.compileExpression()
            self._eat("]")

        self._eat("=")
        self.compileExpression()
        self._eat(";")

        self.output.write("</letStatement>\n")


    def compileIf(self):
        '''Compiles an if statement, possibly with a trailing else clause'''

        self.output.write("<ifStatement>\n")

        self._eat(IF)
        self._eat("(")
        self.compileExpression()
        self._eat(")")
        self._eat("{")
        self.compileStatements()
        self._eat("}")

        if self.tokenizer.keyWord() == "else":
            self._eat("else")
            self._eat("{")
            self.compileStatements()
            self._eat("}")

        self.output.write("</ifStatement>\n")


    def compileWhile(self):
        '''Compiles a while statement'''
        self.output.write("<whileStatement>\n")

        self._eat(WHILE)
        self._eat("(")
        self.compileExpression()
        self._eat(")")
        self._eat("{")
        self.compileStatements()
        self._eat("}")

        self.output.write("</whileStatement>\n")


    def compileDo(self):
        '''Compiles a do statement'''

        self.output.write("<doStatement>\n")

        self._eat(DO)
        self._eat(self.tokenizer.identifier())

        # Compile subroutineCall
        if self.tokenizer.symbol() == "(":
            self._eat("(")
            self.compileExpressionList()
            self._eat(")")
        elif self.tokenizer.symbol() == ".":
            self._eat(".")
            self._eat(self.tokenizer.identifier())
            self._eat("(")
            self.compileExpressionList()
            self._eat(")")

        self._eat(";")

        self.output.write("</doStatement>\n")


    def compileReturn(self):
        '''Compiles a return statement'''

        self.output.write("<returnStatement>\n")

        self._eat(RETURN)

        if self.tokenizer.symbol() != ";":
            self.compileExpression()

        self._eat(";")

        self.output.write("</returnStatement>\n")


    def compileExpression(self):
        '''Compiles an expression'''

        self.output.write("<expression>\n")

        self.compileTerm()

        while self.tokenizer.tokenType() == Jt.SYMBOL and self.tokenizer.symbol() in ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]:    # adapted to comply with XML notations
            self._eat(self.tokenizer.symbol())
            self.compileTerm()

        self.output.write("</expression>\n")


    def compileTerm(self):
        '''Compiles a term'''

        self.output.write("<term>\n")

        if self.tokenizer.tokenType() == Jt.IDENTIFIER:
            self._eat(self.tokenizer.identifier())

            if self.tokenizer.tokenType() == Jt.SYMBOL:
                if self.tokenizer.symbol() == "[":  # resolve into an array entry
                    self._eat("[")
                    self.compileExpression()
                    self._eat("]")
                elif self.tokenizer.symbol() == "(":    # resolve into a subroutine call
                    self._eat("(")
                    self.compileExpressionList()
                    self._eat(")")
                elif self.tokenizer.symbol() == ".":    # # resolve into a subroutine call
                    self._eat(".")
                    self._eat(self.tokenizer.identifier())
                    self._eat("(")
                    self.compileExpressionList()
                    self._eat(")")

        elif self.tokenizer.tokenType() == Jt.INT_CONST:
            self._eat(self.tokenizer.intVal())

        elif self.tokenizer.tokenType() == Jt.STRING_CONST:
            self._eat(self.tokenizer.stringVal())

        elif self.tokenizer.tokenType() == Jt.KEYWORD:
            self._eat(self.tokenizer.keyWord())

        elif self.tokenizer.tokenType() == Jt.SYMBOL:
            if self.tokenizer.symbol() == "(":
                self._eat("(")
                self.compileExpression()
                self._eat(")")
            elif self.tokenizer.symbol() in ["-", "~"]:
                self._eat(self.tokenizer.symbol())
                self.compileTerm()

        self.output.write("</term>\n")


    def compileExpressionList(self):
        '''Compiles a (possibly empty) comma-seperated list of expressions. Returns the number of expressions in the list'''
        numberOfExpressions = 0

        self.output.write("<expressionList>\n")

        if self.tokenizer.tokenType() != Jt.SYMBOL or (self.tokenizer.tokenType() == Jt.SYMBOL and self.tokenizer.symbol() != ")"):   # if the list is not empty
            self.compileExpression()
            numberOfExpressions += 1

            while self.tokenizer.symbol() == ",":
                self._eat(",")
                self.compileExpression()
                numberOfExpressions += 1

        self.output.write("</expressionList>\n")

        return numberOfExpressions


    def _eat(self, str):
        '''Private function used to process the tokens with their matching XML tags'''

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
            self.output.write(f"<{currentTokenType}> {currentToken} </{currentTokenType}>\n")
            self.tokenizer.advance()