import random

class Laberinto:
 def __init__(self, filas, columnas):
    self.filas = filas 
    self.columnas = columnas 
    # Posiciones iniciales
    self.gato_pos =  [0, 0] # Arriba a la izq.
    self.raton_pos = [filas - 1, columnas - 1] # Abajo a la der.

 def generar_tablero(self):
    # Matriz llena de puntos
    tablero = [["." for _ in range(self.columnas)] for _ in range(self.filas)]
    # Ubica al gato al gato y raton en sus coord. iniciales (tablero[fila][columnas])
    tablero[self.gato_pos[0]][self.gato_pos[1]] = "G"
    tablero[self.raton_pos[0]][self.raton_pos[1]] = "R"

    return tablero
 def mostrar(self):
    tablero_actual = self.generar_tablero()
    for fila in tablero_actual:
        print(" ".join(fila)) # Une los elementos con un espacio
   
    print("-" * 20) # Linea separadora de turnos

 def calcular_distancia(self):
    # Dist. Manhattan, le ayuda al gato a saber si se acerca al raton
    return abs(self.gato_pos[0] - self.raton_pos[0]) + abs(self.gato_pos[1]- self.raton_pos[1])

 def mover_raton_azar(self):
    # El raton se mueve al azar
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Arriba, Abajo, Izq., Der.

    movimiento = random.choice(direcciones)

    nueva_f = self.raton_pos[0] + movimiento[0]
    nueva_c = self.raton_pos[1] + movimiento[1]

    # Validacion1: que no salga del terreno de juego
    if 0 <= nueva_f < self.filas and 0 <= nueva_c < self.columnas:
      self.raton_pos = [nueva_f, nueva_c]

 def mover_gato_simple(self):
   # Aqui el gato intenta reducir distancia
   direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
   mejor_movimiento = self.gato_pos
   distancia_minima = float('inf')

   for d in direcciones:
      f = self.gato_pos[0] + d[0]
      c = self.gato_pos[1] + d[1]

      if 0 <= f < self.filas and 0 <= c < self.columnas:
         # Se simula la distancia en caso de movernos ahi
         dist = abs(f - self.raton_pos[0]) + abs(c - self.raton_pos[1])
         if dist < distancia_minima:
            distancia_minima = dist
            mejor_movimiento = [f, c]

   self.gato_pos =  mejor_movimiento





