import random, copy, os, time

class Laberinto:
    # Cambiamos 'dimension' por 'tamano' para que coincida con la llamada
    def __init__(self, tamano):
        self.tamano = tamano
        self.posicion_gato = [0, 1]
        self.posicion_raton = [tamano - 1, tamano - 1]
        self.posicion_salida = [0, 0]
        
        self.lista_quesos = []
        self.lista_paredes = []
        
        # Generación del mapa
        while True:
            self.lista_paredes = []
            zonas_restringidas = [[0,0], [0,1], [1,0], [1,1], self.posicion_gato, self.posicion_raton]
            for _ in range((tamano * tamano) // 4):
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
        print(f"╔═════════════════════════════════════════════════╗")
        print(f"║ TURNO: {turno:2}  | GATO: {modo_g:8} | RATÓN: {modo_r:8} ║")
        print(f"╚═════════════════════════════════════════════════╝")
        for f in range(self.tamano):
            fila = ""
            for c in range(self.tamano):
                p = [f, c]
                if p == self.posicion_gato: fila += "🐱 "
                elif p == self.posicion_raton: fila += "🐭 "
                elif p == self.posicion_salida: fila += "🚪 "
                elif p in self.lista_quesos: fila += "🧀 "
                elif p in self.lista_paredes: fila += "⬛ "
                else: fila += "⬜ "
            print(fila)

    def minimax(self, profundidad, es_max):
        if self.posicion_gato == self.posicion_raton: return -5000
        if self.posicion_raton == self.posicion_salida: return 5000
        if profundidad == 0:
            d_gr = abs(self.posicion_gato[0]-self.posicion_raton[0]) + abs(self.posicion_gato[1]-self.posicion_raton[1])
            d_rs = abs(self.posicion_raton[0]-self.posicion_salida[0]) + abs(self.posicion_raton[1]-self.posicion_salida[1])
            return (d_gr * 2) - (d_rs * 4) if es_max else (d_gr * 10)

        mejor = float('-inf') if es_max else float('inf')
        yo = self.posicion_raton if es_max else self.posicion_gato
        rival = self.posicion_gato if es_max else self.posicion_raton
        for m in self.obtener_movimientos_legales(yo, rival, es_gato=not es_max):
            sim = copy.deepcopy(self)
            if es_max: sim.posicion_raton = m
            else: sim.posicion_gato = m
            val = sim.minimax(profundidad - 1, not es_max)
            mejor = max(mejor, val) if es_max else min(mejor, val)
        return mejor

    def mover_ia(self, es_raton):
        mejor_p = float('-inf') if es_raton else float('inf')
        yo = self.posicion_raton if es_raton else self.posicion_gato
        rival = self.posicion_gato if es_raton else self.posicion_raton
        mejor_m = yo
        for m in self.obtener_movimientos_legales(yo, rival, es_gato=not es_raton):
            sim = copy.deepcopy(self)
            if es_raton: sim.posicion_raton = m
            else: sim.posicion_gato = m
            p = sim.minimax(3, not es_raton)
            if (es_raton and p > mejor_p) or (not es_raton and p < mejor_p):
                mejor_p, mejor_m = p, m
        if es_raton:
            self.posicion_raton = mejor_m
            if self.posicion_raton in self.lista_quesos: self.lista_quesos.remove(self.posicion_raton)
        else: self.posicion_gato = mejor_m

def manual(juego, pos, rival, es_g):
    while True:
        muda = input(f"\n Mover {'GATO' if es_g else 'RATÓN'} (W/A/S/D): ").lower()
        d = {'w':(-1,0), 's':(1,0), 'a':(0,-1), 'd':(0,1)}
        if muda in d:
            n = [pos[0]+d[muda][0], pos[1]+d[muda][1]]
            if n in juego.obtener_movimientos_legales(pos, rival, es_g): return n
        print(" Movimiento no válido.")

def jugar():
    # Configuración inicial
    LIMITE_TURNOS = 80
    TAMANO_TABLERO = 10
    historial_estados = {}
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("--- CAT & MOUSE: THE CHASE ---")
    print("1. Jugar como RATÓN\n2. Jugar como GATO\n3. Modo ESPECTADOR")
    op = input("\nSelecciona una opción (1, 2 o 3): ")
    
    j = Laberinto(tamano=TAMANO_TABLERO)
    
    for t in range(1, LIMITE_TURNOS + 1):
        # 1. Detección de Bucles / Empate por repetición
        estado_actual = (tuple(j.posicion_gato), tuple(j.posicion_raton))
        historial_estados[estado_actual] = historial_estados.get(estado_actual, 0) + 1
        
        if historial_estados[estado_actual] >= 3:
            j.mostrar_tablero(t, "EMPATE", "EMPATE")
            print(f"\n🤝 EMPATE: Se detectó un patrón repetitivo en las posiciones {estado_actual}.")
            return

        # 2. Definición de modos para mostrar en pantalla
        m_r = "JUGADOR" if op == "1" else "GENIO"
        m_g = "JUGADOR" if op == "2" else "GENIO"
        
        j.mostrar_tablero(t, m_g, m_r)

        # 3. Turno del Ratón
        if op == "1": 
            j.posicion_raton = manual(j, j.posicion_raton, j.posicion_gato, False)
            if j.posicion_raton in j.lista_quesos: j.lista_quesos.remove(j.posicion_raton)
        else: 
            j.mover_ia(True)
        
        if j.posicion_raton == j.posicion_salida:
            j.mostrar_tablero(t, m_g, m_r)
            print("🧀 ¡VICTORIA! El ratón escapó por la puerta."); return

        # 4. Turno del Gato
        j.mostrar_tablero(t, m_g, m_r)
        if op == "2": 
            j.posicion_gato = manual(j, j.posicion_gato, j.posicion_raton, True)
        else: 
            if op == "3": time.sleep(0.4) # Pausa para ver los movimientos en modo espectador
            j.mover_ia(False)

        if j.posicion_gato == j.posicion_raton:
            j.mostrar_tablero(t, m_g, m_r)
            print("💀 ¡GAME OVER! El gato atrapó al ratón."); return

    print("\n🤝 EMPATE: Se alcanzó el límite máximo de turnos.")

if __name__ == "__main__":
    jugar()





