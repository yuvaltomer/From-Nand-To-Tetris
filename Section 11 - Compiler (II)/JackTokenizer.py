import re

KEYWORD = "keyword"
SYMBOL = "symbol"
INT_CONST = "integerConstant"
STRING_CONST = "stringConstant"
IDENTIFIER = "identifier"

'''Define the patterns of the regular expressions each token type induces'''
COMMENTS_PATTERN = [re.compile("//.*\n*"), re.compile("/\*.*?\*/", re.DOTALL)]
KEYWORD_PATTERN = re.compile("^\s*(class|constructor|function|method|static|field|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)[^A-Za-z0-9_]\s*")
SYMBOL_PATTERN = re.compile("^\s*([()\[\]\{\},;=./&-|*~<+>])\s*")
INTEGER_PATTERN = re.compile("^\s*(\d\d*)\s*")
STRING_PATTERN = re.compile("^\s*\"(.*?)\"\s*")
IDENTIFIER_PATTERN = re.compile("^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*")

class JackTokenizer:
    '''Breaks the input stream into Jack-language tokens, as specified by the Jack grammar'''

    def __init__(self, fileName):
        '''Opens the input file'''

        input = open(fileName, "r")
        self.currentToken = ""
        self.type = ""

        # Remove all inline and multiline comments, and save the result as a string
        commentless = re.sub(COMMENTS_PATTERN[0], "", input.read())
        commentless = re.sub(COMMENTS_PATTERN[1], "", commentless)

        # Remove consequent white spaces and add non-empty lines to cleanInput
        self.cleanInput = ""
        for line in commentless.splitlines():
            if line.strip() != "":
                self.cleanInput += line.strip() + " "

    def hasMoreTokens(self):
        '''Checks if there are more tokens in the input'''

        if re.fullmatch(re.compile("^\s*"), self.cleanInput):   # if cleanInput only includes white spaces
            return False
        
        return True

    def advance(self):
        '''Gets the next token from the input and makes it the current token'''
        if self.hasMoreTokens():
            # Check to which of the six patterns above the beginning of cleanInput matches
            # Remove it from the beginning of the string and make it the currentToken
            currentMatch = re.match(KEYWORD_PATTERN, self.cleanInput)
            if currentMatch:
                self.cleanInput = re.sub(re.compile("^\s*(class|constructor|function|method|static|field|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)\s*"), "", self.cleanInput) # remove only the keyword and following white spaces
                self.type = KEYWORD
                self.currentToken = currentMatch.group(1)

            else:
                currentMatch = re.match(IDENTIFIER_PATTERN, self.cleanInput)
                if currentMatch:
                    self.cleanInput = re.sub(IDENTIFIER_PATTERN, "", self.cleanInput)
                    self.type = IDENTIFIER
                    self.currentToken = currentMatch.group(1)

                else:
                    currentMatch = re.match(INTEGER_PATTERN, self.cleanInput)
                    if currentMatch:
                        self.cleanInput = re.sub(INTEGER_PATTERN, "", self.cleanInput)
                        self.type = INT_CONST
                        self.currentToken = currentMatch.group(1)

                    else:
                        currentMatch = re.match(STRING_PATTERN, self.cleanInput)
                        if currentMatch:
                            self.cleanInput = re.sub(STRING_PATTERN, "", self.cleanInput)
                            self.type = STRING_CONST
                            self.currentToken = currentMatch.group(1)

                        else:
                            currentMatch = re.match(SYMBOL_PATTERN, self.cleanInput)
                            if currentMatch:
                                self.cleanInput = re.sub(SYMBOL_PATTERN, "", self.cleanInput)
                                self.type = SYMBOL
                                self.currentToken = currentMatch.group(1)

    def tokenType(self):
        '''Returns the type of the current token'''
        return self.type

    def keyWord(self):
        '''Returns the keyword which is the current token'''
        if self.type == KEYWORD:
            return self.currentToken

    def symbol(self):
        '''Returns the character which is the current token'''
        # Modify the returned value for "<", ">", """ and "&" to comply with XML notations
        if self.type == SYMBOL:
            if self.currentToken == "<":
                return "&lt;"
            elif self.currentToken == ">":
                    return "&gt;"
            elif self.currentToken == "\"":
                    return "&quot;"
            elif self.currentToken == "&":
                    return "&amp;"
            else:
                return self.currentToken

    def identifier(self):
        '''Returns the identifier which is the current token'''
        if self.type == IDENTIFIER:
            return self.currentToken

    def intVal(self):
        '''Returns the integer value of the current token'''
        if self.type == INT_CONST:
            return int(self.currentToken)

    def stringVal(self):
        '''Returns the string value of the current token, without the double quotes'''
        if self.type == STRING_CONST:
            return self.currentToken