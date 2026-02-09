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
    tablero_actual = self.generar_tablero()J
    for fila in tablero_actual:
        print(" ".join(fila)) # Une los elementos con un espacio
   
    print("-" * 20) # Linea separadora de turnos


 




