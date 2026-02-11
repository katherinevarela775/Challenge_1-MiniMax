import random, copy, os, time

class Laberinto:
    def __init__(self, dimension):
        self.dimension = dimension
        self.posicion_gato = [0, 1]
        self.posicion_raton = [dimension - 1, dimension - 1]
        self.posicion_salida = [0, 0]
        
        self.historial_gato = []
        self.historial_raton = []
        self.lista_quesos = []
        self.lista_paredes = []
        
        while True:
            self.lista_paredes = []
            zonas_restringidas = [[0,0], [0,1], [1,0], [1,1], self.posicion_gato, self.posicion_raton]
            
            for _ in range((dimension * dimension) // 4):
                pared_tentativa = [random.randint(0, dimension - 1), random.randint(0, dimension - 1)]
                if pared_tentativa not in zonas_restringidas and pared_tentativa not in self.lista_paredes:
                    self.lista_paredes.append(pared_tentativa)
            
            if self.existe_camino_real(self.posicion_raton, self.posicion_salida):
                self.lista_quesos = [] # Limpiar antes de llenar
                while len(self.lista_quesos) < 3:
                    queso_tentativo = [random.randint(0, dimension - 1), random.randint(0, dimension - 1)]
                    if queso_tentativo not in self.lista_paredes and queso_tentativo not in zonas_restringidas and queso_tentativo not in self.lista_quesos:
                        self.lista_quesos.append(queso_tentativo)
                break

    def existe_camino_real(self, inicio, fin):
        cola_busqueda = [inicio]
        nodos_visitados = [inicio]
        for posicion in cola_busqueda:
            if posicion == fin: return True
            for vecino in self.obtener_movimientos_legales(posicion, [], es_gato=False):
                if vecino not in nodos_visitados:
                    nodos_visitados.append(vecino)
                    cola_busqueda.append(vecino)
        return False

    def obtener_movimientos_legales(self, posicion_actual, posicion_oponente, es_gato=True):
        movimientos_validos = []
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for delta_fila, delta_col in direcciones:
            nueva_fila = posicion_actual[0] + delta_fila
            nueva_col = posicion_actual[1] + delta_col
            
            if 0 <= nueva_fila < self.dimension and 0 <= nueva_col < self.dimension:
                punto_nuevo = [nueva_fila, nueva_col]
                
                if punto_nuevo not in self.lista_paredes:
                    # CORRECCIÓN: El ratón NUNCA puede saltar sobre el gato
                    if not es_gato and punto_nuevo == posicion_oponente:
                        continue
                    movimientos_validos.append(punto_nuevo)
                    
        random.shuffle(movimientos_validos)
        return movimientos_validos

    def mostrar_tablero(self, numero_turno, modo_gato, modo_raton):
        os.system('cls' if os.name == 'nt' else 'clear')
        header = f"║ Turno: {numero_turno:2} | Gato: {modo_gato:6} | Ratón: {modo_raton:6} ║"
        print(f"╔{'═' * (len(header)-2)}╗\n{header}\n╚{'═' * (len(header)-2)}╝")
        
        for fila_idx in range(self.dimension):
            buffer_fila = ""
            for col_idx in range(self.dimension):
                punto_actual = [fila_idx, col_idx]
                if punto_actual == self.posicion_gato: buffer_fila += "🐱 "
                elif punto_actual == self.posicion_raton: buffer_fila += "🐭 "
                elif punto_actual == self.posicion_salida: buffer_fila += "🚪 "
                elif punto_actual in self.lista_quesos: buffer_fila += "🧀 "
                elif punto_actual in self.lista_paredes: buffer_fila += "⬛ "
                else: buffer_fila += "⬜ "
            print(buffer_fila)

    def minimax(self, profundidad, es_maximizando):
        # CORRECCIÓN: Penalizaciones mucho más fuertes para evitar colisiones lógicas
        if self.posicion_gato == self.posicion_raton: return -5000 
        if self.posicion_raton == self.posicion_salida: return 5000
        
        if profundidad == 0:
            dist_gato_raton = abs(self.posicion_gato[0] - self.posicion_raton[0]) + abs(self.posicion_gato[1] - self.posicion_raton[1])
            dist_raton_salida = abs(self.posicion_raton[0] - self.posicion_salida[0]) + abs(self.posicion_raton[1] - self.posicion_salida[1])
            
            penalidad_raton = self.historial_raton.count(self.posicion_raton) * 150
            penalidad_gato = self.historial_gato.count(self.posicion_gato) * 150

            if es_maximizando: 
                dist_queso = min([abs(self.posicion_raton[0]-q[0]) + abs(self.posicion_raton[1]-q[1]) for q in self.lista_quesos]) if self.lista_quesos else 0
                return (dist_gato_raton * 2) - (dist_raton_salida * 4) - (dist_queso * 2) - penalidad_raton
            else: 
                # CORRECCIÓN: El gato ahora prioriza cerrar la distancia agresivamente
                return (dist_gato_raton * 10) + penalidad_gato

        if es_maximizando:
            mejor_valor = float('-inf')
            for movimiento in self.obtener_movimientos_legales(self.posicion_raton, self.posicion_gato, es_gato=False):
                estado_simulado = copy.deepcopy(self)
                estado_simulado.posicion_raton = movimiento
                valor_obtenido = estado_simulado.minimax(profundidad - 1, False)
                mejor_valor = max(mejor_valor, valor_obtenido)
            return mejor_valor
        else:
            mejor_valor = float('inf')
            for movimiento in self.obtener_movimientos_legales(self.posicion_gato, self.posicion_raton, es_gato=True):
                estado_simulado = copy.deepcopy(self)
                estado_simulado.posicion_gato = movimiento
                valor_obtenido = estado_simulado.minimax(profundidad - 1, True)
                mejor_valor = min(mejor_valor, valor_obtenido)
            return mejor_valor

    def ejecutar_movimiento_ia(self, es_raton, profundidad):
        mejor_puntuacion = float('-inf') if es_raton else float('inf')
        posicion_actual = self.posicion_raton if es_raton else self.posicion_gato
        mejor_movimiento = posicion_actual
        
        movimientos = self.obtener_movimientos_legales(posicion_actual, self.posicion_gato if es_raton else self.posicion_raton, es_gato=(not es_raton))
        
        for movimiento in movimientos:
            simulacion = copy.deepcopy(self)
            if es_raton: simulacion.posicion_raton = movimiento
            else: simulacion.posicion_gato = movimiento
            
            puntuacion = simulacion.minimax(profundidad, not es_raton)
            if (es_raton and puntuacion > mejor_puntuacion) or (not es_raton and puntuacion < mejor_puntuacion):
                mejor_puntuacion, mejor_movimiento = puntuacion, movimiento
        
        if es_raton:
            self.posicion_raton = mejor_movimiento
            if self.posicion_raton in self.lista_quesos: self.lista_quesos.remove(self.posicion_raton)
            self.historial_raton = (self.historial_raton + [list(mejor_movimiento)])[-4:]
        else:
            self.posicion_gato = mejor_movimiento
            self.historial_gato = (self.historial_gato + [list(mejor_movimiento)])[-4:]

def jugar_simulacion(tamano=10, turnos_azar=4, limite_turnos=40):
    juego = Laberinto(tamano)
    for turno in range(1, limite_turnos + 1):
        modo = "AZAR" if turno <= turnos_azar else "GENIO"
        juego.mostrar_tablero(turno, modo, modo)
        
        # Turno del Ratón
        if turno <= turnos_azar:
            movs = juego.obtener_movimientos_legales(juego.posicion_raton, juego.posicion_gato, es_gato=False)
            if movs: juego.posicion_raton = random.choice(movs)
        else:
            juego.ejecutar_movimiento_ia(es_raton=True, profundidad=3)
        
        if juego.posicion_raton == juego.posicion_salida:
            juego.mostrar_tablero(turno, modo, modo)
            print("🧀 ¡VICTORIA! El ratón escapó por la puerta."); return
        if juego.posicion_gato == juego.posicion_raton:
            juego.mostrar_tablero(turno, modo, modo)
            print("💀 ¡GAME OVER! El gato atrapó al ratón."); return

        # Turno del Gato
        juego.mostrar_tablero(turno, modo, modo)
        if turno <= turnos_azar:
            movs = juego.obtener_movimientos_legales(juego.posicion_gato, juego.posicion_raton, es_gato=True)
            if movs: juego.posicion_gato = random.choice(movs)
        else:
            juego.ejecutar_movimiento_ia(es_raton=False, profundidad=3)
            
        if juego.posicion_gato == juego.posicion_raton:
            juego.mostrar_tablero(turno, modo, modo)
            print("💀 ¡GAME OVER! El gato atrapó al ratón."); return
        
        time.sleep(0.8)
    print("🤝 EMPATE: Se agotó el tiempo de persecución.")

jugar_simulacion(tamano=10, turnos_azar=2, limite_turnos=40)





