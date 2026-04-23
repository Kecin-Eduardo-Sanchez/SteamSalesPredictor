
#import pandas as pd
#import os

#class DataModel:
#    def __init__(self):
        # Localización dinámica de la carpeta assets dentro del proyecto
#        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#        ruta_db = os.path.join(base_path, 'assets', 'steam_db.xlsx')
        
#        try:
            # Cargamos el Excel. Ya no usamos parse_dates porque Año y Mes son INT.
#            self.df = pd.read_excel(ruta_db, engine='openpyxl')
#           print("Base de datos (Año/Mes) cargada con éxito.")
#        except Exception as e:
#            print(f"Error al cargar la base de datos: {e}")
            # Estructura de respaldo con las nuevas columnas de tiempo
#            self.df = pd.DataFrame(columns=[
#                'ID', 'Nombre del Juego', 'Género (Tag)', 'Año', 'Mes',
#                'Wishlists', 'Seguidores', 'Precio (USD)', 
#                'Ventas Día 1', 'Ventas Sem. 1'
#            ])

   # def get_all_data(self):
    #    """Devuelve el DataFrame completo con los 50 registros [cite: 29]"""
      #  return self.df

   # def get_datos_por_temporada(self, mes):
    #    """Filtra juegos lanzados en un mes específico para analizar estacionalidad"""
     #   return self.df[self.df['Mes'] == mes]

import polars as pl
import os

class DataModel:
    def __init__(self):
        # Mantenemos la lógica de rutas que es excelente
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta_db = os.path.join(base_path, 'assets', 'steam_db.xlsx')
        
        try:
            # Polars lee el Excel. Nota: read_excel en Polars es muy eficiente
            self.df = pl.read_excel(ruta_db)
            print("Base de datos cargada con Polars con éxito.")
        except Exception as e:
            print(f"Error al cargar con Polars: {e}")
            # Creamos un DataFrame de Polars vacío con tipos de datos definidos (Schema)
            self.df = pl.DataFrame({
                'ID': [], 'Nombre del Juego': [], 'Género (Tag)': [], 
                'Año': pl.Int64, 'Mes': pl.Int64, 'Wishlists': pl.Int64, 
                'Seguidores': pl.Int64, 'Precio (USD)': pl.Float64, 
                'Ventas Día 1': pl.Int64, 'Ventas Sem. 1': pl.Int64
            })

    def get_all_data(self):
        """Retorna el DataFrame de Polars"""
        return self.df

    def get_datos_por_temporada(self, mes):
        """
        Usa la sintaxis de expresiones de Polars. 
        pl.col('Mes') es mucho más rápido que el acceso por strings de Pandas.
        """
        return self.df.filter(pl.col('Mes') == mes)
    
    def get_datos_por_anio(self, anio):
        """Filtro por año para la Vista 2 usando Polars"""
        return self.df.filter(pl.col('Año') == anio)
    
