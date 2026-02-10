import random
import copy
import os
import time

class Laberinto:
   def __init__(self, filas, columnas):
      self.filas = filas 
      self.columnas = columnas 
      # Posiciones iniciales
      self.gato_pos =  [0, 1] # Arriba a la izq.
      self.raton_pos = [filas - 1, columnas - 1] # Abajo a la der.
      self.salida_pos = [0, 0]

   def generar_tablero(self):
      # Matriz llena de puntos
      tablero = [["." for _ in range(self.columnas)] for _ in range(self.filas)]
      
      # Dibujamos la salida
      sf, sc = self.salida_pos
      tablero[sf][sc] = "S"

      # 1. Ubicamos primero al ratón
      tablero[self.raton_pos[0]][self.raton_pos[1]] = "R"
      
      # 2. Ubicamos al gato al final (si están en la misma posición, se verá la G)
      tablero[self.gato_pos[0]][self.gato_pos[1]] = "G"
      
      return tablero

   def mostrar(self, turno, modo_gato, modo_raton):
   #Limpia la consola
      os.system('cls' if os.name == 'nt' else 'clear')
      print("╔══════════════════════════════════════════╗")
      print(f"║ TURNO: {turno:2} | GATO: {modo_gato:7} | RATÓN: {modo_raton:7} ║")
      print("╚══════════════════════════════════════════╝")

      tablero_actual = self.generar_tablero()
      for fila in tablero_actual:
         render = "".join(["🐱 " if c == "G" else "🐭 " if c == "R" else "🚪 " if c == "S" else "⬜ " for c in fila])
         print(render)
      print("=" * 44)

   def calcular_distancia(self, pos_gato, pos_raton):
      # Dist. Manhattan, le ayuda al gato a saber si se acerca al raton
      return abs(self.gato_pos[0] - self.raton_pos[0]) + abs(self.gato_pos[1]- self.raton_pos[1])

   def obtener_movimientos_legales(self,posicion):
      posibles_movimientos = []
      # Definimos las 4 direcciones: (delta_fila, delta_columna)
      direcciones = [(-1, 0), (1, 0 ), (0, -1), (0, 1)]
      for df, dc in direcciones:
         nf, nc = posicion[0] + df, posicion[1] + dc
         # Verificamos si la nueva posicion esta dentro de los limites
         if 0 <= nf < self.filas and 0 <= nc < self.columnas:
            posibles_movimientos.append([nf, nc])

      return posibles_movimientos

   def ha_terminado(self):
   # 3. Condiciones de finalización según las nuevas pautas [cite: 29, 30]
      if self.gato_pos == self.raton_pos:
         return True, "GATO"
      if self.raton_pos == self.salida_pos:
         return True, "RATON"
      return False, None

   def minimax (self, profundidad, es_maximizando):
         terminado, ganador = self.ha_terminado()
         if terminado:
            if ganador == "RATON": return 1000 # Prioridad máxima escapar 
            if ganador == "GATO": return -1000 # Prioridad máxima atrapar 
         
         if profundidad == 0:
            # Evaluación: El ratón quiere distancia al gato y cercanía a la salida
            dist_gato_raton = self.calcular_distancia(self.gato_pos, self.raton_pos)
            dist_raton_salida = self.calcular_distancia(self.raton_pos, self.salida_pos)
            return dist_gato_raton - (dist_raton_salida * 2)

         if es_maximizando: # Turno del Ratón
            mejor_valor = float('-inf')
            for movimiento in self.obtener_movimientos_legales(self.raton_pos):
                  simulacion = copy.deepcopy(self)
                  simulacion.raton_pos = movimiento
                  valor = simulacion.minimax(profundidad - 1, False)
                  mejor_valor = max(mejor_valor, valor)
            return mejor_valor
         else: # Turno del Gato
            mejor_valor = float('inf')
            for movimiento in self.obtener_movimientos_legales(self.gato_pos):
                  simulacion = copy.deepcopy(self)
                  simulacion.gato_pos = movimiento
                  valor = simulacion.minimax(profundidad - 1, True)
                  mejor_valor = min(mejor_valor, valor)
            return mejor_valor

   def mover_raton_azar(self):
      direcciones = self.obtener_movimientos_legales(self.raton_pos)
      self.raton_pos = random.choice(direcciones)


   def mover_raton_inteligente(self, profundidad):
      mejor_puntuacion = float('-inf')
      movimientos = self.obtener_movimientos_legales(self.raton_pos)
      random.shuffle(movimientos) 
      mejor_movimiento = self.raton_pos

   # Buscamos en la lista de movimientos validos
      for mov in self.obtener_movimientos_legales(self.raton_pos):
         copia = copy.deepcopy(self)
         copia.raton_pos = mov

         # El Raton pregunta: Si me muevo a esta posicion, que es lo peor que podria hacerme el gato?
         # False significa que el siguiente turno en la simulacion es del Gato
         puntuacion = copia.minimax(profundidad, False)

      
      if puntuacion > mejor_puntuacion:
         mejor_puntuacion = puntuacion
         mejor_movimiento = mov
      self.raton_pos = mejor_movimiento

   def mover_gato_azar(self):
      movs = self.obtener_movimientos_legales(self.gato_pos)
      self.gato_pos = random.choice(movs)

   def mover_gato_inteligente(self, profundidad):
      mejor_puntuacion = float('inf')
      movimientos = self.obtener_movimientos_legales(self.gato_pos)
      random.shuffle(movimientos) 
      mejor_movimiento = self.gato_pos

      # Buscamos en la lista de movimientos validos
      for mov in self.obtener_movimientos_legales(self.gato_pos):
         copia = copy.deepcopy(self)
         copia.gato_pos = mov
         puntuacion = copia.minimax(profundidad, True)

         if puntuacion < mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_movimiento = mov
      self.gato_pos = mejor_movimiento

def jugar_simulacion(tamano=8, despertar=5):
   juego = Laberinto(tamano, tamano)
   turno = 1
   print("¡COMIENZA LA PERSECUCIÓN!")

    # 4. Bucle infinito hasta que uno gane 
   while True:
      modo = "AZAR" if turno <= despertar else "GENIO"
      juego.mostrar(turno, modo, modo)

      # Turno del Ratón
      if turno <= despertar: juego.mover_raton_azar()
      else: juego.mover_raton_inteligente(profundidad=2)

      terminado, ganador = juego.ha_terminado()
      if terminado:
         juego.mostrar(turno, modo, modo)
         if ganador == "RATON": print("🧀 ¡EL RATÓN ESCAPÓ POR LA PUERTA!")
         else: print("💀 ¡EL GATO ATRAPÓ AL RATÓN!")
         break

      # Turno del Gato
      if turno <= despertar: juego.mover_gato_azar()
      else: juego.mover_gato_inteligente(profundidad=2)

      terminado, ganador = juego.ha_terminado()
      if terminado:
         juego.mostrar(turno, modo, modo)
         if ganador == "GATO": print("💀 ¡EL GATO ATRAPÓ AL RATÓN!")
         else: print("🧀 ¡EL RATÓN ESCAPÓ!")
         break

      turno += 1
      time.sleep(0.4)

# Iniciar la partida final
jugar_simulacion(tamano=8, despertar=5) 

      





