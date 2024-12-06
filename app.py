import random
import matplotlib.pyplot as plt
import sys

class Sustrato:
    def __init__(self, ancho, alto, prob_nutrientes=0.1, energia_nutrientes=1):
        self.ancho = ancho
        self.alto = alto
        self.energia_nutrientes = energia_nutrientes
        self.mapa_nutrientes = [[0 for _ in range(ancho)] for _ in range(alto)]
        self.mapa_micelios = [[0 for _ in range(ancho)] for _ in range(alto)]
        self.mapa_arboles = [[0 for _ in range(ancho)] for _ in range(alto)]
        self.distribuir_nutrientes(prob_nutrientes, tipo_distribucion='grupos')

    def distribuir_nutrientes(self, prob_nutrientes, tipo_distribucion='grupos'):
        if tipo_distribucion == 'uniforme':
            for y in range(self.alto):
                for x in range(self.ancho):
                    if random.random() < prob_nutrientes:
                        self.mapa_nutrientes[y][x] = random.randint(1, 10)  # Cantidad aleatoria de nutrientes
        elif tipo_distribucion == 'grupos':
            num_grupos = int(self.ancho * self.alto * prob_nutrientes)
            for _ in range(num_grupos):
                grupo_x = random.randint(0, self.ancho - 1)
                grupo_y = random.randint(0, self.alto - 1)
                tamano_grupo = random.randint(1, 3)  # Tamaño del grupo de nutrientes
                for _ in range(tamano_grupo):
                    dx = random.randint(-2, 2)
                    dy = random.randint(-2, 2)
                    x = min(max(grupo_x + dx, 0), self.ancho - 1)
                    y = min(max(grupo_y + dy, 0), self.alto - 1)
                    self.mapa_nutrientes[y][x] = random.randint(1, 10)  # Cantidad aleatoria de nutrientes
        elif tipo_distribucion == 'bordes':
            for y in range(self.alto):
                for x in range(self.ancho):
                    if x < self.ancho * 0.1 or x > self.ancho * 0.9 or y < self.alto * 0.1 or y > self.alto * 0.9:
                        if random.random() < prob_nutrientes:
                            self.mapa_nutrientes[y][x] = random.randint(1, 10)  # Cantidad aleatoria de nutrientes

    def consumir_nutrientes(self, x, y, cantidad):
        self.mapa_nutrientes[y][x] = max(0, self.mapa_nutrientes[y][x] - cantidad)

    def marcar_micelio(self, x, y):
        self.mapa_micelios[y][x] = 1

    def marcar_arbol(self, x, y):
        self.mapa_arboles[y][x] = 1

class Arbol:
    def __init__(self, x, y, energia_arbol=5):
        self.x = x
        self.y = y
        self.edad = 0
        self.nutrientes_acumulados = 0
        self.nivel_nutrientes_intercambio = 0
        self.energia_arbol = energia_arbol

    def intercambiar_nutrientes(self, micelio):
        # Lógica de intercambio de nutrientes
        return self.energia_arbol

class Micelio:
    def __init__(self, x, y, centro_x, centro_y, direccion=None, energia=10):
        self.x = x
        self.y = y
        self.edad = 0
        self.energia = energia
        self.centro_x = centro_x
        self.centro_y = centro_y
        self.direccion = direccion if direccion else random.choice([(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)])

    def crecer(self, sustrato, arboles):
        # Lógica de crecimiento del micelio buscando nutrientes
        nuevas_posiciones = []
        direcciones = [self.direccion] + [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]  # Direcciones: preferida y otras

        # Ordenar direcciones por distancia al centro
        direcciones.sort(key=lambda d: ((self.x + d[0] - self.centro_x) ** 2 + (self.y + d[1] - self.centro_y) ** 2), reverse=True)

        crecio = False
        for dx, dy in direcciones:
            nuevo_x = self.x + dx
            nuevo_y = self.y + dy
            if 0 <= nuevo_x < sustrato.ancho and 0 <= nuevo_y < sustrato.alto:
                if sustrato.mapa_micelios[nuevo_y][nuevo_x] == 0:  # Solo crecer en celdas vacías
                    if sustrato.mapa_nutrientes[nuevo_y][nuevo_x] > 0:  # Buscar nutrientes
                        nuevas_posiciones.append(Micelio(nuevo_x, nuevo_y, self.centro_x, self.centro_y, (dx, dy), self.energia))
                        sustrato.marcar_micelio(nuevo_x, nuevo_y)
                        sustrato.consumir_nutrientes(nuevo_x, nuevo_y, 1)  # Consumir un nutriente
                        self.energia += sustrato.energia_nutrientes  # Ganar energía al consumir nutrientes
                        crecio = True
                        break  # Crecer en una sola dirección por ciclo
                    elif sustrato.mapa_arboles[nuevo_y][nuevo_x] == 1:  # Encontrar un árbol
                        nuevas_posiciones.append(Micelio(nuevo_x, nuevo_y, self.centro_x, self.centro_y, (dx, dy), self.energia))
                        sustrato.marcar_micelio(nuevo_x, nuevo_y)
                        arbol = next(arbol for arbol in arboles if arbol.x == nuevo_x and arbol.y == nuevo_y)
                        self.energia += arbol.intercambiar_nutrientes(self)  # Ganar energía al encontrar un árbol
                        crecio = True
                        break  # Crecer en una sola dirección por ciclo

        if not crecio and self.energia > 0:
            # Si no encontró nutrientes, crecer en cualquier dirección pero más lento
            for dx, dy in direcciones:
                nuevo_x = self.x + dx
                nuevo_y = self.y + dy
                if 0 <= nuevo_x < sustrato.ancho and 0 <= nuevo_y < sustrato.alto:
                    if sustrato.mapa_micelios[nuevo_y][nuevo_x] == 0:  # Solo crecer en celdas vacías
                        if random.random() < 0.5:  # Probabilidad de crecer más lento
                            nuevas_posiciones.append(Micelio(nuevo_x, nuevo_y, self.centro_x, self.centro_y, (dx, dy), self.energia - 1))
                            sustrato.marcar_micelio(nuevo_x, nuevo_y)
                            self.energia -= 1  # Perder energía al crecer sin nutrientes
                            break  # Crecer en una sola dirección por ciclo

        return nuevas_posiciones

class ControlPrueba:
    def __init__(self, ancho, alto, num_arboles, prob_nutrientes=0.1, energia_nutrientes=1, energia_arbol=5, tipo_distribucion='grupos'):
        self.sustrato = Sustrato(ancho, alto, prob_nutrientes, energia_nutrientes)
        self.micelios = []
        self.arboles = []
        self.ciclo_actual = 0

        # Generar un único micelio en el centro
        self.centro_x = ancho // 2
        self.centro_y = alto // 2
        micelio = Micelio(self.centro_x, self.centro_y, self.centro_x, self.centro_y)
        self.micelios.append(micelio)
        self.sustrato.marcar_micelio(self.centro_x, self.centro_y)
        
        # Generar árboles
        for _ in range(num_arboles):
            x = random.randint(0, ancho - 1)
            y = random.randint(0, alto - 1)
            arbol = Arbol(x, y, energia_arbol)
            self.arboles.append(arbol)
            self.sustrato.marcar_arbol(x, y)
        
        # Configuración de la visualización
        plt.ion()  # Activar modo interactivo
        self.fig, self.ax1 = plt.subplots(figsize=(10, 10))
        plt.tight_layout()
        
        # Conectar el evento de cierre de la ventana
        self.fig.canvas.mpl_connect('close_event', self.on_close)

    def on_close(self, event):
        print("Cerrando la ventana y deteniendo la ejecución.")
        plt.ioff()  # Desactivar modo interactivo
        plt.close(self.fig)
        sys.exit()  # Salir del programa

    def simular_ciclo(self) -> None:
        nuevos_micelios = []
        
        for micelio in self.micelios:
            if micelio.energia > 0:  # Solo crecer si el micelio tiene energía
                posiciones_crecimiento = micelio.crecer(self.sustrato, self.arboles)
                nuevos_micelios.extend(posiciones_crecimiento)
        
        self.micelios.extend(nuevos_micelios)
        self.ciclo_actual += 1
        self.actualizar_visualizacion()
        
        # Verificar si todos los árboles han sido conectados
        if all(self.sustrato.mapa_micelios[arbol.y][arbol.x] == 1 for arbol in self.arboles):
            print(f"Todos los árboles han sido conectados en el ciclo {self.ciclo_actual}.")
            plt.ioff()  # Desactivar modo interactivo
            plt.show()  # Mostrar la figura final
            sys.exit()  # Salir del programa
        
    def actualizar_visualizacion(self) -> None:
        self.ax1.clear()
        self.ax1.set_title('Crecimiento del Micelio')
        self.ax1.set_xlim(0, self.sustrato.ancho)
        self.ax1.set_ylim(0, self.sustrato.alto)
        
        # Dibujar nutrientes
        x_nutrientes = []
        y_nutrientes = []
        for y in range(self.sustrato.alto):
            for x in range(self.sustrato.ancho):
                if self.sustrato.mapa_nutrientes[y][x] > 0:
                    x_nutrientes.append(x)
                    y_nutrientes.append(y)
        self.ax1.scatter(x_nutrientes, y_nutrientes, c='blue', marker='s', label='Nutrientes')
        
        # Dibujar micelios
        x_coords = [micelio.x for micelio in self.micelios]
        y_coords = [micelio.y for micelio in self.micelios]
        self.ax1.scatter(x_coords, y_coords, c='white', edgecolors='black', label='Micelio')
        
        # Dibujar árboles
        x_arboles = [arbol.x for arbol in self.arboles]
        y_arboles = [arbol.y for arbol in self.arboles]
        self.ax1.scatter(x_arboles, y_arboles, c='green', marker='^', label='Árboles')
        
        # Mostrar el ciclo actual y la energía del micelio
        energia_total = sum(micelio.energia for micelio in self.micelios)
        self.ax1.text(0.02, 0.95, f'Ciclo: {self.ciclo_actual} - Energía Total: {energia_total}', transform=self.ax1.transAxes, fontsize=12, verticalalignment='top', color='white', bbox=dict(facecolor='black', alpha=0.5))
        
        self.ax1.legend()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

# Ejemplo de uso
control = ControlPrueba(ancho=100, alto=100, num_arboles=10, prob_nutrientes=0.1, energia_nutrientes=1, energia_arbol=5, tipo_distribucion='bordes')
for _ in range(100):  # Simular N ciclos
    control.simular_ciclo()

plt.ioff()  # Desactivar modo interactivo
plt.show()  # Mostrar la figura final