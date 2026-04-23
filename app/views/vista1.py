import tkinter as tk
from tkinter import ttk

class Vista1(tk.Frame):
    def __init__(self, parent, controller): 
        # Aplicamos el color de fondo azul oscuro estilo Steam
        super().__init__(parent, bg="#1b2838") 
        self.controller = controller 
        
        # Contenedor principal con margen interno para que no quede pegado a los bordes
        contenedor = tk.Frame(self, bg="#1b2838", padx=40, pady=40)
        contenedor.pack(fill="both", expand=True)
        
        # 1. TÍTULO DE BIENVENIDA
        titulo = tk.Label(
            contenedor, 
            text="¡Bienvenido a Steam Sales Predictor!", 
            font=("Helvetica", 24, "bold"), 
            fg="#66c0f4", # Celeste característico de Steam
            bg="#1b2838"
        )
        titulo.pack(anchor="w", pady=(0, 20))
        
        # 2. MOTIVOS DEL SOFTWARE
        motivos_titulo = tk.Label(
            contenedor, 
            text="Motivos y Objetivos del Software", 
            font=("Helvetica", 14, "bold"), 
            fg="#ffffff", 
            bg="#1b2838"
        )
        motivos_titulo.pack(anchor="w", pady=(10, 5))
        
        texto_motivos = (
            "Esta herramienta fue desarrollada con el propósito de mitigar el riesgo comercial de los "
            "desarrolladores independientes en la plataforma Steam. A través del análisis de datos históricos "
            "y técnicas de Business Intelligence, el software permite identificar los 'puntos dulces' de precios "
            "y predecir la conversión de listas de deseados (Wishlists) en ventas reales durante el lanzamiento."
        )
        
        # Nota: wraplength=700 obliga al texto a saltar de línea para no salirse de la pantalla
        motivos_lbl = tk.Label(
            contenedor, 
            text=texto_motivos, 
            font=("Helvetica", 11), 
            fg="#c7d5e0", # Gris azulado claro para lectura cómoda
            bg="#1b2838",
            wraplength=700,
            justify="left"
        )
        motivos_lbl.pack(anchor="w", pady=(0, 20))
        
        # Línea divisoria elegante
        separador = ttk.Separator(contenedor, orient="horizontal")
        separador.pack(fill="x", pady=10)
        
        # 3. MARCO LEGAL
        legal_titulo = tk.Label(
            contenedor, 
            text="Marco Legal y Protección de Datos", 
            font=("Helvetica", 14, "bold"), 
            fg="#ffffff", 
            bg="#1b2838"
        )
        legal_titulo.pack(anchor="w", pady=(10, 5))
        
        texto_legal = (
            "En cumplimiento de las normativas de la República de Colombia y los lineamientos de la "
            "Corporación Unificada Nacional de Educación Superior (CUN), este proyecto se acoge a:\n\n"
            "• Ley 23 de 1982 y Decisión Andina 351: Protección a los derechos de autor del código fuente.\n"
            "• Ley 1581 de 2012 (Habeas Data): Manejo responsable y protección de datos personales.\n"
            "• Uso de Datos Públicos: Toda la información analizada proviene de métricas públicas de la plataforma Steam."
        )
        
        legal_lbl = tk.Label(
            contenedor, 
            text=texto_legal, 
            font=("Helvetica", 11), 
            fg="#c7d5e0", 
            bg="#1b2838",
            wraplength=700,
            justify="left"
        )
        legal_lbl.pack(anchor="w", pady=(0, 20))
        
        # 4. INSTRUCCIÓN FINAL
        instruccion = tk.Label(
            contenedor, 
            text="Usa el menú lateral para comenzar a explorar los módulos del sistema.", 
            font=("Helvetica", 11, "italic"), 
            fg="#107c10", # Un verde sutil que denota acción
            bg="#1b2838"
        )
        instruccion.pack(anchor="w", pady=(20, 0))