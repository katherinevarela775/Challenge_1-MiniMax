import random
import copy

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

 def obtener_movimientos_legales(self,posicion):
   posibles_movimientos = []
   # Definimos las 4 direcciones: (delta_fila, delta_columna)
   direcciones = [(-1, 0), (1, 0 ), (0, -1), (0, 1)]
   for d_f, d_c in direcciones:
      nueva_f = posicion[0] + d_f
      nueva_c = posicion[1] + d_c
      # Verificamos si la nueva posicion esta dentro de los limites
      if 0 <= nueva_f < self.filas and 0 <= nueva_c < self.columnas:
         posibles_movimientos.append([nueva_f, nueva_c])
   return posibles_movimientos 

 def minimax (self, profundidad, es_maximizando):
   # Situacion 1: Uno de los personajes gano o se llego al limite de vision (profundidad)
   if profundidad == 0 or self.gato_pos == self.raton_pos:
      return self.calcular_distancia() # Retorna el valor actual

   if es_maximizando: # Turno del Raton (quiere alejarse)
      mejor_valor =  float('-inf')
      for movimiento in self.obtener_movimientos_legales(self.raton_pos):
         # Creamos una copia del juego para simular
         simulacion = copy.deepcopy(self)
         # 2. Mueve al ratón en el futuro
         simulacion.raton_pos = movimiento
         # 3. Preguntamos que hara el gato despues
         valor = simulacion.minimax(profundidad - 1, False)
         mejor_valor = max(mejor_valor, valor)
         return mejor_valor

   else: # Turno del Gato (quiere acercarse)
      mejor_valor = float('inf')
      for movimiento in self.obtener_movimientos_legales(self.gato_pos):
         # 1. Copia el estado actual
         simulacion = copy.deepcopy(self)
         # 2. Mueve al gato en esa copia en el futuro
         simulacion.gato_pos = movimiento
         # 3. Preguntamos que hara el raton despues
         valor = simulacion.minimax(profundidad - 1, True)
         mejor_valor = min(mejor_valor, valor)
         return mejor_valor
 def mover_raton_inteligente(self, profundidad):
   mejor_puntuacion = float('-inf')
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

   # Crear juego
juego = Laberinto(6, 6)

# Turno de prueba
print("Estado Inicial:")
juego.mostrar()

print("El Ratón está pensando...")
# El ratón usa profundidad 3 (ve 3 movimientos al futuro)
juego.mover_raton_inteligente(3)

print("El Ratón se ha movido:")
juego.mostrar()


      





