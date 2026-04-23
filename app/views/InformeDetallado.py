import tkinter as tk
from tkinter import ttk
import polars as pl

class InformeDetallado(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f4f7f6")

        # 1. Obtener datos y determinar el año del informe
        self.df = self.controller.obtener_datos_crudos()
        try:
            # Intentamos obtener el año que el usuario analizó en la VistaWish
            w_data = self.controller.almacen_exito.get("wishlist_reciente")
            if w_data:
                self.anio_act = w_data["anio"]
            else:
                self.anio_act = self.df.select(pl.col("Año")).max().to_series()[0]
        except:
            self.anio_act = "Actual"

        # 2. Configurar la interfaz con Scroll
        self.setup_ui()
        
        # 3. Generar el contenido
        self.generar_reporte_completo()

    def setup_ui(self):
        """Crea el header y el área de scroll."""
        # Header Estilo Alva Majo
        header = tk.Frame(self, bg="#2c3e50", pady=25)
        header.pack(fill="x")
        
        tk.Label(header, text="ESTRATEGIA FINAL DE LANZAMIENTO", 
                 font=("Helvetica", 18, "bold"), fg="#ecf0f1", bg="#2c3e50").pack()
        tk.Label(header, text=f"Reporte Consolidado - Periodo {self.anio_act}", 
                 font=("Helvetica", 10), fg="#bdc3c7", bg="#2c3e50").pack()

        # Sistema de Scroll
        self.canvas = tk.Canvas(self, bg="#f4f7f6", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.root_frame = tk.Frame(self.canvas, bg="#f4f7f6")

        self.root_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.root_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=20)
        self.scrollbar.pack(side="right", fill="y")

    def generar_reporte_completo(self):
        """Genera las 3 secciones clave del informe."""
        
        # --- DATOS DE ENTRADA ---
        g = self.controller.almacen_exito.get("semana_1", {"genero": "No definido", "precio": 0.0})
        w = self.controller.almacen_exito.get("wishlist_reciente")

        # --- PARTE 1: MERCADO Y POSICIONAMIENTO ---
        txt_mercado = (
            f"El análisis de mercado identifica a '{g['genero']}' como el nicho objetivo.\n\n"
            f"• Punto Dulce de Precio: ${g['precio']:.2f} USD.\n"
            f"• Competitividad: Este precio se sitúa en la mediana del género, lo que "
            f"favorece la conversión sin sacrificar el valor percibido del arte."
        )
        self.agregar_nota("PARTE 1: Análisis de Género y Mercado", txt_mercado, "#16a085")

        # --- PARTE 2: MÉTRICAS DE IMPACTO (DÍA 1 Y SEMANA 1) ---
        if w:
            # Cálculo de relevancia del día 1
            rel_d1 = (w['d1_num'] / w['s1_num'] * 100) if w['s1_num'] > 0 else 0
            
            txt_impacto = (
                f"Conversión basada en la Mediana de Wishlists ({w['wish']:,} seguidores):\n\n"
                f"• IMPACTO DÍA 1: {w['d1_num']:,.0f} ventas ({w['d1_porc']:.2f}% de conversión).\n"
                f"• TOTAL SEMANA 1: {w['s1_num']:,.0f} ventas ({w['s1_porc']:.2f}% de conversión).\n"
                f"• PESO DEL LANZAMIENTO: El primer día generó el {rel_d1:.1f}% de las ventas semanales.\n\n"
                f"• OPORTUNIDAD (REMANENTE): {w['rem_num']:,.0f} usuarios ({w['rem_porc']:.2f}%) "
                f"están en tu lista de deseados pero aún no han pasado por caja."
            )
        else:
            txt_impacto = "⚠️ No hay datos de Wishlist. Realice el análisis en la pestaña 'VistaWish' primero."
        
        self.agregar_nota("PARTE 2: Informe de Conversión y Hype", txt_impacto, "#2980b9")

        # --- PARTE 3: PLAN DE ACCIÓN Y CONCLUSIONES ---
        if w:
            # Lógica dinámica para el plan de acción
            status = "DÉBIL" if w['d1_porc'] < 5 else "SÓLIDO" if w['d1_porc'] < 12 else "EXPLOSIVO"
            
            txt_accion = (
                f"Estado del Hype Inicial: {status} ({w['d1_porc']:.1f}% en 24h).\n\n"
                f"1. ESTRATEGIA DE VISIBILIDAD: {'Mejorar el llamado a la acción y la cápsula' if w['d1_porc'] < 7 else 'Mantener actualizaciones constantes para alimentar el algoritmo'}.\n"
                f"2. GESTIÓN DEL REMANENTE: El {w['rem_porc']:.1f}% de tu audiencia acumulada es 'sensible al precio'. "
                f"Se recomienda un descuento del 20% en las próximas rebajas de Steam.\n"
                f"3. RECOMENDACIÓN: Si el algoritmo no duplica tus ventas externas en la semana 1, revisa los tags del juego."
            )
        else:
            txt_accion = "Realice los análisis previos para generar un plan de acción personalizado."

        self.agregar_nota("PARTE 3: Plan de Acción Sugerido", txt_accion, "#8e44ad")

    def agregar_nota(self, titulo, contenido, color):
        """Crea un bloque visual de información."""
        container = tk.Frame(self.root_frame, bg="white", padx=20, pady=20, 
                             highlightbackground="#dcdde1", highlightthickness=1)
        container.pack(fill="x", pady=10, padx=10)

        # Barra de color lateral
        tk.Frame(container, bg=color, width=6).pack(side="left", fill="y")

        # Área de texto
        text_area = tk.Frame(container, bg="white", padx=15)
        text_area.pack(side="left", fill="both", expand=True)

        tk.Label(text_area, text=titulo.upper(), font=("Arial", 11, "bold"), 
                 fg=color, bg="white").pack(anchor="w")
        
        tk.Label(text_area, text=contenido, font=("Segoe UI", 10), justify="left", 
                 bg="white", wraplength=500).pack(anchor="w", pady=(10, 0))