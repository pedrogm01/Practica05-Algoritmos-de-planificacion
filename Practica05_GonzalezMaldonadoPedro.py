import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QMessageBox, QInputDialog
)

# Clase del Simulador de Procesos
class SimuladorDeProcesos(QWidget):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.setWindowTitle("Simulador de Algoritmos de Planificación")
        self.setGeometry(100, 100, 800, 400)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Combobox para seleccionar el algoritmo
        self.comboBox = QComboBox()
        self.comboBox.addItem("FIFO")
        self.comboBox.addItem("SJF")
        self.comboBox.addItem("Prioridades")  # Nueva opción
        self.comboBox.addItem("Round Robin")  # Nueva opción
        layout.addWidget(QLabel("Selecciona el algoritmo de simulación:"))
        layout.addWidget(self.comboBox)
        
        # Botón para ejecutar la simulación
        self.botonEjecutar = QPushButton("Ejecutar simulación")
        self.botonEjecutar.clicked.connect(self.ejecutar_simulacion)
        layout.addWidget(self.botonEjecutar)

        # Botón para agregar nuevo proceso
        self.botonAgregar = QPushButton("Agregar nuevo proceso")
        self.botonAgregar.clicked.connect(self.agregar_proceso)
        layout.addWidget(self.botonAgregar)
        
        # Tabla para mostrar los resultados
        self.tabla = QTableWidget()
        layout.addWidget(self.tabla)
        
        # Mostrar layout
        self.setLayout(layout)
        self.procesos = []
    
    # Método para cargar los procesos desde un archivo .txt
    def cargar_procesos(self, algoritmo):
        nombre_archivo = f"{algoritmo}.txt"
        if not os.path.exists(nombre_archivo):
            print(f"Error: El archivo {nombre_archivo} no existe.")
            return
        
        self.procesos = []
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                partes = linea.strip().split(',')
                if len(partes) < 3:
                    print(f"Error: La línea '{linea.strip()}' no tiene el formato correcto.")
                    continue
                
                # Si el algoritmo es Prioridades, se espera un campo adicional para la prioridad
                if algoritmo == "Prioridades":
                    nombre_proceso, duracion, orden_llegada, prioridad = partes
                    self.procesos.append((nombre_proceso, int(duracion), int(orden_llegada), int(prioridad)))
                else:
                    nombre_proceso, duracion, orden_llegada = partes
                    self.procesos.append((nombre_proceso, int(duracion), int(orden_llegada)))
    
    # Método para ejecutar la simulación de los algoritmos de planificación
    def ejecutar_simulacion(self):
        algoritmo = self.comboBox.currentText()
        
        # Cargar el archivo de acuerdo al algoritmo seleccionado
        self.cargar_procesos(algoritmo)
        if not self.procesos:
            return  # No se cargaron procesos
        
        if algoritmo == "FIFO":
            resultado = self.fifo()
            self.mostrar_resultados_simulacion(resultado)
        elif algoritmo == "SJF":
            resultado = self.sjf()
            self.mostrar_resultados_simulacion(resultado)
        elif algoritmo == "Prioridades":
            resultado = self.prioridades()  # Ejecutar Prioridades
            self.mostrar_resultados_simulacion(resultado, tiene_prioridad=True)
        elif algoritmo == "Round Robin":
            resultado = self.round_robin()  # Ejecutar Round Robin
            self.mostrar_resultados_simulacion(resultado)
    
    # Algoritmo FIFO (First In, First Out)
    def fifo(self):
        procesos_ordenados = sorted(self.procesos, key=lambda x: x[2])  # Ordenar por tiempo de llegada
        return self.simular(procesos_ordenados)
    
    # Algoritmo SJF (Shortest Job First)
    def sjf(self):
        tiempo_actual = 1  # Comenzar en segundo 1
        resultados = []
        procesos_restantes = sorted(self.procesos, key=lambda x: x[2])  # Ordenar inicialmente por tiempo de llegada
        
        while procesos_restantes:
            # Filtrar procesos que han llegado
            procesos_disponibles = [p for p in procesos_restantes if p[2] <= tiempo_actual]
            
            if procesos_disponibles:
                # Procesar el proceso con la duración más corta
                proceso_a_procesar = min(procesos_disponibles, key=lambda x: x[1])
                procesos_restantes.remove(proceso_a_procesar)
                
                nombre_proceso, duracion, orden_llegada = proceso_a_procesar
                inicio = tiempo_actual
                tiempo_actual += duracion
                fin = tiempo_actual
                
                resultados.append((nombre_proceso, duracion, orden_llegada, inicio, fin))
            else:
                # Si no hay procesos disponibles, avanzar el tiempo al próximo proceso
                tiempo_actual = min(procesos_restantes, key=lambda x: x[2])[2]
        
        return resultados
    
    # Algoritmo Prioridades
    def prioridades(self):
        # Ordenar por prioridad (descendente) y tiempo de llegada (en caso de empate)
        procesos_ordenados = sorted(self.procesos, key=lambda x: (-x[3], x[2]))  # Prioridad descendente, luego llegada
        tiempo_actual = 1  # Comenzar en segundo 1
        registro_ejecucion = []
        
        # Se asegura que el primer proceso inicie en segundo 1
        for i, (nombre_proceso, duracion, orden_llegada, prioridad) in enumerate(procesos_ordenados):
            if i == 0:
                inicio = tiempo_actual  # El primer proceso inicia en segundo 1
            else:
                # Avanzar el tiempo si el proceso aún no ha llegado
                if tiempo_actual < orden_llegada:
                    tiempo_actual = orden_llegada
                inicio = tiempo_actual
            
            tiempo_actual += duracion
            fin = tiempo_actual
            registro_ejecucion.append((nombre_proceso, prioridad, duracion, orden_llegada, inicio, fin))
        
        return registro_ejecucion
    
    # Algoritmo Round Robin
    def round_robin(self):
        quantum = 3
        tiempo_actual = 1  # Comenzar en segundo 1
        resultados = []
        cola_procesos = self.procesos[:]
        tiempos_restantes = {p[0]: p[1] for p in self.procesos}  # Duración restante de cada proceso
        
        while cola_procesos:
            proceso = cola_procesos.pop(0)
            nombre_proceso, duracion, orden_llegada = proceso
            
            # Se asegura que el primer proceso inicie en segundo 1
            if tiempo_actual == 1 and resultados == []:
                inicio = tiempo_actual  # El primer proceso inicia en segundo 1
            else:
                # Avanzar el tiempo si el proceso aún no ha llegado
                if tiempo_actual < orden_llegada:
                    tiempo_actual = orden_llegada
                inicio = tiempo_actual
            
            # Si el proceso aún tiene tiempo restante
            tiempo_procesado = min(tiempos_restantes[nombre_proceso], quantum)
            tiempo_actual += tiempo_procesado
            tiempos_restantes[nombre_proceso] -= tiempo_procesado
            fin = tiempo_actual
            
            # Guardar el proceso en la tabla de resultados
            resultados.append((nombre_proceso, duracion, orden_llegada, inicio, fin))
            
            # Si el proceso no ha terminado, se vuelve a agregar a la cola
            if tiempos_restantes[nombre_proceso] > 0:
                cola_procesos.append(proceso)
        
        return resultados
    
    # Método para simular la ejecución de los procesos
    def simular(self, procesos_ordenados):
        tiempo = 1  # Comenzar en segundo 1
        registro_ejecucion = []
        
        for (nombre_proceso, duracion, orden_llegada) in procesos_ordenados:
            # Avanzar el tiempo si el proceso aún no ha llegado
            if tiempo < orden_llegada:
                tiempo = orden_llegada  # Esperar hasta que el proceso llegue
            inicio = tiempo
            tiempo += duracion
            fin = tiempo
            registro_ejecucion.append((nombre_proceso, duracion, orden_llegada, inicio, fin))  # Incluye el orden de llegada
            
        return registro_ejecucion
    
    # Mostrar los resultados de la simulación en la tabla
    def mostrar_resultados_simulacion(self, resultados, tiene_prioridad=False):
        self.tabla.setRowCount(len(resultados))
        
        # Configurar las columnas de acuerdo al algoritmo
        if tiene_prioridad:
            self.tabla.setColumnCount(6)
            self.tabla.setHorizontalHeaderLabels(["Proceso", "Prioridad", "Duración", "Llegada", "Inicio", "Fin"])
            for i, (nombre_proceso, prioridad, duracion, orden_llegada, inicio, fin) in enumerate(resultados):
                self.tabla.setItem(i, 0, QTableWidgetItem(nombre_proceso))
                self.tabla.setItem(i, 1, QTableWidgetItem(str(prioridad)))
                self.tabla.setItem(i, 2, QTableWidgetItem(str(duracion)))
                self.tabla.setItem(i, 3, QTableWidgetItem(str(orden_llegada)))
                self.tabla.setItem(i, 4, QTableWidgetItem(str(inicio)))
                self.tabla.setItem(i, 5, QTableWidgetItem(str(fin)))
        else:
            self.tabla.setColumnCount(5)
            self.tabla.setHorizontalHeaderLabels(["Proceso", "Duración", "Llegada", "Inicio", "Fin"])
            for i, (nombre_proceso, duracion, orden_llegada, inicio, fin) in enumerate(resultados):
                self.tabla.setItem(i, 0, QTableWidgetItem(nombre_proceso))
                self.tabla.setItem(i, 1, QTableWidgetItem(str(duracion)))
                self.tabla.setItem(i, 2, QTableWidgetItem(str(orden_llegada)))
                self.tabla.setItem(i, 3, QTableWidgetItem(str(inicio)))
                self.tabla.setItem(i, 4, QTableWidgetItem(str(fin)))
    
    # Método para agregar un nuevo proceso
    def agregar_proceso(self):
        nombre_proceso, ok1 = QInputDialog.getText(self, "Agregar Proceso", "Nombre del proceso:")
        if not ok1 or not nombre_proceso:
            return
        
        duracion, ok2 = QInputDialog.getInt(self, "Agregar Proceso", "Duración del proceso:")
        if not ok2:
            return
        
        orden_llegada, ok3 = QInputDialog.getInt(self, "Agregar Proceso", "Orden de llegada del proceso:")
        if not ok3:
            return

        # Para el algoritmo de Prioridades, solicitar prioridad
        prioridad = 0
        if self.comboBox.currentText() == "Prioridades":
            prioridad, ok4 = QInputDialog.getInt(self, "Agregar Proceso", "Prioridad del proceso (número entero):")
            if not ok4:
                return
        
        # Guardar el proceso en la lista y en el archivo correspondiente
        if self.comboBox.currentText() == "Prioridades":
            self.procesos.append((nombre_proceso, duracion, orden_llegada, prioridad))
            with open("Prioridades.txt", "a") as f:
                f.write(f"{nombre_proceso},{duracion},{orden_llegada},{prioridad}\n")
        else:
            self.procesos.append((nombre_proceso, duracion, orden_llegada))
            with open(f"{self.comboBox.currentText()}.txt", "a") as f:
                f.write(f"{nombre_proceso},{duracion},{orden_llegada}\n")

        QMessageBox.information(self, "Proceso agregado", f"El proceso '{nombre_proceso}' ha sido agregado.")

# Inicializar la aplicación
app = QApplication(sys.argv)
simulador = SimuladorDeProcesos()
simulador.show()
sys.exit(app.exec_())
