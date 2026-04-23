import tkinter as tk
from tkinter import ttk

class InformeDetallado(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f4f7f6")

        # 1. Obtener el año más reciente dinámicamente
        try:
            df = self.controller.obtener_inventario()
            self.anio_reciente = df.select("Año").max().to_series()[0]
        except:
            self.anio_reciente = "2024"

        datos_mercado = self.controller.almacen_exito
        
        # --- HEADER ---
        header = tk.Frame(self, bg="#34495e", pady=20)
        header.pack(fill="x")
        tk.Label(header, text=f"📋 REPORTE DE ESTRATEGIA: LANZAMIENTO {self.anio_reciente}", 
                 font=("Helvetica", 18, "bold"), fg="white", bg="#34495e").pack()

        # --- CONTENEDOR CON SCROLL ---
        self.canvas = tk.Canvas(self, bg="#f4f7f6", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f4f7f6")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=20)
        self.scrollbar.pack(side="right", fill="y")

        # 2. Dibujar las secciones (Notes)
        self.dibujar_secciones(datos_mercado)

    def dibujar_secciones(self, datos):
        # --- PARTE 1: INFORME DE GÉNERO (DATOS VISTA 2) ---
        if datos["semana_1"]["genero"]:
            contenido_genero = (
                f"Tras analizar el mercado del año {self.anio_reciente}, se concluye:\n\n"
                f"• GÉNERO DOMINANTE: {datos['semana_1']['genero']}\n"
                f"• PUNTO DULCE (Día 1): ${datos['dia_1']['precio']:.2f} USD\n"
                f"• PUNTO DULCE (Semana 1): ${datos['semana_1']['precio']:.2f} USD\n\n"
                f"Nota: Este género presenta la mejor relación de ventas vs. cantidad de juegos "
                f"desarrollados, lo que indica una demanda insatisfecha o alta rotación."
            )
        else:
            contenido_genero = "⚠️ No se han procesado datos en la Vista 2 (Informe de Género)."

        self.crear_nota("PARTE 1: Análisis de Género y Mercado", contenido_genero, "#16a085")

        # --- PARTE 2: INFORME DE WISHLIST (CONECTADO A VISTA WISH) ---
        # Aquí puedes usar el mismo sistema de 'almacen_exito' para traer datos de VistaWish
        contenido_wish = (
            "Este módulo analiza el impacto de los seguidores previos al lanzamiento.\n\n"
            "Estado: Sincronizado con el algoritmo de conversión. El volumen de Wishlists "
            "determinará si el Punto Dulce es alcanzable en el corto plazo."
        )
        self.crear_nota("PARTE 2: Informe de Wishlist e Impacto", contenido_wish, "#2980b9")

        # --- PARTE 3: PREDICCIÓN FINAL ---
        contenido_pred = (
            "Estimación de ingresos basada en regresión lineal y análisis correlacional.\n\n"
            "Resultado: En espera de parámetros de entrada."
        )
        self.crear_nota("PARTE 3: Modelo Predictivo de Ventas", contenido_pred, "#8e44ad")

    def crear_nota(self, titulo, contenido, color):
        """Estructura visual de Note para el informe"""
        frame_nota = tk.Frame(self.scrollable_frame, bg="white", relief="flat", padx=20, pady=15)
        frame_nota.pack(fill="x", pady=10, padx=10)

        # Barra de color lateral para indicar sección
        lado = tk.Frame(frame_nota, bg=color, width=6)
        lado.pack(side="left", fill="y")

        cuerpo = tk.Frame(frame_nota, bg="white", padx=15)
        cuerpo.pack(side="left", fill="both", expand=True)

        tk.Label(cuerpo, text=titulo.upper(), font=("Arial", 11, "bold"), 
                 bg="white", fg=color).pack(anchor="w")
        
        tk.Label(cuerpo, text=contenido, font=("Segoe UI", 10), bg="white", 
                 justify="left", wraplength=650).pack(anchor="w", pady=(8, 0))