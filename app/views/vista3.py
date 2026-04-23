import tkinter as tk
from tkinter import ttk, messagebox
import polars as pl

class Vista3(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Asumimos que el controlador ahora entrega un DataFrame de Polars
        self.df_original = self.controller.obtener_inventario()
        
        # --- PANEL DE BÚSQUEDA GRANULAR ---
        self.search_frame = tk.LabelFrame(self, text="Filtros Técnicos de Mercado (BI)", pady=10, padx=10)
        self.search_frame.pack(fill="x", padx=10, pady=5)

        for i in range(6): self.search_frame.columnconfigure(i, weight=1)

        # Fila 1: Nombre y Género
        tk.Label(self.search_frame, text="Nombre:").grid(row=0, column=0, sticky="w")
        self.ent_nombre = tk.Entry(self.search_frame)
        self.ent_nombre.grid(row=0, column=1, padx=5, sticky="ew")

        tk.Label(self.search_frame, text="Género:").grid(row=0, column=2, sticky="w")
        self.ent_genero = tk.Entry(self.search_frame)
        self.ent_genero.grid(row=0, column=3, padx=5, sticky="ew")

        # Fila 2: Año y Precio
        tk.Label(self.search_frame, text="Año (Min - Max):").grid(row=1, column=0, pady=10, sticky="w")
        self.frame_anio = tk.Frame(self.search_frame)
        self.frame_anio.grid(row=1, column=1, sticky="w")
        self.ent_anio_min = tk.Entry(self.frame_anio, width=6); self.ent_anio_min.pack(side="left")
        self.ent_anio_max = tk.Entry(self.frame_anio, width=6); self.ent_anio_max.pack(side="left", padx=5)

        tk.Label(self.search_frame, text="Precio $ (Min - Max):").grid(row=1, column=2, sticky="w")
        self.frame_precio = tk.Frame(self.search_frame)
        self.frame_precio.grid(row=1, column=3, sticky="w")
        self.ent_pre_min = tk.Entry(self.frame_precio, width=6); self.ent_pre_min.pack(side="left")
        self.ent_pre_max = tk.Entry(self.frame_precio, width=6); self.ent_pre_max.pack(side="left", padx=5)

        # Fila 3: Wishlists y Seguidores
        tk.Label(self.search_frame, text="Wishlists (Min - Max):").grid(row=2, column=0, pady=5, sticky="w")
        self.frame_wish = tk.Frame(self.search_frame)
        self.frame_wish.grid(row=2, column=1, sticky="w")
        self.ent_wish_min = tk.Entry(self.frame_wish, width=8); self.ent_wish_min.pack(side="left")
        self.ent_wish_max = tk.Entry(self.frame_wish, width=8); self.ent_wish_max.pack(side="left", padx=5)

        tk.Label(self.search_frame, text="Seguidores (Min - Max):").grid(row=2, column=2, sticky="w")
        self.frame_seg = tk.Frame(self.search_frame)
        self.frame_seg.grid(row=2, column=3, sticky="w")
        self.ent_seg_min = tk.Entry(self.frame_seg, width=8); self.ent_seg_min.pack(side="left")
        self.ent_seg_max = tk.Entry(self.frame_seg, width=8); self.ent_seg_max.pack(side="left", padx=5)

        # Botones
        self.btn_buscar = tk.Button(self.search_frame, text="Filtrar Mercado", command=self.ejecutar_busqueda, bg="#27ae60", fg="white", font=("Arial", 10, "bold"))
        self.btn_buscar.grid(row=0, column=4, rowspan=2, padx=10, sticky="nsew")
        
        self.btn_reset = tk.Button(self.search_frame, text="Limpiar Filtros", command=self.limpiar_filtro)
        self.btn_reset.grid(row=2, column=4, padx=10, sticky="ew")

        # --- CONTENEDOR DE TABLA ---
        self.container = tk.Frame(self)
        self.container.pack(padx=10, pady=10, fill="both", expand=True)
        self.crear_tabla(self.df_original)

    def ejecutar_busqueda(self):
        try:
            # En Polars, trabajamos con el DataFrame original directamente para filtrar
            df = self.df_original
            
            # 1. Filtros de Texto (Case-insensitive)
            if self.ent_nombre.get():
                nombre = self.ent_nombre.get().lower()
                df = df.filter(pl.col('Nombre del Juego').str.to_lowercase().str.contains(nombre))
            
            if self.ent_genero.get():
                genero = self.ent_genero.get().lower()
                df = df.filter(pl.col('Género (Tag)').str.to_lowercase().str.contains(genero))

            # 2. Lógica de Rangos con Polars (Más limpia que en Pandas)
            def aplicar_rango(polars_df, columna, min_e, max_e):
                res_df = polars_df
                if min_e.get():
                    res_df = res_df.filter(pl.col(columna) >= float(min_e.get()))
                if max_e.get():
                    res_df = res_df.filter(pl.col(columna) <= float(max_e.get()))
                return res_df

            # Aplicar filtros numéricos en cascada
            df = aplicar_rango(df, 'Año', self.ent_anio_min, self.ent_anio_max)
            df = aplicar_rango(df, 'Precio (USD)', self.ent_pre_min, self.ent_pre_max)
            df = aplicar_rango(df, 'Wishlists', self.ent_wish_min, self.ent_wish_max)
            df = aplicar_rango(df, 'Seguidores', self.ent_seg_min, self.ent_seg_max)

            self.actualizar_tabla(df)
            
        except ValueError:
            messagebox.showerror("Error", "Asegúrese de ingresar solo números en los campos de rango.")

    def crear_tabla(self, df):
        columnas = list(df.columns)
        self.tabla = ttk.Treeview(self.container, columns=columnas, show='headings')
        
        s_y = ttk.Scrollbar(self.container, orient="vertical", command=self.tabla.yview)
        s_x = ttk.Scrollbar(self.container, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=s_y.set, xscrollcommand=s_x.set)

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=120, anchor="center")

        s_x.pack(side="bottom", fill="x")
        s_y.pack(side="right", fill="y")
        self.tabla.pack(side="left", fill="both", expand=True)
        self.actualizar_tabla(df)

    def actualizar_tabla(self, df):
        # Limpiar tabla
        for i in self.tabla.get_children(): self.tabla.delete(i)
        
        # Polars: iter_rows() es extremadamente eficiente para llenar widgets
        # Nos devuelve una lista de tuplas directamente
        for fila in df.iter_rows():
            self.tabla.insert("", "end", values=fila)

    def limpiar_filtro(self):
        for e in [self.ent_nombre, self.ent_genero, self.ent_anio_min, self.ent_anio_max, 
                  self.ent_pre_min, self.ent_pre_max, self.ent_wish_min, self.ent_wish_max, 
                  self.ent_seg_min, self.ent_seg_max]:
            e.delete(0, tk.END)
        self.actualizar_tabla(self.df_original)