import tkinter as tk
from tkinter import ttk
import polars as pl

class VistaWish(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f8f9fa")
        
        # 1. Obtener años disponibles para el selector
        self.df_completo = self.controller.obtener_datos_crudos()
        self.anios_disponibles = sorted(self.df_completo.select(pl.col("Año")).unique().to_series().to_list(), reverse=True)
        
        # Año por defecto (el más reciente)
        self.anio_seleccionado = tk.StringVar(value=str(self.anios_disponibles[0]) if self.anios_disponibles else "")

        # 2. Setup Scroll con centrado
        self.setup_scroll_centrado()
        
        # 3. Render Inicial
        self.actualizar_vista()

    def setup_scroll_centrado(self):
        self.canvas = tk.Canvas(self, bg="#f8f9fa", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f8f9fa")

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def ejecutar_logica_wishlist(self, anio):
        """Calcula métricas filtradas por el año seleccionado."""
        if self.df_completo.is_empty(): return None
        
        df_filt = self.df_completo.filter(pl.col("Año") == int(anio))
        if df_filt.is_empty(): return None

        m_wish = df_filt.select(pl.col("Wishlists").median()).to_series()[0]
        m_d1 = df_filt.select(pl.col("Ventas Día 1").median()).to_series()[0]
        m_s1 = df_filt.select(pl.col("Ventas Sem. 1").median()).to_series()[0]
        
        p_d1 = (m_d1 / m_wish * 100) if m_wish > 0 else 0
        p_s1 = (m_s1 / m_wish * 100) if m_wish > 0 else 0
        
        resultados = {
            "anio": anio,
            "wish": m_wish,
            "d1_num": m_d1, "d1_porc": p_d1,
            "s1_num": m_s1, "s1_porc": p_s1,
            "rem_num": m_wish - m_s1, "rem_porc": max(0, 100 - p_s1)
        }

        # GUARDAR EN EL CONTROLADOR PARA EL INFORME DETALLADO
        # Asumiendo que tu controlador tiene este diccionario
        self.controller.almacen_exito["wishlist_reciente"] = resultados
        
        return resultados

    def actualizar_vista(self, *args):
        """Limpia el contenido actual y vuelve a renderizar con el año seleccionado."""
        # Limpiar frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Recalcular
        self.datos = self.ejecutar_logica_wishlist(self.anio_seleccionado.get())
        
        # Renderizar
        self.configurar_interfaz()

    def configurar_interfaz(self):
        # --- SELECTOR DE AÑO ---
        selector_frame = tk.Frame(self.scrollable_frame, bg="#f8f9fa")
        selector_frame.pack(pady=10)
        
        tk.Label(selector_frame, text="Seleccionar Año:", bg="#f8f9fa", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        combo = ttk.Combobox(selector_frame, textvariable=self.anio_seleccionado, values=self.anios_disponibles, state="readonly", width=10)
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", self.actualizar_vista)

        if not self.datos:
            tk.Label(self.scrollable_frame, text="⚠️ No hay datos para este periodo", bg="#f8f9fa").pack(pady=50)
            return

        # --- CONTENEDOR DE IMPACTO ---
        main_container = tk.Frame(self.scrollable_frame, bg="#f8f9fa")
        main_container.pack(pady=10, padx=20, expand=True)

        tk.Label(main_container, text=f"ANÁLISIS DE IMPACTO {self.datos['anio']}", 
                 font=("Helvetica", 16, "bold"), bg="#f8f9fa", fg="#2c3e50").pack(pady=5)

        # Gráfica
        self.canvas_pie = tk.Canvas(main_container, width=240, height=240, bg="#f8f9fa", highlightthickness=0)
        self.canvas_pie.pack(pady=10)
        self.dibujar_pastel()

        # Leyenda
        leyenda = tk.Frame(main_container, bg="#f8f9fa")
        leyenda.pack(pady=5)
        for txt, col in [("Día 1", "#e74c3c"), ("Semana 1", "#27ae60"), ("Remanente", "#dcdde1")]:
            f = tk.Frame(leyenda, bg="#f8f9fa", padx=10)
            f.pack(side="left")
            tk.Frame(f, bg=col, width=12, height=12).pack(side="left", padx=5)
            tk.Label(f, text=txt, font=("Arial", 9, "bold"), bg="#f8f9fa", fg="#57606f").pack(side="left")

        # Card Métricas
        card = tk.Frame(main_container, bg="white", padx=30, pady=20, relief="flat", highlightbackground="#dcdde1", highlightthickness=1)
        card.pack(pady=20, fill="x")

        self.crear_fila(card, "MEDIANA TOTAL WISHLISTS", self.datos['wish'], "100%", "#34495e", True)
        tk.Frame(card, bg="#f1f2f6", height=1).pack(fill="x", pady=10)
        self.crear_fila(card, "Ventas Día 1:", self.datos['d1_num'], f"{self.datos['d1_porc']:.2f}%", "#e74c3c")
        self.crear_fila(card, "Ventas Semana 1:", self.datos['s1_num'], f"{self.datos['s1_porc']:.2f}%", "#27ae60")
        self.crear_fila(card, "Remanente (No compraron):", self.datos['rem_num'], f"{self.datos['rem_porc']:.2f}%", "#7f8c8d")

        # Nota
        nota_frame = tk.Frame(main_container, bg="#eef2f3", padx=20, pady=20)
        nota_frame.pack(pady=20, fill="x")
        tk.Label(nota_frame, text="💡 NOTA METODOLÓGICA", font=("Arial", 9, "bold"), bg="#eef2f3", fg="#2980b9").pack(anchor="w")
        
        txt_expl = ("Análisis basado en la Mediana de Wishlists (100%). "
                    "El área roja es el impacto inmediato, la verde el residual de semana 1, "
                    "y la gris la audiencia que aún no convierte.")
        
        tk.Label(nota_frame, text=txt_expl, font=("Arial", 9, "italic"), bg="#eef2f3", fg="#34495e", justify="center", wraplength=450).pack(pady=(5, 0))

    def dibujar_pastel(self):
        d = self.datos
        g_d1 = (d['d1_porc'] * 360) / 100
        g_s1_extra = ((d['s1_porc'] - d['d1_porc']) * 360) / 100
        g_rem = (d['rem_porc'] * 360) / 100
        coord = (10, 10, 230, 230)
        inicio = 0
        self.canvas_pie.create_arc(coord, start=inicio, extent=g_d1, fill="#e74c3c", outline="white", width=2)
        inicio += g_d1
        self.canvas_pie.create_arc(coord, start=inicio, extent=g_s1_extra, fill="#27ae60", outline="white", width=2)
        inicio += g_s1_extra
        self.canvas_pie.create_arc(coord, start=inicio, extent=g_rem, fill="#dcdde1", outline="white", width=2)

    def crear_fila(self, parent, label, num, porc, color, bold=False):
        f = tk.Frame(parent, bg="white")
        f.pack(fill="x", pady=4)
        fuente = ("Arial", 10, "bold") if bold else ("Arial", 10)
        tk.Label(f, text=label, font=fuente, bg="white", fg="#4b4b4b", width=25, anchor="w").pack(side="left")
        tk.Label(f, text=f"{num:,.0f}", font=("Arial", 11, "bold"), bg="white", fg="#2c3e50", width=12, anchor="e").pack(side="left")
        tk.Label(f, text=porc, font=("Arial", 11, "bold"), bg="white", fg=color, width=12, anchor="e").pack(side="left")