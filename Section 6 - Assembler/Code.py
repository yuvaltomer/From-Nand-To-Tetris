class Code:
    '''Translates Hack assembly language mnemonics into binary codes'''

    destCode = ""
    compCode = ""
    jumpCode = ""
    
    def __init__(self):
        '''Opens dictionary'''
        self.compCode = {   "0"   : "101010",
                            "1"   : "111111",
                            "-1"  : "111010",
                            "D"   : "001100",
                            "A"   : "110000",
                            "!D"  : "001101",
                            "!A"  : "110001",
                            "-D"  : "001111",
                            "-A"  : "110011",
                            "D+1" : "011111",
                            "A+1" : "110111",
                            "D-1" : "001110",
                            "A-1" : "110010",
                            "D+A" : "000010",
                            "D-A" : "010011",
                            "A-D" : "000111",
                            "D&A" : "000000",
                            "D|A" : "010101"    }
        self.destCode = {   "null" : "000",
                            "M"    : "001",
                            "D"    : "010",
                            "MD"   : "011",
                            "A"    : "100",
                            "AM"   : "101",
                            "AD"   : "110",
                            "ADM"  : "111"      }
        self.jumpCode = {   "null" : "000",
                            "JGT"  : "001",
                            "JEQ"  : "010",
                            "JGE"  : "011",
                            "JLT"  : "100",
                            "JNE"  : "101",
                            "JLE"  : "110",
                            "JMP"  : "111"      }

    def dest(self, destString):
        '''Returns the binary code of the dest mnemonic'''
        return self.destCode[destString]

    def comp(self, compString):
        '''Returns the binary code of the comp mnemonic'''
        newCompString = compString.replace("M", "A")    # dictionary is defined only for "A" in comp
        return self.compCode[newCompString]

    def jump(self, jumpString):
        '''Returns the binary code of the jump mnemonic'''
        return self.jumpCode[jumpString]