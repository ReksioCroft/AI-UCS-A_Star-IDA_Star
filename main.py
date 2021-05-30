import time
from os import listdir
import copy
from queue import PriorityQueue


class StareGraph:
    nr_aflate_in_memorie = 0

    def __init__(self, matrix, robinet, canal, timp_gasire=0.0, val=0, tata=None, poz_modificat=None):
        """
        Aceste obiecte vor retine o stare din graf
        :param matrix: matricea unei stari, formate din o si # si bordata cu None, unde o e spatiu liber si # e obstacol
        :param robinet: pozitia robinetului in matrice (indexat de la 1)
        :param canal: pozitia canalului de scurgere din matrice, indexat de la 1
        :param timp_gasire: timpul in care a fost gasit
        :param val: ce cost s-a strans pana in acest punct in urma eliminarii obstacolelor
        :param tata: starea (tot de tip StareGraph) din care s-a generat aceasta stare sau None pt radacina
        :param poz_modificat: pozitia obstacolului care a fost eliminat din matricea tatalui sau None pt radacina
        """
        self.matrix = copy.deepcopy(matrix)
        self.robinet = robinet
        self.canal = canal
        self.tata = tata
        self.val = val
        self.poz_modificat = poz_modificat
        self.timp_gasire = timp_gasire
        self.succesori = None

    def __lt__(self, other):
        """
        O stare se considera mai mica decat alta, daca are costul la care s-a ajuns mai mic.
        Este necesara aceasta relatie pentru functionalitatea PriorityQueue
        :param other: Obiect de comparat
        :return:
        """
        return self.val < other.val

    def __eq__(self, o):
        """
        Doua stari se considera echivalente daca au aceeasi o matrice identica a obstacolelor, au robinetul si canalul pozitionate in aceleasi locuri
        si s-a ajuns la acelasi cost pentru generarea matricei.
        Cu alte cuvinte, pt doua drumuri in care s-au eliminat o succesiune de obstacole intr-o ordine DIFERITA, dar aceleasi, ajungandu-se la acelasi cost,
        se considera stari ehivalente (avand drumuri considerate echivalente, chiar daca obstacolele s-au eliminat intr-o ordine diferita)
        :param o: un obiect pt comparare
        :return: returneaza True daca cele doua stari sunt echivalente
        """
        if o.__class__ != self.__class__:
            return False
        else:
            return self.matrix == o.matrix and self.robinet == o.robinet and self.canal == o.canal and self.val == o.val

    @classmethod
    def calc_val_vecini(cls, matrix, poz):
        """
        :param matrix: matricea pe care se calculeaza
        :param poz: poztia din care se priveste
        :return: Pentru o matrice si o poztie data, se returneaza nr de vecini '#', adica costul eliminarii acestui obstacol

        """
        co = 0
        for i in [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]:
            if matrix[poz[0] + i[0]][poz[1] + i[1]] == '#':
                co += 1
        return co

    @classmethod
    def generare_succesori(cls, stare_curenta):
        """
        Aceasta classmethod genereaza succesorii unei stari o singura data, si ii retine in memorie pe toata durata de viata a programului,
        returnandu-i la urmatoarele apeluri, in loc sa ii regenereze.
        Se porneste cu fill din robinet si se umple toata portiunea, iar pentru fiecare obstacol intalnit pe conturul zonei libere din jurul robinetului,
        se genereaza cate o stare noua in care acel obstacol ar fi eliminat
        :param stare_curenta: stare pt care dorim succesorii
        :return: returneaza o lista cu succesorii unei stari date
        """

        if stare_curenta.succesori is None:
            l_succesori = []

            def fill_succesori(matrix, poz):
                if matrix[poz[0]][poz[1]] == '#':
                    m_aux = copy.deepcopy(stare_curenta.matrix)
                    m_aux[poz[0]][poz[1]] = 'o'
                    nod = StareGraph(matrix=m_aux, robinet=stare_curenta.robinet, canal=stare_curenta.canal,
                                     val=stare_curenta.val + StareGraph.calc_val_vecini(m_aux, poz),
                                     tata=stare_curenta, poz_modificat=poz, timp_gasire=time.time() - Graph.t0)
                    if nod not in l_succesori:
                        l_succesori.append(nod)
                elif matrix[poz[0]][poz[1]] == 'o':
                    matrix[poz[0]][poz[1]] = '*'
                    for i in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                        fill_succesori(matrix, (poz[0] + i[0], poz[1] + i[1]))

            fill_succesori(copy.deepcopy(stare_curenta.matrix), stare_curenta.robinet)
            stare_curenta.succesori = l_succesori
            cls.nr_aflate_in_memorie += len(l_succesori)
        return stare_curenta.succesori

    @classmethod
    def is_final_state(cls, state):
        """
        Aceasta functie creaza o copie a matricei din starea primita pe care o umple folosinf FILL, verificand astfel daca se poate ajunge la canal
        ul de scurgere, plecand din robinet
        :param state: primeste o stare
        :return: Intoarce True daca e stare finala, altfel False
        """
        matrix = copy.deepcopy(state.matrix)
        Graph.fill(matrix, state.robinet)
        if matrix[state.canal[0]][state.canal[1]] == '*':
            return True
        else:
            return False


class Graph:
    t0 = time.time()

    def __init__(self, fin, fout):
        """

        :param fin: fisierul de intrare de unde se citesc informatiile
        :param fout: fisierul de iesire in care se vor scrie informatiile
        Un obiect de tip graph retine starea initiala (radacina) din care se vor forma arborii specifici de catre fiecare algoritm
        Aceasta clasa dispune de 4 algoritmi: UCS, A*, A* optimizat, IDA*
        La instantierea unui nou obiect, se reseteaza contorul de noduri din memorie al clasei StareGraph
        """

        def initial_matrix():
            """
            Functie care imi genereaza matricea, citind elementele din fisierul de intrare
            Matricea va fi bordata cu None, iar elem efective cor fi indexate de la (1,1)
            :return: returneaza matricea generata
            """
            matrix = []
            for i in fin:
                if len(matrix) == 0:
                    matrix.append([None] * (len(i.strip()) + 2))
                matrix.append([None] + list(i.strip()) + [None])
            matrix.append([None] * len(matrix[0]))
            if robinet[0] < 1 or robinet[0] >= len(matrix) - 1:
                raise Exception("Input invalid: Pozitie linie robinet incorecta")
            elif robinet[1] < 1 or robinet[1] >= len(matrix[0]) - 1:
                raise Exception("Input invalid: Pozitie coloana robinet incorecta")
            elif canal[0] < 1 or canal[0] >= len(matrix) - 1:
                raise Exception("Input invalid: Pozitie linie canal incorecta")
            elif canal[1] < 1 or canal[1] >= len(matrix[0]) - 1:
                raise Exception("Input invalid: Pozitie coloana canal incorecta")
            elif matrix[robinet[0]][robinet[1]] != 'o':
                raise Exception("Input invalid: robinet astupat")
            elif matrix[canal[0]][canal[1]] != 'o':
                raise Exception("Input invalid: canal astupat")

            return matrix

        robinet = tuple([int(i) for i in fin.readline().split()])
        canal = tuple([int(i) for i in fin.readline().split()])
        self.stare0 = StareGraph(matrix=initial_matrix(), robinet=robinet, canal=canal)
        self.fout = fout
        StareGraph.nr_aflate_in_memorie = 0

    @classmethod
    def fill(cls, matrix, poz, ch0='o', ch='*'):
        """
        Metoda care umple o portiunea libera din matrice(inconjurata de obstacole)
        :param matrix: matricea de umplut
        :param poz: pozitia curenta ce se coloreaza, in apelul recursiv
        :param ch0: caracterul de modificat (by default, 'o')
        :param ch: noul caracter (by default, '*')
        :return:
        """
        if matrix[poz[0]][poz[1]] == ch0:
            matrix[poz[0]][poz[1]] = ch
            for i in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                Graph.fill(matrix, (poz[0] + i[0], poz[1] + i[1]), ch0, ch)

    @classmethod
    def calc_cost_till_end(cls, euristica, current_state):
        """
        Aceasta metoda returneaza cele 4 euristici posibile (dintre care 3 acceptabile)

        :param euristica: tipul euristicii
                          "banala" - intoarce costul pana in acest punct
                          "urmatorul_pas" se uita la copii acestei starii si intoarce valoare minima de construire
                          "peste_2_pasi" intoarce costul minim de construire al unui nepot
                          "distanta_manhattan_neadmisibila" intoarce costul de construire al starii curente + distanta manhattan pana la canal. Aceasta este neadmisibila
                          !Important atat "urmatorul_pas" cat si "peste_2_pasi" vor verifica doar copii (si nepotii) care nu sunt generati dintr-o stare finala,
                          altfel intorc costul de ajungere al starii finale pt un drum care trece prin starea curenta
        :param current_state: starea curenta pentru care se calculeaza
        :return:
        """
        if euristica == "banala" or StareGraph.is_final_state(current_state):
            return current_state.val
        elif euristica == "urmatorul_pas":
            l_succesori_euristica = StareGraph.generare_succesori(current_state)
            best_value = float('+inf')
            for i in l_succesori_euristica:
                if i.val < best_value:
                    best_value = i.val
            return best_value
        elif euristica == "peste_2_pasi":
            best_value = float('+inf')
            l_succesori_euristica = StareGraph.generare_succesori(current_state)
            for i in l_succesori_euristica:
                if StareGraph.is_final_state(i):
                    if i.val < best_value:
                        best_value = i.val
                else:
                    for j in StareGraph.generare_succesori(i):
                        if j.val < best_value:
                            best_value = j.val
            return best_value
        elif euristica == "distanta_manhattan_neadmisibila":
            if current_state.poz_modificat is not None:
                return current_state.val + abs(current_state.poz_modificat[0] - current_state.canal[0]) + abs(current_state.poz_modificat[1] - current_state.canal[1])
            else:
                return current_state.val
        else:
            raise Exception("Eurisitca necunoscuta")

    def afis_drum(self, state, co):
        """
        Primind o stare finala, parcurge recursiv drumul pana in tata, si apoi il afiseaza de la tata la fiu
        :param state: primeste o stare FINALA
        :param co: primeste initial o lista co=[0] in care se va incrementa indicele nodului din drum
        :return:
        """
        if state.tata is not None:
            self.afis_drum(state.tata, co)
        else:
            self.fout.write("Nr de noduri aflate in memorie dupa generarea acestei sol: {}\n".format(str(StareGraph.nr_aflate_in_memorie)))

        co[0] += 1
        self.fout.write(str(co[0]) + ') ')
        if state.poz_modificat is not None:
            self.fout.write("Eliminam obstacolul de pe linia " + str(state.poz_modificat[0]) + ", coloana " + str(state.poz_modificat[1]) + '\n')
        else:
            self.fout.write("Configuratie Initiala\n")
        m = copy.deepcopy(state.matrix)
        Graph.fill(m, state.robinet)
        for i in m[1:len(m) - 1]:  # excludem bordarea
            self.fout.write(str(i[1:len(i) - 1]) + '\n')
        self.fout.write("Lungime intermediara drum: {}\n".format(str(co[0])))
        self.fout.write("Cost actual: {}\n".format(str(state.val)))
        self.fout.write("Timp gasire: {}s\n".format(str(round(state.timp_gasire, 5))))
        self.fout.write('...........\n')

    def ucs(self, nr_solutii=1, timeout=60):
        """
        Calculeaza n drumuri, in ordinea costului, de la starea initiala pana intr-o stare finala(in care canalul e accesibil dinspre robinet)
        Se foloseste o coada de prioritati pt a determina ce nod urmeaza ca cost
        Starile finale gasite sunt retinute intr-o lista pt a nu afisa drumuri echivalente (in care se ajunge cu acelasi cost si cu o matrice a obstacolelor identica
        in starea finala, indiferent de ordinea de eliminare a obstacolelor)
        :param nr_solutii: nr solutii care se doreste sa fie intors
        :param timeout: timpul de functionare maxim al algoritmului
        :return: nu returneaza nimic, dar scrie in fisierul de iesire soltuiile
        """
        state = self.stare0
        Graph.t0 = time.time()
        pq = PriorityQueue()
        pq.put((0, state))
        co_solutii = 0
        stari_finale = []
        self.fout.write("===========\n")

        while not pq.empty():
            _, state = pq.get()
            if StareGraph.is_final_state(state):
                if state not in stari_finale:
                    co_solutii += 1
                    self.fout.write("\n-----------\n")
                    self.fout.write("UCS {}:\n".format(co_solutii))
                    self.afis_drum(state, [0])
                    stari_finale.append(state)
                if co_solutii < nr_solutii:
                    continue
                else:
                    break
            if time.time() - Graph.t0 > timeout:
                self.fout.write("Timeout...\n")
                break
            for nextState in StareGraph.generare_succesori(state):
                pq.put((nextState.val, nextState))

        self.fout.write("===========\n")

    def a_star_optimizat(self, euristica="peste_2_pasi", timeout=60):
        """
        Calculeaza drumul optim dpdv al costului, de la starea initiala pana intr-o stare finala(in care canalul e accesibil dinspre robinet)
        Se foloseste o coada de prioritati pt a determina ce nod urmeaza, folosind euristica specificata (cost+euristica, val intoarsa de alta metoda)
        Starile finale gasite sunt retinute intr-o lista pt a nu afisa drumuri echivalente (in care se ajunge cu acelasi cost si cu o matrice a obstacolelor identica
        in starea finala, indiferent de ordinea de eliminare a obstacolelor).
        Euristici admisibile posibile: "banala", "urmatorul_pas", "peste_2_pasi"
        Listele opened si closed ne asigura ca nu expandam noduri prin care am trecut deja
        :param timeout: timpul de functionare maxim al algoritmului
        :return: nu returneaza nimic, dar scrie in fisierul de iesire soltuiile
        """
        self.fout.write("===========\n")
        state = self.stare0
        Graph.t0 = time.time()
        q = PriorityQueue()
        q.put((Graph.calc_cost_till_end(euristica=euristica, current_state=state), state))
        closed = []
        opened = [state]
        while not q.empty():
            _, state = q.get()
            opened.remove(state)
            closed.append(state)
            if StareGraph.is_final_state(state):  # daca e stare finala, o aifsez si ma opresc
                self.fout.write("\n-----------\n")
                self.fout.write("AStar Optim (euristica {}):\n".format(euristica))
                self.afis_drum(state, [0])
                break
            if time.time() - Graph.t0 > timeout:
                self.fout.write("Timeout...\n")
                break
            for nextState in StareGraph.generare_succesori(state):  # altfel, parcurg succesorii
                if nextState not in closed and nextState not in opened:
                    q.put((Graph.calc_cost_till_end(euristica=euristica, current_state=nextState), nextState))  # am verificat deja sa nu se repete in generare_succesori
                    opened.append(nextState)  # pt a nu repeta

        self.fout.write("===========\n...........\n")

    def a_star(self, euristica="urmatorul_pas", nr_solutii=1, timeout=60):
        """
        Calculeaza n drumuri, in ordinea costului, de la starea initiala pana intr-o stare finala(in care canalul e accesibil dinspre robinet)
        Se foloseste o coada de prioritati pt a determina ce nod urmeaza, folosind euristica specificata (cost+euristica, val intoarsa de alta metoda)
        Starile finale gasite sunt retinute intr-o lista pt a nu afisa drumuri echivalente (in care se ajunge cu acelasi cost si cu o matrice a obstacolelor identica
        in starea finala, indiferent de ordinea de eliminare a obstacolelor).
        Euristici admisibile posibile: "banala", "urmatorul_pas", "peste_2_pasi"
        :param nr_solutii: nr solutii care se doreste sa fie intors
        :param timeout: timpul de functionare maxim al algoritmului
        :return: nu returneaza nimic, dar scrie in fisierul de iesire soltuiile
        """
        self.fout.write("===========\n")
        state = self.stare0
        q = PriorityQueue()
        co_solutii = 0
        Graph.t0 = time.time()
        stari_finale = []
        q.put((Graph.calc_cost_till_end(euristica=euristica, current_state=state), state))
        while not q.empty():
            _, state = q.get()
            if StareGraph.is_final_state(state):  # daca e stare finala, ma opresc
                if state not in stari_finale:
                    stari_finale.append(state)
                    co_solutii += 1
                    self.fout.write("\n-----------\n")
                    self.fout.write("AStar {} (euristica {}):\n".format(co_solutii, euristica))
                    self.afis_drum(state, [0])
                if co_solutii < nr_solutii:
                    continue
                else:
                    break
            if time.time() - Graph.t0 > timeout:
                self.fout.write("Timeout...\n")
                break
            for nextState in StareGraph.generare_succesori(state):  # altfel, parcurg succesorii
                q.put((Graph.calc_cost_till_end(euristica=euristica, current_state=nextState), nextState))  # am verificat deja sa nu se repete in generare_succesori

        self.fout.write("===========\n...........\n")

    def ida_star(self, euristica="banala", nr_solutii=1, timeout=60):
        """
        Calculeaza n drumuri, in ordinea costului, de la starea initiala pana intr-o stare finala(in care canalul e accesibil dinspre robinet)
        Se foloseste o parcurgere recursiva ce se reapeleaza pe masura ce limita de recursie este incrementata de rezultatul intors de euristica aleasa
        Starile finale gasite sunt retinute intr-o lista pt a nu afisa drumuri echivalente (in care se ajunge cu acelasi cost si cu o matrice a obstacolelor identica
        in starea finala, indiferent de ordinea de eliminare a obstacolelor).
        Euristici admisibile posibile: "banala", "urmatorul_pas", "peste_2_pasi"
        :param nr_solutii: nr solutii care se doreste sa fie intors
        :param timeout: timpul de functionare maxim al algoritmului
        :return: nu returneaza nimic, dar scrie in fisierul de iesire soltuiile
      """

        def recursie_ida_star(cost_euristic_stare_curenta, stare):
            """
            Parcurgere recursiva pana la limita de recursie, care asiguira ca se gasesc in ordine corecta a costurilor toate drumurile
            de la starea initiala la cea finala. Daca starea curenta nu e stare finala, se reapeleaza recursiv succesorii ei,
            si se retine costul euristic urmator(minim)
            :param cost_euristic_stare_curenta: costul de constructie+aproximatia
            :param stare: nodul ce urmeaza a fi expandat
            :return: returneaza noua limita de recursie si afiseaza starile finala pe masura ce sunt gasite
            """
            if cost_euristic_stare_curenta > limita_cost_recursie:
                return cost_euristic_stare_curenta
            elif StareGraph.is_final_state(stare):
                if stare not in stari_finale:
                    stari_finale.append(stare)
                    self.fout.write("\n-----------\n")
                    self.fout.write("IDA Star {} (euristica {}):\n".format(len(stari_finale), euristica))
                    self.fout.write("Nr calculate dupa aceasta solutie: {}\n".format(str(recursie_ida_star.co_noduri_calculate)))
                    self.afis_drum(state=stare, co=[0])
                return float('+inf')
            elif len(stari_finale) < nr_solutii and time.time() - Graph.t0 <= timeout:
                lista_succesori = StareGraph.generare_succesori(stare)
                recursie_ida_star.co_noduri_calculate += len(lista_succesori)
                best_cost_recursie = float('+inf')
                for stare_urmatoare in lista_succesori:
                    if len(stari_finale) >= nr_solutii or time.time() - Graph.t0 > timeout:
                        return cost_euristic_stare_curenta
                    cost_nou_recursie = recursie_ida_star(Graph.calc_cost_till_end(current_state=stare_urmatoare, euristica=euristica), stare_urmatoare)
                    if cost_nou_recursie < best_cost_recursie:
                        best_cost_recursie = cost_nou_recursie
                return best_cost_recursie
            else:
                return cost_euristic_stare_curenta

        self.fout.write("===========\n")
        Graph.t0 = time.time()
        stari_finale = []
        cost_stare0 = Graph.calc_cost_till_end(euristica=euristica, current_state=self.stare0)
        limita_cost_recursie = cost_stare0
        recursie_ida_star.co_noduri_calculate = 0

        if StareGraph.is_final_state(state=self.stare0):
            recursie_ida_star(cost_stare0, self.stare0)
        else:
            while len(stari_finale) < nr_solutii:
                limita_cost_recursie = recursie_ida_star(cost_stare0, self.stare0)
                if time.time() - Graph.t0 > timeout:
                    self.fout.write("Timeout...\n")
                    break


if __name__ == "__main__":
    """
    Se introduc caile catre direcotarele de intrare si iesire, nr de solutii dorit (pt algoritmii care intorc mai multe solutii)
    si timpul maxim de viata al unui algoritm. Apoi se apeleaza pt fiecare fisier de intrare toti algoritmii
    Intrucat se apeleaza unul dupa celalalt, fiecare nod generat de un algoritm va fi disponibil in memorie si pentru urmatorul algoritm 
    ce va fi rulat. Dupa fiecare fisier, se incearca stergerea obiectelor folosind operatorul del
    """
    inputPath = input("cale folder fișier intrare (./folder/): ")
    outputPath = input("cale folder fișier ieșire (./folder/): ")
    nSol = int(input("Număr soluții căutate: "))
    timeout = int(input("Timeout: "))
    for inputFile in listdir(inputPath):
        try:
            print(inputPath + inputFile)

            fin = open(inputPath + inputFile, 'r')
            fout = open(outputPath + inputFile + '.out', 'w')
            graph = Graph(fin, fout)

            print("ucs")
            graph.ucs(nr_solutii=nSol, timeout=timeout)

            print("a star")
            print("banala")
            graph.a_star(euristica="banala", nr_solutii=nSol, timeout=timeout)
            print("urmatorul_pas")
            graph.a_star(euristica="urmatorul_pas", nr_solutii=nSol, timeout=timeout)
            print("peste 2 pasi")
            graph.a_star(euristica="peste_2_pasi", nr_solutii=nSol, timeout=timeout)
            print("neadmisibila manhattan")
            graph.a_star(euristica="distanta_manhattan_neadmisibila", nr_solutii=nSol, timeout=timeout)

            print("a star optim")
            print("banala")
            graph.a_star_optimizat(euristica="banala", timeout=timeout)
            print("urmatorul_pas")
            graph.a_star_optimizat(euristica="urmatorul_pas", timeout=timeout)
            print("peste 2 pasi")
            graph.a_star_optimizat(euristica="peste_2_pasi", timeout=timeout)
            print("neadmisibila manhattan")
            graph.a_star_optimizat(euristica="distanta_manhattan_neadmisibila", timeout=timeout)

            print("ida star")
            print("banala")
            graph.ida_star(euristica="banala", timeout=timeout, nr_solutii=nSol)
            print("urmatorul_pas")
            graph.ida_star(euristica="urmatorul_pas", timeout=timeout, nr_solutii=nSol)
            print("peste 2 pasi")
            graph.ida_star(euristica="peste_2_pasi", timeout=timeout)
            print("neadmisibila manhattan")
            graph.ida_star(euristica="distanta_manhattan_neadmisibila", nr_solutii=nSol, timeout=timeout)

            del graph

            fin.close()
            fout.close()
        except Exception as e:
            print(e)
