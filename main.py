import time
from os import listdir
import copy
from queue import PriorityQueue


class StareGraph:
    def __init__(self, matrix, robinet, canal, val=0, tata=None, msg="\n"):
        self.matrix = copy.deepcopy(matrix)
        self.robinet = robinet
        self.canal = canal
        self.tata = tata
        self.val = val
        self.msg = msg

    def __lt__(self, other):
        return self.val < other.val

    def __eq__(self, o):
        if o.__class__ != self.__class__:
            return False
        else:
            return self.matrix == o.matrix and self.robinet == o.robinet and self.canal == o.canal and self.val == o.val

    @classmethod
    def calc_val_vecini(cls, matrix, poz):
        co = 0
        for i in [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]:
            if matrix[poz[0] + i[0]][poz[1] + i[1]] == '#':
                co += 1
        return co

    @classmethod
    def generare_succesori(cls, stare_curenta):
        l_succesori = []

        def fill_succesori(matrix, poz):
            if matrix[poz[0]][poz[1]] == '#':
                m_aux = copy.deepcopy(stare_curenta.matrix)
                m_aux[poz[0]][poz[1]] = 'o'
                nod = StareGraph(matrix=m_aux, robinet=stare_curenta.robinet, canal=stare_curenta.canal, val=stare_curenta.val + StareGraph.calc_val_vecini(matrix, poz), tata=stare_curenta, msg="Eliminam obstacolul de pe linia " + str(poz[0]) + ", coloana " + str(poz[1]) + '\n')
                if nod not in l_succesori:
                    l_succesori.append(nod)
            elif matrix[poz[0]][poz[1]] == 'o':
                matrix[poz[0]][poz[1]] = '*'
                for i in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                    fill_succesori(matrix, (poz[0] + i[0], poz[1] + i[1]))

        fill_succesori(copy.deepcopy(stare_curenta.matrix), stare_curenta.robinet)
        return l_succesori

    @classmethod
    def is_final_state(cls, state):
        matrix = copy.deepcopy(state.matrix)
        Graph.fill(matrix, state.robinet)
        if matrix[state.canal[0]][state.canal[1]] == '*':
            return True
        else:
            return False


class Graph:
    def __init__(self, fin, fout):
        def initial_matrix():
            matrix = []
            for i in fin:  # vom borda matricea cu None
                if len(matrix) == 0:
                    matrix.append([None] * (len(i.strip()) + 2))
                matrix.append([None] + list(i.strip()) + [None])
            matrix.append([None] * len(matrix[0]))
            if matrix[robinet[0]][robinet[1]] != 'o':
                raise Exception("Input invalid: robinet astupat")
            elif matrix[canal[0]][canal[1]] != 'o':
                raise Exception("Input invalid: canal astupat")

            return matrix

        robinet = tuple([int(i) for i in fin.readline().split()])  # matrice indexata de la 1 pt bordare
        canal = tuple([int(i) for i in fin.readline().split()])
        self.stare0 = StareGraph(matrix=initial_matrix(), robinet=robinet, canal=canal, msg="Configuratie Initiala\n")  # construim starea inițială
        self.fout = fout

    @classmethod
    def fill(cls, matrix, poz, ch0='o', ch='*'):
        if matrix[poz[0]][poz[1]] == ch0:
            matrix[poz[0]][poz[1]] = ch
            for i in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                Graph.fill(matrix, (poz[0] + i[0], poz[1] + i[1]), ch0, ch)

    @classmethod
    def calc_cost_till_end(cls, euristica, current_state):
        if euristica == "banala" or StareGraph.is_final_state(state=current_state):
            return current_state.val
        elif euristica == "urmatorul_pas":
            l_succesori_euristica = StareGraph.generare_succesori(current_state)
            best_value = l_succesori_euristica[0].val
            for i in l_succesori_euristica:
                if i.val < best_value:
                    best_value = i.val
            return current_state.val + best_value
        elif euristica == "peste_2_pasi":
            best_value = None
            l_succesori_euristica = StareGraph.generare_succesori(current_state)
            for i in l_succesori_euristica:
                if StareGraph.is_final_state(i):
                    if best_value is None or i.val < best_value:
                        best_value = i.val
                else:
                    for j in StareGraph.generare_succesori(i):
                        if best_value is None or j.val < best_value:
                            best_value = j.val
            return best_value

        else:
            raise Exception("Eurisitca necunoscuta")

    def afis_drum(self, state, co):
        if state.tata is not None:
            self.afis_drum(state.tata, co)
        co[0] += 1
        self.fout.write(str(co[0]) + ') ' + state.msg)
        m = copy.deepcopy(state.matrix)
        Graph.fill(m, state.robinet)
        for i in m[1:len(m) - 1]:  # excludem bordarea
            self.fout.write(str(i[1:len(i) - 1]) + '\n')
        self.fout.write('...........\n')

    def ucs(self, nr_solutii=1, timeout=60):
        state = self.stare0
        t0 = time.time()
        pq = PriorityQueue()
        pq.put((0, state))
        co_solutii = 0
        self.fout.write("===========\n")

        while not pq.empty():
            _, state = pq.get()
            if StareGraph.is_final_state(state):  # daca e stare finala, ma opresc
                co_solutii += 1
                self.fout.write("...........\nUCS {}:\n".format(co_solutii))
                self.afis_drum(state, [0])
                if co_solutii < nr_solutii:
                    continue
                else:
                    break
            if time.time() - t0 > timeout:
                self.fout.write("Timeout...\n")
                break
            for nextState in StareGraph.generare_succesori(state):  # altfel, parcurg succesorii
                pq.put((nextState.val, nextState))  # am verificat deja sa nu se repete in generareSuccesori

        self.fout.write("===========\n")

    def a_star_optimizat(self, euristica="peste_2_pasi", timeout=60):
        self.fout.write("===========\n")
        state = self.stare0
        t0 = time.time()
        q = PriorityQueue()
        q.put((Graph.calc_cost_till_end(euristica=euristica, current_state=state), state))
        closed = []
        opened = [state]
        while not q.empty():
            _, state = q.get()
            opened.remove(state)
            closed.append(state)
            if StareGraph.is_final_state(state):  # daca e stare finala, o aifsez si ma opresc
                self.fout.write("AStar Optim (euristica {}):\n".format(euristica))
                self.afis_drum(state, [0])
                break
            if time.time() - t0 > timeout:
                self.fout.write("Timeout...\n")
                break
            for nextState in StareGraph.generare_succesori(state):  # altfel, parcurg succesorii
                if nextState not in closed and nextState not in opened:
                    q.put((Graph.calc_cost_till_end(euristica=euristica, current_state=nextState), nextState))  # am verificat deja sa nu se repete in generare_succesori
                    opened.append(nextState)  # pt a nu repeta

        self.fout.write("===========\n...........\n")

    def a_star(self, euristica="urmatorul_pas", nr_solutii=1, timeout=60):
        self.fout.write("===========\n")
        state = self.stare0
        q = PriorityQueue()
        co_solutii = 0
        t0 = time.time()
        q.put((Graph.calc_cost_till_end(euristica=euristica, current_state=state), state))
        while not q.empty():
            _, state = q.get()
            if StareGraph.is_final_state(state):  # daca e stare finala, ma opresc
                co_solutii += 1
                self.fout.write("AStar {} (euristica {}):\n".format(co_solutii, euristica))
                self.afis_drum(state, [0])
                if co_solutii < nr_solutii:
                    continue
                else:
                    break
            if time.time() - t0 > timeout:
                self.fout.write("Timeout...\n")
                break
            for nextState in StareGraph.generare_succesori(state):  # altfel, parcurg succesorii
                q.put((Graph.calc_cost_till_end(euristica=euristica, current_state=nextState), nextState))  # am verificat deja sa nu se repete in generare_succesori

        self.fout.write("===========\n...........\n")


if __name__ == "__main__":
    inputPath = input("cale folder fișier intrare (./folder/): ")
    outputPath = input("cale folder fișier ieșire (./folder/): ")
    nSol = int(input("Număr soluții căutate: "))
    timeout = int(input("Timeout: "))
    for inputFile in listdir(inputPath):
        fin = open(inputPath + inputFile, 'r')
        fout = open(outputPath + inputFile + '.out', 'w')
        graph = Graph(fin, fout)

        print("ucs")
        graph.ucs(nr_solutii=nSol, timeout=timeout)

        print("a star")
        graph.a_star(euristica="banala", nr_solutii=nSol, timeout=timeout)
        print()
        graph.a_star(euristica="urmatorul_pas", nr_solutii=nSol, timeout=timeout)
        print()
        graph.a_star(euristica="peste_2_pasi", nr_solutii=nSol, timeout=timeout)

        print("a star optim")
        graph.a_star_optimizat(euristica="banala", timeout=timeout)
        print()
        graph.a_star_optimizat(euristica="urmatorul_pas", timeout=timeout)
        print()
        graph.a_star_optimizat(euristica="peste_2_pasi", timeout=timeout)

        fin.close()
        fout.close()
