import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import os
from generador import GeneradorCasosPrueba

class InterfazGenerador:
    """Interfaz gráfica para el generador de casos de prueba."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Generador Automático de Casos de Prueba")
        self.root.geometry("900x700")
        self.generador = GeneradorCasosPrueba()
        self.archivo_gramatica = None
        self.crear_interfaz()
    
    def crear_interfaz(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        ttk.Label(main_frame, text="Generador de Casos de Prueba desde Gramática", 
                  font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=3, pady=10)
        
        # Sección 1: Cargar Gramática
        self._crear_seccion_gramatica(main_frame)
        
        # Sección 2: Configuración
        self._crear_seccion_configuracion(main_frame)
        
        # Botón Generar
        ttk.Button(main_frame, text="3. GENERAR CASOS", command=self.generar,
                   style='Accent.TButton').grid(row=3, column=0, columnspan=3, 
                                                 pady=15, ipadx=20, ipady=10)
        
        # Área de resultados
        self._crear_seccion_resultados(main_frame)
        
        # Botones de exportación
        self._crear_botones_exportacion(main_frame)
        
        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
    
    def _crear_seccion_gramatica(self, parent):
        frame = ttk.LabelFrame(parent, text="1. Cargar Gramática", padding="10")
        frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(frame, text="Seleccionar archivo .txt", 
                  command=self.cargar_gramatica).grid(row=0, column=0, padx=5)
        
        self.label_archivo = ttk.Label(frame, text="Ningún archivo cargado", foreground="red")
        self.label_archivo.grid(row=0, column=1, padx=5)
    
    def _crear_seccion_configuracion(self, parent):
        frame = ttk.LabelFrame(parent, text="2. Configuración", padding="10")
        frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Configuraciones con valores por defecto
        configs = [
            ("Cantidad de casos:", "spin_cantidad", 1, 1000, 20),
            ("Profundidad máxima:", "spin_profundidad", 1, 30, 5),
            ("Longitud máxima (tokens):", "spin_longitud", 5, 200, 50),
            ("% Casos válidos:", "spin_validos", 0, 100, 50),
            ("% Casos inválidos:", "spin_invalidos", 0, 100, 30)
        ]
        
        for i, (label, attr, from_, to, default) in enumerate(configs):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            spin = ttk.Spinbox(frame, from_=from_, to=to, width=10)
            spin.set(default)
            spin.grid(row=i, column=1, padx=5, pady=2)
            setattr(self, attr, spin)
        
        ttk.Label(frame, text="(Resto = casos extremos)", 
                 font=('Arial', 8, 'italic')).grid(row=5, column=1, sticky=tk.W)
    
    def _crear_seccion_resultados(self, parent):
        frame = ttk.LabelFrame(parent, text="4. Resultados", padding="10")
        frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.texto_resultados = scrolledtext.ScrolledText(frame, height=15, width=100)
        self.texto_resultados.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar estilos de texto
        self.texto_resultados.tag_config("error", foreground="red", font=('Arial', 10, 'bold'))
        self.texto_resultados.tag_config("success", foreground="green", font=('Arial', 10))
        self.texto_resultados.tag_config("warning", foreground="orange", font=('Arial', 10))
    
    def _crear_botones_exportacion(self, parent):
        frame = ttk.Frame(parent)
        frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        ttk.Button(frame, text="Exportar JSON", 
                  command=self.exportar_json).grid(row=0, column=0, padx=5)
        ttk.Button(frame, text="Exportar Reporte TXT", 
                  command=self.exportar_reporte).grid(row=0, column=1, padx=5)
    
    def cargar_gramatica(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar gramática",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos", "*.*")]
        )
        if archivo and self.generador.cargar_gramatica(archivo):
            self.archivo_gramatica = archivo
            self.label_archivo.config(text=f"✓ {os.path.basename(archivo)}", foreground="green")
        elif archivo:
            self.label_archivo.config(text="✗ Error al cargar gramática", foreground="red")
    
    def generar(self):
        if not self.generador.gramatica:
            self.texto_resultados.delete(1.0, tk.END)
            self.texto_resultados.insert(tk.END, "❌ ERROR: Primero debes cargar una gramática\n", "error")
            return
        
        try:
            cantidad = int(self.spin_cantidad.get())
            profundidad = int(self.spin_profundidad.get())
            longitud = int(self.spin_longitud.get())
            dist_valida = float(self.spin_validos.get())
            dist_invalida = float(self.spin_invalidos.get())
            
            if dist_valida + dist_invalida > 100:
                self.texto_resultados.delete(1.0, tk.END)
                self.texto_resultados.insert(tk.END, "❌ ERROR: Válidos + Inválidos no puede superar 100%\n", "error")
                return
            
            self.texto_resultados.delete(1.0, tk.END)
            self.texto_resultados.insert(tk.END, "⏳ Generando casos...\n")
            self.root.update()
            
            # Configurar y generar
            self.generador.configurar(profundidad, longitud, dist_valida, dist_invalida)
            self.generador.generar_casos(cantidad)
            
            self._mostrar_reporte()
            
        except ValueError as e:
            self.texto_resultados.delete(1.0, tk.END)
            self.texto_resultados.insert(tk.END, f"❌ ERROR: Valores inválidos - {e}\n", "error")
    
    def _mostrar_reporte(self):
        reporte = self.generador.generar_reporte()
        self.texto_resultados.delete(1.0, tk.END)
        
        texto = f"""{'='*70}
GENERACIÓN COMPLETADA
{'='*70}

Total: {reporte['total_casos']} casos
Tiempo: {reporte['tiempo_ejecucion_total_segundos']}s

DISTRIBUCIÓN:
"""
        for tipo, porc in reporte['distribucion_porcentual'].items():
            num = reporte['distribucion_numerica'][tipo.replace('s', '')]
            texto += f"  • {tipo.capitalize()}: {num} ({porc})\n"
        
        texto += f"""
MÉTRICAS:
  Longitud promedio: {reporte['longitud_promedio_tokens']:.2f} tokens
  Longitud máxima: {reporte['longitud_maxima_tokens']} tokens
  Profundidad máxima: {reporte['profundidad_maxima_arbol']}
  Profundidad promedio: {reporte['profundidad_promedio_arbol']:.2f}
  Anidamiento promedio: {reporte['nivel_anidamiento_promedio']:.2f}

OPERADORES:
"""
        for op, count in reporte['operadores_generados_total'].items():
            texto += f"  {op}: {count}\n"
        
        if reporte['mutaciones_aplicadas']:
            texto += "\nMUTACIONES:\n"
            for mut, count in reporte['mutaciones_aplicadas'].items():
                texto += f"  {mut}: {count}\n"
        
        self.texto_resultados.insert(tk.END, texto)
    
    def exportar_json(self):
        if not self.generador.resultados:
            self.texto_resultados.delete(1.0, tk.END)
            self.texto_resultados.insert(tk.END, "⚠️ No hay casos para exportar\n", "warning")
            return
        
        archivo = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")]
        )
        if archivo:
            self.generador.exportar_json(archivo)
            self.texto_resultados.insert(tk.END, f"\n✓ JSON exportado: {os.path.basename(archivo)}\n", "success")
    
    def exportar_reporte(self):
        if not self.generador.resultados:
            self.texto_resultados.delete(1.0, tk.END)
            self.texto_resultados.insert(tk.END, "⚠️ No hay reporte para exportar\n", "warning")
            return
        
        archivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
        )
        if archivo:
            self.generador.exportar_reporte_txt(archivo)
            self.texto_resultados.insert(tk.END, f"\n✓ Reporte exportado: {os.path.basename(archivo)}\n", "success")


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazGenerador(root)
    root.mainloop()