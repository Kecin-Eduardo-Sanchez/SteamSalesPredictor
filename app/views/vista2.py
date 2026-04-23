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

        self.actualizar_analisis()

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