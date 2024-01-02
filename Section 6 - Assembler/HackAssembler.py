'''Reads as input a text file named Prog.asm, containing a Hack assembly program,
   and produces as output a text file named Prog.hack, containing the translated Hack machine code'''

import sys
import Parser
import Code
import SymbolTable

def symbolTableInit(symbolTable):
    '''Initializes the symbol table with all the predefined symbols and their pre-allocated RAM addresses'''
    symbolTable.addEntry("SP", 0)
    symbolTable.addEntry("LCL", 1)
    symbolTable.addEntry("ARG", 2)
    symbolTable.addEntry("THIS", 3)
    symbolTable.addEntry("THAT", 4)
    symbolTable.addEntry("R0", 0)
    symbolTable.addEntry("R1", 1)
    symbolTable.addEntry("R2", 2)
    symbolTable.addEntry("R3", 3)
    symbolTable.addEntry("R4", 4)
    symbolTable.addEntry("R5", 5)
    symbolTable.addEntry("R6", 6)
    symbolTable.addEntry("R7", 7)
    symbolTable.addEntry("R8", 8)
    symbolTable.addEntry("R9", 9)
    symbolTable.addEntry("R10", 10)
    symbolTable.addEntry("R11", 11)
    symbolTable.addEntry("R12", 12)
    symbolTable.addEntry("R13", 13)
    symbolTable.addEntry("R14", 14)
    symbolTable.addEntry("R15", 15)
    symbolTable.addEntry("SCREEN", 16384)
    symbolTable.addEntry("KBD", 24576)

def replaceLabels(fileParser, symbolTable):
    '''Enters all the program's labels along with their ROM addresses into the symbol table'''
    lineNumber = 0
    while fileParser.hasMoreLines():

        fileParser.advance()

        if fileParser.instructionType() == "A_INSTRUCTION" or fileParser.instructionType() == "C_INSTRUCTION":
            lineNumber += 1

        if fileParser.instructionType() == "L_INSTRUCTION":
            symbolTable.addEntry(fileParser.symbol(), lineNumber)
            
    fileParser.file.seek(0)

# Create a SymbolTable object and initialize it with the predefined symbols
symbolTable = SymbolTable.SymbolTable()
symbolTableInit(symbolTable)

# Get .asm file name from input and open a .hack with the same name
inputFilePath = sys.argv[1]
outputFilePath = inputFilePath.rpartition(".")[0] + ".hack"
outputFile = open(outputFilePath, "w")

# Create a Parser object to parse the input .asm file and replace labels with ROM addresses
fileParser = Parser.Parser(inputFilePath)
replaceLabels(fileParser, symbolTable)

nextFreeRAMAddress = 16

# Parse each line seperately
while fileParser.hasMoreLines():

    fileParser.advance()

    if fileParser.instructionType() == "C_INSTRUCTION":

        code = Code.Code()

        instructionType = "111"
        AorM = "0"

        # get binary code of dest mnemonic
        destString = fileParser.dest()
        destBin = code.dest(destString)

        # get binary code of comp mnemonic, together with the "a" bit
        compString = fileParser.comp()
        if "M" in compString:
            AorM = "1"
        compBin = code.comp(compString)

        # get binary code of jump mnemonic
        jumpString = fileParser.jump()
        jumpBin = code.jump(jumpString)

        # write the binary code to the .hack file
        # if fileParser.hasMoreLines():
        outputFile.write(instructionType + AorM + compBin + destBin + jumpBin + "\n")
        # else:
            # outputFile.write(instructionType + AorM + compBin + destBin + jumpBin)

    elif fileParser.instructionType() == "A_INSTRUCTION":

        symbol = fileParser.symbol()

        # check if address or symbol
        if not symbol.isnumeric():

                # if the symbol is defined get its address
                if symbolTable.contains(symbol):
                    symbol = symbolTable.getAddress(symbol)

                # else, add a new symbol and get its address
                else:
                    symbolTable.addEntry(symbol, nextFreeRAMAddress)
                    nextFreeRAMAddress += 1
                    symbol = symbolTable.getAddress(symbol)

        instructionType = "0"

        # convert decimal to a 15-bit binary number
        addressBin = bin(int(symbol))[2:]
        addressBin15 = addressBin.rjust(15, "0")

        # write the binary code to the .hack file
        # if fileParser.hasMoreLines():
        outputFile.write(instructionType + addressBin15 + "\n")
        # else:
            # outputFile.write(instructionType + addressBin15)

fileParser.file.close()
outputFile.close()