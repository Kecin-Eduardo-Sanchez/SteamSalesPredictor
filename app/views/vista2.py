import tkinter as tk
from tkinter import ttk
import polars as pl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class Vista2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.df_completo = self.controller.obtener_inventario()
        
        # --- HEADER ---
        header = tk.Frame(self, bg="#2c3e50", pady=15)
        header.pack(fill="x")
        
        tk.Label(header, text="📖 Análisis de Mercado: Punto Dulce (Motor Polars)", 
                 font=("Arial", 16, "bold"), bg="#2c3e50", fg="white").pack(side="left", padx=25)
        
        try:
            años = self.df_completo.select(pl.col("Año")).unique().sort("Año", descending=True).to_series().to_list()
        except:
            años = [2024]

        self.var_anio = tk.StringVar(value=años[0] if años else "2024")
        self.combo_anio = ttk.Combobox(header, textvariable=self.var_anio, values=años, state="readonly", width=10, font=("Arial", 11))
        self.combo_anio.pack(side="left", padx=20)
        self.combo_anio.bind("<<ComboboxSelected>>", lambda e: self.actualizar_analisis())

        # --- CONTENEDOR SCROLLABLE ---
        self.outer_canvas = tk.Canvas(self, bg="#ecf0f1", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.outer_canvas.yview)
        self.scrollable_content = tk.Frame(self.outer_canvas, bg="#ecf0f1")
        
        self.canvas_window = self.outer_canvas.create_window((0, 0), window=self.scrollable_content, anchor="nw")
        self.scrollable_content.bind("<Configure>", lambda e: self.outer_canvas.configure(scrollregion=self.outer_canvas.bbox("all")))
        self.outer_canvas.bind('<Configure>', lambda e: self.outer_canvas.itemconfig(self.canvas_window, width=e.width))
        
        self.outer_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.outer_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.outer_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Para Linux (usa eventos distintos)
        self.outer_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.outer_canvas.bind_all("<Button-5>", self._on_mousewheel)

        self.actualizar_analisis()

    def _on_mousewheel(self, event):
        # En Windows, event.delta es 120 o -120. En Linux se usan Button 4/5.
        if event.num == 4: # Linux scroll up
            self.outer_canvas.yview_scroll(-1, "units")
        elif event.num == 5: # Linux scroll down
            self.outer_canvas.yview_scroll(1, "units")
        else: # Windows / MacOS
            self.outer_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def actualizar_analisis(self):
        for widget in self.scrollable_content.winfo_children():
            widget.destroy()
            
        try:
            anio_sel = int(self.var_anio.get())
            df_anio = self.df_completo.filter(pl.col("Año") == anio_sel)
            if df_anio.is_empty(): return

            libro_frame = tk.Frame(self.scrollable_content, bg="#ecf0f1")
            libro_frame.pack(fill="both", expand=True, padx=10, pady=10)
            libro_frame.columnconfigure(0, weight=1); libro_frame.columnconfigure(1, weight=1)

            fases = [("Ventas Día 1", "Día 1", "#16a085"), ("Ventas Sem. 1", "Semana 1", "#2980b9")]
            for i, (col_data, nombre, color) in enumerate(fases):
                frame_fase = tk.Frame(libro_frame, bg="white", relief="ridge", bd=2)
                frame_fase.grid(row=0, column=i, sticky="nsew", padx=15, pady=10)
                self.generar_bloque_fase(frame_fase, df_anio, col_data, nombre, color)
                self.generar_tabla_ranking(self.scrollable_content, df_anio)
        except Exception as e: print(f"Error General: {e}")

    def generar_bloque_fase(self, parent, df, columna, nombre_fase, color_tema):
        try:
            tk.Label(parent, text=f"ANÁLISIS {nombre_fase.upper()}", font=("Arial", 14, "bold"), 
                     fg="white", bg=color_tema, pady=15).pack(fill="x")

            df = df.with_columns([
                pl.col(columna).cast(pl.Float64, strict=False).fill_null(0),
                pl.col("Precio (USD)").cast(pl.Float64, strict=False).fill_null(0)
            ])

            ranking = df.group_by("Género (Tag)").agg(pl.col(columna).sum().alias("V")).sort("V", descending=True).filter(pl.col("V") > 0)
            if ranking.is_empty(): return

            gen_top = ranking[0, "Género (Tag)"]
            total_v = int(ranking[0, "V"])
            df_lider = df.filter(pl.col("Género (Tag)") == gen_top)
            conteo = df_lider.height
            
            punto_d_data = df_lider.group_by("Precio (USD)").agg(pl.col(columna).sum().alias("S")).sort("S", descending=True)
            punto_d = float(punto_d_data[0, "Precio (USD)"])

            # --- GUARDADO PARA INFORME ---
            fase_id = "dia_1" if "Día" in nombre_fase else "semana_1"
            self.controller.guardar_punto_dulce(fase_id, gen_top, punto_d)

            # Texto de reporte
            txt_frame = tk.Frame(parent, bg="white", padx=20, pady=20)
            txt_frame.pack(fill="x")
            txt = (f"Para el periodo de {nombre_fase}, el género más vendido fue '{gen_top}' "
                   f"con un total de {total_v:,} ventas y con {conteo} juegos lanzados.\n\n"
                   f"PUNTO DULCE detectado: ${punto_d:.2f} USD.")
            tk.Label(txt_frame, text=txt, wraplength=400, justify="left", font=("Segoe UI", 10), bg="white").pack()

            # Gráfica Ranking
            nombres = ranking["Género (Tag)"].to_list()[:12][::-1]
            valores = ranking["V"].to_list()[:12][::-1]
            self.crear_grafica_manual(parent, nombres, valores, f"Ranking {nombre_fase}", color_tema, "barh")

            # Gráfica Punto Dulce
            precios_df = df_lider.group_by("Precio (USD)").agg(pl.col(columna).sum().alias("S")).sort("Precio (USD)")
            px = [f"${p:.2f}" for p in precios_df["Precio (USD)"].to_list()]
            py = precios_df["S"].to_list()
            self.crear_grafica_manual(parent, px, py, f"Punto Dulce en {gen_top}", "#e67e22", "bar")

        except Exception as e: print(f"Error en bloque: {e}")


    def generar_tabla_ranking(self, parent, df):
        """Nueva sección para listar todos los géneros y sus puntos dulces"""
        contenedor_tabla = tk.Frame(parent, bg="white", relief="groove", bd=1)
        contenedor_tabla.pack(fill="x", padx=25, pady=20)

        tk.Label(contenedor_tabla, text="📊 DESGLOSE POR GÉNERO Y PUNTO DULCE (SEMANA 1)", 
                 font=("Arial", 12, "bold"), bg="#34495e", fg="white", pady=10).pack(fill="x")

        # Columnas de la tabla
        cols = ("Género", "Juegos", "Ventas Totales (S1)", "Punto Dulce (USD)")
        tree = ttk.Treeview(contenedor_tabla, columns=cols, show="headings", height=10)
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)
        
        # Procesamiento de datos para la tabla
        generos_unicos = df.select(pl.col("Género (Tag)")).unique().to_series().to_list()
        datos_tabla = []

        for gen in generos_unicos:
            df_gen = df.filter(pl.col("Género (Tag)") == gen)
            v_totales = df_gen.select(pl.col("Ventas Sem. 1").sum()).to_series()[0]
            num_juegos = df_gen.height
            
            # Calcular Punto Dulce para este género específico
            pd_data = df_gen.group_by("Precio (USD)").agg(pl.col("Ventas Sem. 1").sum().alias("S")).sort("S", descending=True)
            pd = pd_data[0, "Precio (USD)"] if not pd_data.is_empty() else 0.0
            
            datos_tabla.append((gen, num_juegos, int(v_totales), f"${pd:.2f}"))

        # Ordenar por ventas de mayor a menor
        datos_tabla.sort(key=lambda x: x[2], reverse=True)

        for item in datos_tabla:
            tree.insert("", "end", values=item)

        tree.pack(fill="x", padx=10, pady=10)

    def crear_grafica_manual(self, parent, x_data, y_data, titulo, color, tipo):
        fig = Figure(figsize=(5, 3.5), dpi=85)
        ax = fig.add_subplot(111)
        if tipo == "barh":
            ax.barh(x_data, y_data, color=color, edgecolor="black", alpha=0.8)
        else:
            ax.bar(x_data, y_data, color=color, edgecolor="black", alpha=0.8)
            ax.tick_params(axis='x', labelsize=7, rotation=45)
        ax.set_title(titulo, fontsize=10, fontweight='bold')
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=10, pady=5)