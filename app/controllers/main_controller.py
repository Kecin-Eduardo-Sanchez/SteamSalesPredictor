import tkinter as tk
import polars as pl
from app.views.vista1 import Vista1
from app.views.vista2 import Vista2
from app.views.vista3 import Vista3
from app.views.vistaWish import VistaWish
from app.views.InformeDetallado import InformeDetallado
from app.models.Charge_Data import DataModel 

class MainController:
    def __init__(self, view):
        self.view = view
        # 1. Inicializamos el modelo de datos
        self.modelo = DataModel() 
        
        # 2. Almacén global para persistencia entre vistas (Puntos Dulces)
        self.almacen_exito = {
            "dia_1": {"genero": None, "precio": 0.0},
            "semana_1": {"genero": None, "precio": 0.0}
        }

        # 3. Almacén para el Informe de Wishlist
        self.datos_wishlist = {
            "ratio_dia_1": 0.0,
            "ratio_semana_1": 0.0,
            "mediana_seguidores": 0
        }

        # 4. Diccionario de clases de vista
        self.vistas = {
            "Inicio": Vista1,
            "Informe de género": Vista2,
            "Visualización Dataset": Vista3,
            "Informe detallado": InformeDetallado,
            "Impacto de WishList": VistaWish
        }

    def show_view(self, view_name):
        """Gestiona el cambio de pantallas y sincroniza BI antes de informes."""
        
        # Sincronización total para el informe final
        if view_name == "Informe detallado":
            print("🔄 Sincronizando BI: Mercado + Wishlists...")
            self.actualizar_almacen_al_ultimo_anio()
            self.calcular_bi_wishlist()

        # Limpiar contenedor
        for widget in self.view.content_area.winfo_children():
            widget.destroy()
        
        # Instanciar la nueva vista
        if view_name in self.vistas:
            nueva_vista = self.vistas[view_name](self.view.content_area, self)
            nueva_vista.pack(fill="both", expand=True)

    def obtener_datos_crudos(self):
        """Método que llama VistaWish e InformeDetallado para sus cálculos."""
        return self.modelo.get_all_data()

    def obtener_inventario(self):
        """Entrega el DataFrame cargado a las vistas"""
        return self.modelo.get_all_data()

    def guardar_punto_dulce(self, fase, genero, precio):
        """Guarda resultados de mercado"""
        self.almacen_exito[fase] = {"genero": genero, "precio": precio}

    def calcular_bi_wishlist(self):
        """
        Calcula los ratios de conversión globales basados en la MEDIANA
        para que el Informe Detallado tenga datos que mostrar.
        """
        df = self.obtener_datos_crudos()
        if df is None or df.is_empty(): return

        try:
            # Filtro para evitar juegos sin datos (Alva Majo Style)
            df_base = df.filter(pl.col("Seguidores") > 100)
            
            # Cálculo de ratios medianos (Ventas / Seguidores)
            stats = df_base.select([
                (pl.col("Ventas Día 1") / pl.col("Seguidores")).median().alias("r_d1"),
                (pl.col("Ventas Sem. 1") / pl.col("Seguidores")).median().alias("r_s1"),
                pl.col("Seguidores").median().alias("m_seg")
            ])

            self.datos_wishlist.update({
                "ratio_dia_1": stats[0, "r_d1"] or 0.0,
                "ratio_semana_1": stats[0, "r_s1"] or 0.0,
                "mediana_seguidores": int(stats[0, "m_seg"] or 0)
            })
        except Exception as e:
            print(f"Error en calculo de wishlist: {e}")

    def actualizar_almacen_al_ultimo_anio(self):
        """Calcula puntos dulces de género y precio del año más reciente."""
        df = self.obtener_inventario()
        if df is None or df.is_empty(): return

        try:
            ultimo_anio = df.select(pl.col("Año")).max().to_series()[0]
            df_reciente = df.filter(pl.col("Año") == ultimo_anio)

            fases = [("Ventas Día 1", "dia_1"), ("Ventas Sem. 1", "semana_1")]

            for col_csv, fase_key in fases:
                temp_df = df_reciente.with_columns([
                    pl.col(col_csv).cast(pl.Float64, strict=False).fill_null(0),
                    pl.col("Precio (USD)").cast(pl.Float64, strict=False).fill_null(0)
                ])

                ranking = temp_df.group_by("Género (Tag)").agg(
                    pl.col(col_csv).sum().alias("V")
                ).sort("V", descending=True)
                
                if not ranking.is_empty() and ranking[0, "V"] > 0:
                    gen_top = ranking[0, "Género (Tag)"]
                    df_lider = temp_df.filter(pl.col("Género (Tag)") == gen_top)
                    
                    punto_d_data = df_lider.group_by("Precio (USD)").agg(
                        pl.col(col_csv).sum().alias("S")
                    ).sort("S", descending=True)
                    
                    punto_d = float(punto_d_data[0, "Precio (USD)"])
                    self.guardar_punto_dulce(fase_key, gen_top, punto_d)
            
            print(f"📊 Mercado Sincronizado ({ultimo_anio})")
        except Exception as e:
            print(f"⚠️ Error Mercado: {e}")