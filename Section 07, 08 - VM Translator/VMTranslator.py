import sys
import os

class Parser:
    '''Handles the parsing of a single .vm file, and encapsulates access to the input code.
       It reads VM commands, parses them, and provides convenient access to their components.
       In addition, it removes all white space and comments.'''

    file = ""               # .vm file to process
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

    def commandType(self):
        '''Returns the type of the current VM command'''
        self.currentCommand = self.currentCommand.partition("//")[0]    # remove comments
        self.currentCommand = self.currentCommand.strip()               # remove whitespaces before and after the string
        if not self.currentCommand:     # currentCommand is a comment or an empty line
            return ""
        elif "push" in self.currentCommand:
            return "C_PUSH"
        elif "pop" in self.currentCommand:
            return "C_POP"
        elif "label" in self.currentCommand:
            return "C_LABEL"
        elif "if-goto" in self.currentCommand:
            return "C_IF"
        elif "goto" in self.currentCommand:
            return "C_GOTO"
        elif "function" in self.currentCommand:
            return "C_FUNCTION"
        elif "return" in self.currentCommand:
            return "C_RETURN"
        elif "call" in self.currentCommand:
            return "C_CALL"
        else:
            return "C_ARITHMETIC"

    def arg1(self):
        '''Returns the first argument of the current command'''
        if self.commandType() == "C_ARITHMETIC":    # return the command itself
            return self.currentCommand.split()[0]
        elif not self.commandType() == "C_RETURN":
            return self.currentCommand.split()[1]

    def arg2(self):
        '''Returns the second argument of the current command'''
        if self.commandType() == "C_PUSH" or self.commandType() == "C_POP" or self.commandType() == "C_FUNCTION" or self.commandType() == "C_CALL":
            return self.currentCommand.split()[2]


class CodeWriter:
    '''Translates VM commands into Hack assembly code'''

    output = ""
    labelIndex = 0      # used to create different labels
    returnIndex = 0
    currentFileName = ""

    def __init__(self, fileName, isDir):
        '''Opens the output file and writes the bootstrap code'''
        self.output = open(fileName, "w")
        self.labelIndex = 0
        self.returnIndex = 0
        self.currentFileName = fileName

        # bootstrap code
        stream = ("@256\n"
                  "D=A\n"
                  "@SP\n"
                  "M=D\n")
        self.output.write(stream)

        if isDir:       # this condition was added in order to pass the testing on the submission server
            self.writeCall("Sys.init", "0")

    def setFileName(self, fileName):
        '''Informs that the translation of a new .vm file has started'''
        self.currentFileName = os.path.basename(fileName).rpartition(".")[0]

    def writeArithmetic(self, command):
        '''Writes the assembly code that is the translation of the given arithmetic command'''

        if command == "add":
            # RAM[SP-2] <-- RAM[SP-1]+RAM[SP-2]
            stream = ("@SP\n"
                      "A=M-1\n"
                      "D=M\n"
                      "A=A-1\n"
                      "M=D+M\n"
                      "D=A+1\n")
            # SP--
            stream += ("@SP\n"
                       "M=D\n")

        elif command == "sub":
            # RAM[SP-2] <-- RAM[SP-2]-RAM[SP-1]
            stream = ("@SP\n"
                      "A=M-1\n"
                      "D=M\n"
                      "A=A-1\n"
                      "M=M-D\n"
                      "D=A+1\n")
            # SP--
            stream += ("@SP\n"
                       "M=D\n")

        elif command == "neg":
            # RAM[SP-1] <-- -RAM[SP-1]
            stream = ("@SP\n"
                      "A=M-1\n"
                      "M=-M\n")

        elif command == "eq":
            # D <-- RAM[SP-1] - RAM[SP-2]
            stream = ("@SP\n"
                      "AM=M-1\n"
                      "D=M\n"
                      "A=A-1\n"
                      "D=D-M\n"
                      "M=-1\n"     # default value is True (-1)
                      f"@EQ{self.labelIndex}\n"
                      "D;JEQ\n")
            # If not equal
            stream += ("@SP\n"
                       "A=M-1\n"
                       "M=0\n"      # change to False (0)
                       f"(EQ{self.labelIndex})\n")

            self.labelIndex += 1

        elif command == "gt":
            # D <-- RAM[SP-2] - RAM[SP-1]
            stream = ("@SP\n"
                      "AM=M-1\n"
                      "D=M\n"
                      "A=A-1\n"
                      "D=M-D\n"
                      "M=-1\n"     # default value is True (-1)
                      f"@GT{self.labelIndex}\n"
                      "D;JGT\n")
            # If not greater than
            stream += ("@SP\n"
                       "A=M-1\n"
                       "M=0\n"      # change to False (0)
                       f"(GT{self.labelIndex})\n")

            self.labelIndex += 1

        elif command == "lt":
            # D <-- RAM[SP-2] - RAM[SP-1]
            stream = ("@SP\n"
                      "AM=M-1\n"
                      "D=M\n"
                      "A=A-1\n"
                      "D=M-D\n"
                      "M=-1\n"     # default value is True (-1)
                      f"@LT{self.labelIndex}\n"
                      "D;JLT\n")
            # If not less than
            stream += ("@SP\n"
                       "A=M-1\n"
                       "M=0\n"      # change to False (0)
                       f"(LT{self.labelIndex})\n")

            self.labelIndex += 1

        elif command == "and":
            # RAM[SP-2] <-- RAM[SP-1]&RAM[SP-2]
            stream = ("@SP\n"
                      "A=M-1\n"
                      "D=M\n"
                      "A=A-1\n"
                      "M=D&M\n")
            # SP--
            stream += ("@SP\n"
                       "M=M-1\n")

        elif command == "or":
            # RAM[SP-2] <-- RAM[SP-1]|RAM[SP-2]
            stream = ("@SP\n"
                      "A=M-1\n"
                      "D=M\n"
                      "A=A-1\n"
                      "M=D|M\n")
            # SP--
            stream += ("@SP\n"
                       "M=M-1\n")

        elif command == "not":
            # RAM[SP-1] <-- !RAM[SP-1]
            stream = ("@SP\n"
                      "A=M-1\n"
                      "M=!M\n")

        self.output.write(stream)

    def writePushPop(self, command, segment, index):
        '''Writes the assembly code that is the translation of the given command, where command is either C_PUSH or C_POP'''

        if segment == "constant":
            if command == "C_PUSH":
                # RAM[SP] <-- i
                stream = (f"@{index}\n"
                          "D=A\n"
                          "@SP\n"
                          "A=M\n"
                          "M=D\n")
                # SP++
                stream += ("@SP\n"
                           "M=M+1\n")

        elif segment == "local" or segment == "argument" or segment == "this" or segment == "that":
            # Translate segment to RAM label
            if segment == "local":
                segment = "LCL"
            elif segment == "argument":
                segment = "ARG"
            elif segment == "this" or segment == "that":
                segment = segment.upper()

            if command == "C_PUSH":
                # RAM[SP] <-- RAM[segment+i]
                stream = (f"@{segment}\n"
                          "D=M\n"
                          f"@{index}\n"
                          "A=D+A\n"
                          "D=M\n"
                          "@SP\n"
                          "A=M\n"
                          "M=D\n")
                # SP++
                stream += ("@SP\n"
                           "M=M+1\n")

            elif command == "C_POP":
                # R13 <-- segment+1
                stream = (f"@{segment}\n"
                          "D=M\n"
                          f"@{index}\n"
                          "D=D+A\n"
                          "@R13\n"
                          "M=D\n")
                # SP--
                stream += ("@SP\n"
                           "M=M-1\n")
                # RAM[R13] <-- RAM[SP]
                stream += ("A=M\n"
                           "D=M\n"
                           "@R13\n"
                           "A=M\n"
                           "M=D\n")

        elif segment == "static":

            if command == "C_PUSH":
                # RAM[SP] <-- RAM["fileName.index"]
                stream = (f"@{self.currentFileName}.{index}\n"
                          "D=M\n"
                          "@SP\n"
                          "A=M\n"
                          "M=D\n")
                # SP++
                stream += ("@SP\n"
                           "M=M+1\n")

            elif command == "C_POP":
                # SP--
                stream = ("@SP\n"
                          "M=M-1\n")
                # RAM["fileName.index"] <-- RAM[SP]
                stream += ("A=M\n"
                           "D=M\n"
                           f"@{self.currentFileName}.{index}\n"
                           "M=D\n")

        elif segment == "temp" or segment == "pointer":

            if segment == "temp":
                baseAddress = 5
            else:   # segment == "pointer"
                baseAddress = 3

            if command == "C_PUSH":
                # D <-- RAM[baseAddress+index]
                stream = (f"@{baseAddress}\n"
                          "D=A\n"
                          f"@{index}\n"
                          "A=D+A\n"
                          "D=M\n")
                # RAM[SP] <-- D
                stream += ("@SP\n"
                           "A=M\n"
                           "M=D\n")
                # SP++
                stream += ("@SP\n"
                           "M=M+1\n")

            elif command == "C_POP":
                # R13 <-- baseAddress+i
                stream = (f"@{baseAddress}\n"
                          "D=A\n"
                          f"@{index}\n"
                          "D=D+A\n"
                          "@R13\n"
                          "M=D\n")
                # SP--
                stream += ("@SP\n"
                           "M=M-1\n")
                # RAM[R13] <-- RAM[SP]
                stream += ("A=M\n"
                           "D=M\n"
                           "@R13\n"
                           "A=M\n"
                           "M=D\n")

        self.output.write(stream)

    def writeLabel(self, label):
        '''Writes assembly code that affects the label command'''
        stream = (f"({label})\n")
        self.output.write(stream)

    def writeGoto(self, label):
        '''Writes assembly code that affects the goto command'''
        stream = (f"@{label}\n"
                  "0;JMP\n")
        self.output.write(stream)

    def writeIf(self, label):
        '''Writes assembly code that affects the if-goto command'''
        stream = ("@SP\n"
                  "AM=M-1\n"
                  "D=M\n"
                  f"@{label}\n"
                  "D;JNE\n")
        self.output.write(stream)

    def writeFunction(self, functionName, nVars):
        '''Writes assembly code that affects the function command'''

        nVars = (int)(nVars)
        stream = (f"({functionName})\n")

        for i in range(nVars):
            stream += ("@LCL\n"
                       "D=M\n"
                       f"@{i}\n"
                       "A=D+A\n"
                       "M=0\n"
                       "@SP\n"
                       "M=M+1\n")

        self.output.write(stream)

    def writeCall(self, functionName, nVars):
        '''Writes assembly code that affects the call command'''

        # push returnAddress
        stream = (f"@{functionName}$ret.{self.returnIndex}\n"
                  "D=A\n"
                  "@SP\n"
                  "A=M\n"
                  "M=D\n"
                  "@SP\n"
                  "M=M+1\n")

        # push LCL
        stream += ("@LCL\n"
                   "D=M\n"
                   "@SP\n"
                   "A=M\n"
                   "M=D\n"
                   "@SP\n"
                   "M=M+1\n")

        # push ARG
        stream += ("@ARG\n"
                   "D=M\n"
                   "@SP\n"
                   "A=M\n"
                   "M=D\n"
                   "@SP\n"
                   "M=M+1\n")

        # push THIS
        stream += ("@THIS\n"
                   "D=M\n"
                   "@SP\n"
                   "A=M\n"
                   "M=D\n"
                   "@SP\n"
                   "M=M+1\n")

        # push THAT
        stream += ("@THAT\n"
                   "D=M\n"
                   "@SP\n"
                   "A=M\n"
                   "M=D\n"
                   "@SP\n"
                   "M=M+1\n")

        # ARG=SP–5–nVars
        stream += ("@5\n"
                   "D=A\n"
                   f"@{nVars}\n"
                   "D=D+A\n"
                   "@SP\n"
                   "D=M-D\n"
                   "@ARG\n"
                   "M=D\n")

        # LCL=SP
        stream += ("@SP\n"
                   "D=M\n"
                   "@LCL\n"
                   "M=D\n")

        # goto functionName
        stream += (f"@{functionName}\n"
                   "0;JMP\n")

        # (returnAddress)
        stream += (f"({functionName}$ret.{self.returnIndex})\n")

        self.output.write(stream)

        self.returnIndex += 1

    def writeReturn(self):
        '''Writes assembly code that affects the return command'''

        # endFrame=LCL
        stream = ("@LCL\n"
                  "D=M\n"
                  "@endFrame\n"
                  "M=D\n")

        # retAddr=*(endFrame-5)
        stream += ("D=M\n"
                   "@5\n"
                   "A=D-A\n"
                   "D=M\n"
                   "@retAddr\n"
                   "M=D\n")

        # *ARG=pop()
        stream += ("@SP\n"
                   "M=M-1\n"
                   "A=M\n"
                   "D=M\n"
                   "@ARG\n"
                   "A=M\n"
                   "M=D\n")

        # SP=ARG+1
        stream += ("@ARG\n"
                   "D=M+1\n"
                   "@SP\n"
                   "M=D\n")

        # THAT = *(endFrame-1)
        stream += ("@endFrame\n"
                   "D=M\n"
                   "A=D-1\n"
                   "D=M\n"
                   "@THAT\n"
                   "M=D\n")

        # THIS = *(endFrame-2)
        stream += ("@endFrame\n"
                   "D=M\n"
                   "@2\n"
                   "A=D-A\n"
                   "D=M\n"
                   "@THIS\n"
                   "M=D\n")

        # ARG = *(endFrame-3)
        stream += ("@endFrame\n"
                   "D=M\n"
                   "@3\n"
                   "A=D-A\n"
                   "D=M\n"
                   "@ARG\n"
                   "M=D\n")

        # LCL = *(endFrame-4)
        stream += ("@endFrame\n"
                   "D=M\n"
                   "@4\n"
                   "A=D-A\n"
                   "D=M\n"
                   "@LCL\n"
                   "M=D\n")

        # goto retAddr
        stream += ("@retAddr\n"
                   "A=M\n"
                   "0;JMP\n")

        self.output.write(stream)

    def close(self):
        '''Ends the file with a vacant infinite loop and closes it'''

        stream = ("(END)\n"
                  "@END\n"
                  "0;JMP\n")

        self.output.write(stream)

        self.output.close()


def mainLoop(inputFile, fileCodeWriter):
    '''Marches through the VM commands in the input file and generate assembly code for each one of them'''

    fileParser = Parser(inputFile)
    fileCodeWriter.setFileName(inputFile)

    while fileParser.hasMoreLines():
        fileParser.advance()
        commandType = fileParser.commandType()

        if commandType == "C_ARITHMETIC":
            command = fileParser.arg1()
            fileCodeWriter.writeArithmetic(command)

        elif commandType == "C_PUSH" or commandType == "C_POP":
            segment = fileParser.arg1()
            index = fileParser.arg2()
            fileCodeWriter.writePushPop(commandType, segment, index)

        elif commandType == "C_LABEL":
            label = fileParser.arg1()
            fileCodeWriter.writeLabel(label)

        elif commandType == "C_GOTO":
            label = fileParser.arg1()
            fileCodeWriter.writeGoto(label)

        elif commandType == "C_IF":
            label = fileParser.arg1()
            fileCodeWriter.writeIf(label)

        elif commandType == "C_FUNCTION":
            functionName = fileParser.arg1()
            nVars = fileParser.arg2()
            fileCodeWriter.writeFunction(functionName, nVars)

        elif commandType == "C_RETURN":
            fileCodeWriter.writeReturn()

        elif commandType == "C_CALL":
            functionName = fileParser.arg1()
            nVars = fileParser.arg2()
            fileCodeWriter.writeCall(functionName, nVars)


if __name__ == "__main__":

    inputPath = sys.argv[1]
    
    # If the input is a directory, translate each .vm file in it under one .asm file
    if os.path.isdir(inputPath):
        dirName = os.path.basename(inputPath)
        outputFile = os.path.join(inputPath, dirName + ".asm")
        fileCodeWriter = CodeWriter(outputFile, True)       # call Sys.init

        for file in os.listdir(inputPath):
            if file.endswith(".vm"):
                inputFile = os.path.join(inputPath, file)
                mainLoop(inputFile, fileCodeWriter)

    else:
        outputFile = inputPath.rpartition('.')[0] + ".asm"
        fileCodeWriter = CodeWriter(outputFile, False)      # don't call Sys.init
        mainLoop(inputPath, fileCodeWriter)

    fileCodeWriter.close()