from os import listdir
import copy
from queue import PriorityQueue


class StareGraph:
    euristica = "acceptabila"

    def __init__(self, matrix, val=0, tata=None, msg="\n"):
        self.matrix = matrix
        self.tata = tata
        self.val = val
        self.msg = msg

    def __lt__(self, other):
        return self.val < other.val


class Graph:
    def __init__(self, fin, fout):
        def initialMatrix():
            matrix = []
            for i in fin:  # vom borda matricea cu None
                if len(matrix) == 0:
                    matrix.append([None] * (len(i.strip()) + 2))
                matrix.append([None] + list(i.strip()) + [None])
            matrix.append([None] * len(matrix[0]))
            return matrix

        self.robinet = tuple([int(i) for i in fin.readline().split()])  # matrice indexata de la 1 pt bordare
        self.canal = tuple([int(i) for i in fin.readline().split()])
        self.stare0 = StareGraph(initialMatrix())  # construim starea initiala
        self.listaSuccesori = [self.stare0]
        self.fout = fout

    def calcValVecini(self, matrix, poz):
        co = 0
        for i in [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]:
            if matrix[poz[0] + i[0]][poz[1] + i[1]] == '#':
                co += 1
        return co

    def generareSuccesori(self, stareCurenta):
        l = []

        def fillSuccesori(matrix, poz):
            if matrix[poz[0]][poz[1]] == '#':
                mAux = copy.deepcopy(stareCurenta.matrix)
                mAux[poz[0]][poz[1]] = 'o'
                if mAux not in self.listaSuccesori:
                    nod = StareGraph(mAux, stareCurenta.val + self.calcValVecini(matrix, poz), stareCurenta, "Eliminam obstacolul de pe linia " + str(poz[0]) + ", coloana " + str(poz[1]) + '\n')
                    if nod not in l:
                        l.append(nod)
            elif matrix[poz[0]][poz[1]] == 'o':
                matrix[poz[0]][poz[1]] = '*'
                for i in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                    fillSuccesori(matrix, (poz[0] + i[0], poz[1] + i[1]))

        fillSuccesori(copy.deepcopy(stareCurenta.matrix), self.robinet)
        self.listaSuccesori.extend(l)
        return l

    @staticmethod
    def fill(matrix, poz, ch0='o', ch='*'):
        if matrix[poz[0]][poz[1]] == ch0:
            matrix[poz[0]][poz[1]] = ch
            for i in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                Graph.fill(matrix, (poz[0] + i[0], poz[1] + i[1]), ch0, ch)

    def isFinalState(self, state):
        matrix = copy.deepcopy(state.matrix)
        Graph.fill(matrix, self.robinet)
        if matrix[self.canal[0]][self.canal[1]] == '*':
            return True
        else:
            return False

    def afisDrum(self, state, co):
        if state.tata is not None:
            self.afisDrum(state.tata, co)
        co[0] += 1
        self.fout.write(str(co[0]) + ') ' + state.msg)
        m = copy.deepcopy(state.matrix)
        Graph.fill(m, self.robinet)
        for i in m[1:len(m) - 1]:
            self.fout.write(str(i[1:len(i) - 1]) + '\n')
        self.fout.write('...........\n')

    def UCS(self):
        state = self.stare0
        self.listaSuccesori = [state]
        pq = PriorityQueue()
        pq.put(state)

        while not pq.empty():
            state = pq.get()
            if self.isFinalState(state):  # daca e stare finala, ma opresc
                break
            for nextState in self.generareSuccesori(state):  # altfel, parcurg succesorii
                pq.put(nextState)  # am verificat deja sa nu se repete in generareSuccesori
                self.listaSuccesori.append(nextState.matrix)  # pt a nu repeta

        self.fout.write("UCS:\n")
        self.afisDrum(state, [0])
        self.fout.write("===========\n...........\n")

    def AStar(self, euristica="admisibila"):
        state = self.stare0

        opened = [state]
        pq = PriorityQueue()
        pq.put(state)


inputPath = input("cale folder fisier intrare: ")
outputPath = input("cale folder fisier iesire: ")
nSol = input("Numar solutii cautate: ")
timeout = input("Timeout: ")
for inputFile in listdir(inputPath):
    fin = open(inputPath + inputFile, 'r')
    fout = open(outputPath + inputFile + '.out', 'w')
    graph = Graph(fin, fout)
    graph.UCS()
    fin.close()
    fout.close()
