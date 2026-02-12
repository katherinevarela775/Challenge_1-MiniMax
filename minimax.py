import random, copy, os, time

class Laberinto:
    def __init__(self, tamano):
        # Unificamos el nombre a 'tamano' para evitar el TypeError
        self.tamano = tamano
        self.posicion_gato = [0, 1]
        self.posicion_raton = [tamano - 1, tamano - 1]
        self.posicion_salida = [0, 0]
        self.lista_quesos = []
        self.lista_paredes = []
        self.memoria_raton = [] 
        
        while True:
            self.lista_paredes = []
            zonas_restringidas = [[0,0], [0,1], [1,0], [1,1], self.posicion_gato, self.posicion_raton]
            # Densidad de paredes moderada para permitir la persecución
            for _ in range((tamano * tamano) // 7):
                pared_tentativa = [random.randint(0, tamano - 1), random.randint(0, tamano - 1)]
                if pared_tentativa not in zonas_restringidas and pared_tentativa not in self.lista_paredes:
                    self.lista_paredes.append(pared_tentativa)
            
            if self.existe_camino_real(self.posicion_raton, self.posicion_salida):
                self.lista_quesos = []
                while len(self.lista_quesos) < 3:
                    q = [random.randint(0, tamano - 1), random.randint(0, tamano - 1)]
                    if q not in self.lista_paredes and q not in zonas_restringidas and q not in self.lista_quesos:
                        self.lista_quesos.append(q)
                break

    def existe_camino_real(self, inicio, fin):
        cola = [inicio]; visitados = [inicio]
        for pos in cola:
            if pos == fin: return True
            for vecino in self.obtener_movimientos_legales(pos, [], es_gato=False):
                if vecino not in visitados:
                    visitados.append(vecino); cola.append(vecino)
        return False

    def obtener_movimientos_legales(self, posicion_actual, posicion_oponente, es_gato=True):
        movs = []
        for df, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nf, nc = posicion_actual[0]+df, posicion_actual[1]+dc
            if 0 <= nf < self.tamano and 0 <= nc < self.tamano:
                punto = [nf, nc]
                if punto not in self.lista_paredes:
                    if not es_gato and punto == posicion_oponente: continue
                    movs.append(punto)
        return movs

    def mostrar_tablero(self, turno, modo_g, modo_r):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Calculamos el ancho del laberinto (cada celda ocupa 3 espacios: emoji + espacio)
        # Sumamos 2 para los bordes laterales
        ancho_laberinto = (self.tamano * 3)
        # La línea de texto informativa también tiene un ancho
        texto_info = f" TURNO: {turno:2}  | GATO: {modo_g:8} | RATÓN: {modo_r:8} "
        
        # El marco debe ser tan ancho como el mayor de los dos
        ancho_final = max(ancho_laberinto, len(texto_info))
        
        print(f"╔{'═' * ancho_final}╗")
        print(f"║{texto_info.center(ancho_final)}║")
        print(f"╚{'═' * ancho_final}╝")
        
        for f in range(self.tamano):
            fila = " " # Un pequeño espacio inicial para centrar visualmente
            for c in range(self.tamano):
                p = [f, c]
                if p == self.posicion_gato: fila += "🐱 "
                elif p == self.posicion_raton: fila += "🐭 "
                elif p == self.posicion_salida: fila += "🚪 "
                elif p in self.lista_quesos: fila += "🧀 "
                elif p in self.lista_paredes: fila += "⬛ "
                else: fila += "⬜ "
            print(fila)

    def evaluar_estado(self, es_raton):
        d_gr = abs(self.posicion_gato[0]-self.posicion_raton[0]) + abs(self.posicion_gato[1]-self.posicion_raton[1])
        d_rs = abs(self.posicion_raton[0]-self.posicion_salida[0]) + abs(self.posicion_raton[1]-self.posicion_salida[1])
        
        if es_raton:
            penalizacion = self.memoria_raton.count(self.posicion_raton) * 50
            return (d_gr * 5) - (d_rs * 60) - penalizacion + random.randint(0, 5)
        else:
            # PRIORIDAD MÁXIMA DEL GATO: Atrapar al ratón (peso -200)
            return -(d_gr * 200) + random.randint(0, 5)

    def minimax(self, profundidad, es_max):
        if self.posicion_gato == self.posicion_raton: return -20000
        if self.posicion_raton == self.posicion_salida: return 20000
        if profundidad == 0:
            return self.evaluar_estado(es_max)

        mejor = float('-inf') if es_max else float('inf')
        yo = self.posicion_raton if es_max else self.posicion_gato
        rival = self.posicion_gato if es_max else self.posicion_raton
        
        for m in self.obtener_movimientos_legales(yo, rival, es_gato=not es_max):
            original = list(yo)
            if es_max: self.posicion_raton = m
            else: self.posicion_gato = m
            
            val = self.minimax(profundidad - 1, not es_max)
            
            if es_max: mejor = max(mejor, val)
            else: mejor = min(mejor, val)
            
            if es_max: self.posicion_raton = original
            else: self.posicion_gato = original
        return mejor

    def mover_ia(self, es_raton):
        # El gato tiene una visión más profunda para ser más letal
        prof_raton, prof_gato = 3, 4
        yo = self.posicion_raton if es_raton else self.posicion_gato
        rival = self.posicion_gato if es_raton else self.posicion_raton
        mejor_m, mejor_p = yo, (float('-inf') if es_raton else float('inf'))
        
        prof = prof_raton if es_raton else prof_gato
        movs = self.obtener_movimientos_legales(yo, rival, es_gato=not es_raton)
        
        if not movs: return

        for m in movs:
            original = list(yo)
            if es_raton: self.posicion_raton = m
            else: self.posicion_gato = m
            p = self.minimax(prof, not es_raton)
            if (es_raton and p > mejor_p) or (not es_raton and p < mejor_p):
                mejor_p, mejor_m = p, m
            if es_raton: self.posicion_raton = original
            else: self.posicion_gato = original
            
        if es_raton:
            self.posicion_raton = mejor_m
            self.memoria_raton.append(list(mejor_m))
            if len(self.memoria_raton) > 5: self.memoria_raton.pop(0)
            if self.posicion_raton in self.lista_quesos: self.lista_quesos.remove(self.posicion_raton)
        else:
            self.posicion_gato = mejor_m

def manual(juego, pos, rival, es_g):
    while True:
        muda = input(f"\n Mover {'GATO' if es_g else 'RATÓN'} (W/A/S/D) + Enter: ").lower()
        d = {'w':(-1,0), 's':(1,0), 'a':(0,-1), 'd':(0,1)}
        if muda in d:
            n = [pos[0]+d[muda][0], pos[1]+d[muda][1]]
            if n in juego.obtener_movimientos_legales(pos, rival, es_g): return n
        print(" Movimiento no válido.")

def jugar():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("        --- CAT & MOUSE: THE CHASE ---")
    
    # 1. Preguntamos el tamaño del tablero
    try:
        entrada_tam = input("\n1. Ingresa el tamaño del tablero (ej. 10): ")
        tam = int(entrada_tam) if entrada_tam.isdigit() else 10
        if tam < 5: tam = 5
    except:
        tam = 10

    # 2. Preguntamos el modo de juego
    print("\n2. Selecciona el modo de juego:")
    print("   [1] Jugar como RATÓN")
    print("   [2] Jugar como GATO")
    print("   [3] Modo ESPECTADOR")
    op = input("\nSelección (1, 2 o 3): ")
    
    # 3. Creamos el objeto Laberinto con el nombre de argumento correcto
    j = Laberinto(tamano=tam)
    historial_estados = {}
    
    for t in range(1, 100):
        # Detección de bucles por estado combinado
        estado_actual = (tuple(j.posicion_gato), tuple(j.posicion_raton))
        historial_estados[estado_actual] = historial_estados.get(estado_actual, 0) + 1
        
        if historial_estados[estado_actual] >= 6:
            j.mostrar_tablero(t, "EMPATE", "EMPATE")
            print(f"\n🤝 EMPATE: Se detectó un patrón repetitivo en {estado_actual}."); return

        modo_raton = "PLAYER" if op == "1" else "AI"
        modo_gato = "PLAYER" if op == "2" else "AI"
        j.mostrar_tablero(t, modo_gato, modo_raton)

        # Turno del Ratón
        if op == "1": j.posicion_raton = manual(j, j.posicion_raton, j.posicion_gato, False)
        else: j.mover_ia(True)
        
        if j.posicion_raton == j.posicion_salida:
            j.mostrar_tablero(t, modo_gato, modo_raton); print("🧀 ¡VICTORIA! El ratón escapó."); return
        if j.posicion_gato == j.posicion_raton:
            j.mostrar_tablero(t, modo_gato, modo_raton); print("💀 ¡GAME OVER! El gato atrapó al ratón."); return

        # Turno del Gato
        j.mostrar_tablero(t, modo_gato, modo_raton)
        if op == "2": j.posicion_gato = manual(j, j.posicion_gato, j.posicion_raton, True)
        else: 
            if op == "3": time.sleep(0.4) # Velocidad del espectador
            j.mover_ia(False)

        if j.posicion_gato == j.posicion_raton:
            j.mostrar_tablero(t, modo_gato, modo_raton); print("💀 ¡GAME OVER! El gato atrapó al ratón."); return

    print("\n🤝 EMPATE: Se alcanzó el límite máximo de turnos.")

if __name__ == "__main__":
    jugar()