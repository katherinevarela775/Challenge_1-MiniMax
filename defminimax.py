import random, os, time

# --- FUNCIONES DE GENERACIÓN Y LÓGICA ---
def generar_mapa(tamano):
    """Crea todos los elementos iniciales del laberinto y los guarda en un diccionario."""
    pos_gato = [0, 1] # Posición inicial fija del gato
    pos_raton = [tamano - 1, tamano - 1] # El ratón empieza en la esquina opuesta
    salida = [0, 0] # La meta del ratón
    
    while True: # Bucle para intentar generar un mapa válido
        paredes = [] # Lista de obstáculos
        # Definimos zonas donde no pueden aparecer paredes para no bloquear el inicio o la meta
        seguras = [[0,0], [0,1], [1,0], [1,1], pos_gato, pos_raton]
        
        # Generar paredes aleatorias según el tamaño del tablero
        for _ in range((tamano ** 2) // 7):
            p = [random.randint(0, tamano-1), random.randint(0, tamano-1)]
            if p not in seguras and p not in paredes: # Valida que no sea zona segura ni pared repetida
                paredes.append(p)
        
        # Validación de victoria: El algoritmo BFS confirma si hay un camino libre a la salida
        if existe_camino(pos_raton, salida, tamano, paredes):
            quesos = colocar_quesos(tamano, paredes, seguras) # Si el mapa es válido, ponemos los quesos
            # Devolvemos un diccionario con todo el "estado" del juego (esto reemplaza a los atributos de clase)
            return {
                "tamano": tamano, "pos_gato": pos_gato, "pos_raton": pos_raton,
                "salida": salida, "quesos": quesos, "paredes": paredes, "memoria_raton": []
            }

def existe_camino(inicio, fin, tamano, paredes):
    """Algoritmo de búsqueda (BFS) para garantizar que el laberinto tenga solución."""
    cola = [inicio] # Nodos por explorar
    visitados = [inicio] # Nodos ya explorados
    for actual in cola:
        if actual == fin: return True # Si encontramos la salida, el mapa sirve
        # Buscamos vecinos (pasamos la lista de paredes y el tamaño por parámetro)
        for vecino in movimientos_posibles(actual, [-1,-1], tamano, paredes, es_gato=False):
            if vecino not in visitados:
                visitados.append(vecino)
                cola.append(vecino)
    return False # Si agota la cola y no llega al fin, el mapa está bloqueado

def colocar_quesos(tamano, paredes, seguras):
    """Ubica 3 quesos aleatorios en posiciones válidas."""
    quesos = []
    while len(quesos) < 3:
        q = [random.randint(0, tamano-1), random.randint(0, tamano-1)]
        # Verifica que no haya pared, que no sea zona segura y que no haya ya un queso ahí
        if q not in paredes and q not in seguras and q not in quesos:
            quesos.append(q)
    return quesos

def movimientos_posibles(pos, oponente, tamano, paredes, es_gato=True):
    """Calcula los movimientos legales (arriba, abajo, izquierda, derecha)."""
    opciones = []
    for df, dc in [(-1,0), (1,0), (0,-1), (0,1)]: # Direcciones posibles
        nueva_pos = [pos[0]+df, pos[1]+dc] # Nueva coordenada hipotética
        # Validamos: 1. Que esté dentro del tablero 2. Que no sea una pared
        if 0 <= nueva_pos[0] < tamano and 0 <= nueva_pos[1] < tamano:
            if nueva_pos not in paredes:
                # El ratón no puede saltar encima del gato (el gato sí sobre el ratón para atraparlo)
                if not es_gato and nueva_pos == oponente: continue
                opciones.append(nueva_pos)
    return opciones

# --- SISTEMA DE INTELIGENCIA ARTIFICIAL (IA) ---

def puntuar_estado(datos, es_raton):
    """Heurística: Asigna un valor numérico a qué tan 'buena' es una posición."""
    g, r, s = datos["pos_gato"], datos["pos_raton"], datos["salida"]
    # Cálculo de distancia Manhattan (suma de pasos horizontales y verticales)
    dist_gr = abs(g[0]-r[0]) + abs(g[1]-r[1])
    dist_rs = abs(r[0]-s[0]) + abs(r[1]-s[1])
    
    if es_raton: # Lógica del ratón: alejarse del gato y acercarse a la salida
        penalizacion = datos["memoria_raton"].count(r) * 50 # Castigo por repetir casillas
        return (dist_gr * 5) - (dist_rs * 60) - penalizacion + random.randint(0,5)
    else: # Lógica del gato: reducir la distancia al ratón lo más posible
        return -(dist_gr * 200) + random.randint(0,5)

def ia_decidir(datos, profundidad, es_max):
    """Simulador Minimax: Imagina jugadas futuras para elegir la mejor."""
    if datos["pos_gato"] == datos["pos_raton"]: return -20000 # Gana el gato (valor muy bajo)
    if datos["pos_raton"] == datos["salida"]: return 20000 # Gana el ratón (valor muy alto)
    if profundidad == 0: return puntuar_estado(datos, es_max) # Fin de la imaginación, evaluamos

    mejor_valor = float('-inf') if es_max else float('inf') # Inicializamos según sea Max o Min
    yo = datos["pos_raton"] if es_max else datos["pos_gato"]
    el_otro = datos["pos_gato"] if es_max else datos["pos_raton"]
    
    for mov in movimientos_posibles(yo, el_otro, datos["tamano"], datos["paredes"], es_gato=not es_max):
        pos_original = list(yo) # Guardamos la posición real para no romper el juego
        if es_max: datos["pos_raton"] = mov # Movemos virtualmente al ratón
        else: datos["pos_gato"] = mov # Movemos virtualmente al gato
        
        # Recursividad: preguntamos qué haría el oponente en el siguiente turno
        valor = ia_decidir(datos, profundidad - 1, not es_max)
        # Nos quedamos con el mejor (si es nuestro turno) o el peor (si es del oponente)
        mejor_valor = max(mejor_valor, valor) if es_max else min(mejor_valor, valor)
        
        # Revertimos el movimiento virtual (Backtracking)
        if es_max: datos["pos_raton"] = pos_original
        else: datos["pos_gato"] = pos_original
        
    return mejor_valor

def ejecutar_turno_ia(datos, es_raton):
    """Toma la decisión final y actualiza las coordenadas en el diccionario de datos."""
    yo = datos["pos_raton"] if es_raton else datos["pos_gato"]
    el_otro = datos["pos_gato"] if es_raton else datos["pos_raton"]
    prof = 3 if es_raton else 4 # El gato suele pensar un paso más adelante
    
    mejor_m, mejor_p = yo, (float('-inf') if es_raton else float('inf'))
    
    # Probamos todos los movimientos inmediatos posibles
    for m in movimientos_posibles(yo, el_otro, datos["tamano"], datos["paredes"], es_gato=not es_raton):
        original = list(yo)
        if es_raton: datos["pos_raton"] = m
        else: datos["pos_gato"] = m 

        puntuacion = ia_decidir(datos, prof, not es_raton) # Simulamos el futuro de ese movimiento

        # Si el movimiento es mejor que el anterior registrado, lo guardamos
        if (es_raton and puntuacion > mejor_p) or (not es_raton and puntuacion < mejor_p):
            mejor_p, mejor_m = puntuacion, m
        
        # Limpiamos el tablero virtual para la siguiente prueba
        if es_raton: datos["pos_raton"] = original
        else: datos["pos_gato"] = original
            
    # Ejecutamos el movimiento ganador en el estado real del juego
    if es_raton:
        datos["pos_raton"] = mejor_m
        datos["memoria_raton"].append(list(mejor_m)) # El ratón anota dónde estuvo para no marearse
        if len(datos["memoria_raton"]) > 5: datos["memoria_raton"].pop(0) # Memoria de corto plazo
        if datos["pos_raton"] in datos["quesos"]: datos["quesos"].remove(datos["pos_raton"]) # Come queso
    else:
        datos["pos_gato"] = mejor_m

# --- INTERFAZ Y JUEGO ---

def dibujar(datos, turno, m_gato, m_raton):
    """Renderiza el tablero en la consola."""
    os.system('cls' if os.name == 'nt' else 'clear') # Limpia la pantalla
    info = f" TURNO: {turno:2} | GATO: {m_gato:8} | RATÓN: {m_raton:8} "
    ancho = max(len(info), datos["tamano"] * 3)
    
    # Imprime el marco superior del marcador
    print(f"╔{'═' * ancho}╗\n║{info.center(ancho)}║\n╚{'═' * ancho}╝")
    
    # Genera el mapa visualmente recorriendo filas y columnas
    for f in range(datos["tamano"]):
        fila = ""
        for c in range(datos["tamano"]):
            p = [f, c]
            if p == datos["pos_gato"]: fila += "🐱 "
            elif p == datos["pos_raton"]: fila += "🐭 "
            elif p == datos["salida"]: fila += "🚪 "
            elif p in datos["quesos"]: fila += "🧀 "
            elif p in datos["paredes"]: fila += "⬛ "
            else: fila += "⬜ "
        print(fila)

def control_manual(datos, pos, rival, es_g):
    """Gestiona la entrada de teclado para el modo jugador."""
    controles = {'w':(-1,0), 's':(1,0), 'a':(0,-1), 'd':(0,1)}
    while True:
        muda = input(f"\n Mover {'GATO' if es_g else 'RATÓN'} (W/A/S/D): ").lower()
        if muda in controles:
            n = [pos[0]+controles[muda][0], pos[1]+controles[muda][1]] # Calcula nueva posición
            # Verifica si ese movimiento es legal según el motor de física
            if n in movimientos_posibles(pos, rival, datos["tamano"], datos["paredes"], es_g):
                return n
        print(" ¡Movimiento inválido!")

def jugar():
    """Función principal que orquesta el ciclo de vida del juego."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("--- BIENVENIDO A CAT & MOUSE (VERSIÓN FUNCIONAL) ---")
    
    # Captura el tamaño deseado
    t_inp = input("\n¿Tamaño del tablero? (ej. 10): ")
    tam = int(t_inp) if t_inp.isdigit() else 10
    
    print("\n[1] Jugar como RATÓN  \n[2] Jugar como GATO \n[3] Ser ESPECTADOR")
    op = input("Selecciona modo (1, 2 o 3): ")
    
    # El estado del juego se crea aquí y se pasará a todas las funciones
    juego = generar_mapa(tam)
    historial = {} # Para detectar bucles infinitos
    
    for t in range(1, 80): # Bucle de turnos
        # Creamos una 'foto' del estado actual (posiciones)
        estado_actual = (tuple(juego["pos_gato"]), tuple(juego["pos_raton"]))
        historial[estado_actual] = historial.get(estado_actual, 0) + 1
        
        # Si se repite mucho la misma posición de ambos, declaramos empate
        if historial[estado_actual] >= 5:
            dibujar(juego, t, "EMPATE", "EMPATE")
            print("\n🤝 EMPATE por repetición técnica."); return

        # Definimos quién es el humano y quién la IA para el marcador
        m_r = "PLAYER" if op == "1" else "IA"
        m_g = "PLAYER" if op == "2" else "IA"
        
        dibujar(juego, t, m_g, m_r) # Dibujamos el turno actual
        
        # --- LÓGICA TURNO RATÓN ---
        if op == "1": 
            juego["pos_raton"] = control_manual(juego, juego["pos_raton"], juego["pos_gato"], False)
            if juego["pos_raton"] in juego["quesos"]: juego["quesos"].remove(juego["pos_raton"])
        else: 
            ejecutar_turno_ia(juego, True)
        
        # Validaciones de fin de juego (Ratón gana o es atrapado)
        if juego["pos_raton"] == juego["salida"]:
            dibujar(juego, t, m_g, m_r)
            print("\n🏁 FINAL: El Ratón escapó."); return
            
        if juego["pos_gato"] == juego["pos_raton"]:
            dibujar(juego, t, m_g, m_r)
            print("\n⚔️ FINAL: El gato atrapó al Ratón."); return

        # --- LÓGICA TURNO GATO ---
        dibujar(juego, t, m_g, m_r)
        if op == "2": 
            juego["pos_gato"] = control_manual(juego, juego["pos_gato"], juego["pos_raton"], True)
        else: 
            if op == "3": time.sleep(0.4) # Pausa estética para el espectador
            ejecutar_turno_ia(juego, False)

        # Validación final de turno del gato
        if juego["pos_gato"] == juego["pos_raton"]:
            dibujar(juego, t, m_g, m_r)
            print("\n⚔️ FINAL: El gato atrapó al Ratón."); return

    print("\n🤝 EMPATE: Tiempo agotado.") # Si llega al turno 80

if __name__ == "__main__":
    jugar() # Punto de entrada del programa