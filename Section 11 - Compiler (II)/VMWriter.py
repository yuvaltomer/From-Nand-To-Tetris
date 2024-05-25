class VMWriter:
    '''Emits VM commands into a file, using the VM command syntax'''
    
    def __init__(self, fileName):
        '''Creates a new file and prepares it for writing'''
        self.output = open(fileName.rpartition(".")[0] + ".vm", "w")

    def writePush(self, segment, index):
        '''Writes a VM push command'''
        self.output.write(f"push {segment} {index}\n")

    def writePop(self, segment, index):
        '''Writes a VM pop command'''
        self.output.write(f"pop {segment} {index}\n")
    
    def writeArithmetic(self, command):
        '''Writes a VM arithmetic command'''
        self.output.write(f"{command}\n")

    def writeLabel(self, label):
        '''Writes a VM label command'''
        self.output.write(f"label {label}\n")

    def writeGoto(self, label):
        '''Writes a VM goto command'''
        self.output.write(f"goto {label}\n")

    def writeIf(self, label):
        '''Writes a VM if-goto command'''
        self.output.write(f"if-goto {label}\n")

    def writeCall(self, name, nVars):
        '''Writes a VM call command'''
        self.output.write(f"call {name} {nVars}\n")

    def writeFunction(self, name, nVars):
        '''Writes a VM function command'''
        self.output.write(f"function {name} {nVars}\n")

    def writeReturn(self):
        '''Writes a VM return command'''
        self.output.write("return\n")

    def close(self):
        '''Closes the output file'''
        self.output.close()