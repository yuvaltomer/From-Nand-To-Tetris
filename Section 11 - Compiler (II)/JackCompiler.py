import sys
import os
import CompilationEngine as Ce

class JackAnalyzer:
    '''Creates a CompilationEngine object from the input file and calls compileClass to start the compilation'''

    def run(inputPath):
        '''Determines wheter the input path is a file or a directiory and creates VM file/s accordingly'''

        # If the input is a directory, compile each .jack file in it
        if os.path.isdir(inputPath):
            for file in os.listdir(inputPath):
                if file.endswith(".jack"):
                    inputFile = os.path.join(inputPath, file)
                    compilationEngine = Ce.CompilationEngine(inputFile)
                    compilationEngine.compileClass()

        else:
            compilationEngine = Ce.CompilationEngine(inputPath)
            compilationEngine.compileClass()


    if __name__ == "__main__":
        run(sys.argv[1])
        string = "   "