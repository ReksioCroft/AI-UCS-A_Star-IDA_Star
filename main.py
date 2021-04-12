inputPath = input("cale folder fisier intrare: ")
outputPath = input("cale folder fisier iesire: ")
nSol = input("Numar solutii cautate: ")
timeout = input("Timeout: ")
for inputFile in inputPath:
    fin = open(inputFile, 'r')
    fin.close()
