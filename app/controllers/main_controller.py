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

        # 3. Diccionario de clases de vista
        self.vistas = {
            "Inicio": Vista1,
            "Informe de género": Vista2,
            "Visualización Dataset": Vista3,
            "Informe detallado": InformeDetallado,
            "Impacto de WishList": VistaWish
        }

    def show_view(self, view_name):
        """
        Gestiona el cambio de pantallas y asegura que los datos 
        estén actualizados antes de mostrar informes.
        """
        
        # LÓGICA DE NEGOCIO: Si el usuario va al informe, forzamos datos del año actual (2024)
        if view_name == "Informe detallado":
            print("🔄 Sincronizando datos del año más reciente para el Informe Detallado...")
            self.actualizar_almacen_al_ultimo_anio()

        # Limpiar contenedor (área de contenido en la UI)
        for widget in self.view.content_area.winfo_children():
            widget.destroy()
        
        # Instanciar la nueva vista
        if view_name in self.vistas:
            nueva_vista = self.vistas[view_name](self.view.content_area, self)
            nueva_vista.pack(fill="both", expand=True)

    def obtener_inventario(self):
        """Método que las vistas llaman para obtener el DataFrame cargado"""
        return self.modelo.get_all_data()

    def guardar_punto_dulce(self, fase, genero, precio):
        """Guarda los resultados calculados en el almacén global"""
        self.almacen_exito[fase] = {"genero": genero, "precio": precio}
        print(f"✅ Almacén actualizado: {fase} -> {genero} (${precio})")

    def actualizar_almacen_al_ultimo_anio(self):
        """
        Calcula los puntos dulces del año más reciente del dataset.
        Esto garantiza que el informe no muestre datos de años 'viejos' consultados por error.
        """
        df = self.obtener_inventario()
        if df is None or df.is_empty():
            print("❌ No hay datos disponibles para actualizar.")
            return

        try:
            # 1. Identificar el año más reciente disponible en el CSV
            ultimo_anio = df.select(pl.col("Año")).max().to_series()[0]
            df_reciente = df.filter(pl.col("Año") == ultimo_anio)

            # 2. Procesar ambas fases de tiempo
            fases = [("Ventas Día 1", "dia_1"), ("Ventas Sem. 1", "semana_1")]

            for col_csv, fase_key in fases:
                # Limpieza y casting para asegurar cálculos correctos
                temp_df = df_reciente.with_columns([
                    pl.col(col_csv).cast(pl.Float64, strict=False).fill_null(0),
                    pl.col("Precio (USD)").cast(pl.Float64, strict=False).fill_null(0)
                ])

                # Obtener el género con más ventas
                ranking = temp_df.group_by("Género (Tag)").agg(
                    pl.col(col_csv).sum().alias("V")
                ).sort("V", descending=True)
                
                if not ranking.is_empty() and ranking[0, "V"] > 0:
                    gen_top = ranking[0, "Género (Tag)"]
                    
                    # Filtrar por ese género líder para hallar su mejor precio (Punto Dulce)
                    df_lider = temp_df.filter(pl.col("Género (Tag)") == gen_top)
                    
                    punto_d_data = df_lider.group_by("Precio (USD)").agg(
                        pl.col(col_csv).sum().alias("S")
                    ).sort("S", descending=True)
                    
                    punto_d = float(punto_d_data[0, "Precio (USD)"])

                    # Sobreescribir el almacén con los datos frescos del año más reciente
                    self.guardar_punto_dulce(fase_key, gen_top, punto_d)
            
        except Exception as e:
            print(f"⚠️ Error en la actualización automática: {e}")