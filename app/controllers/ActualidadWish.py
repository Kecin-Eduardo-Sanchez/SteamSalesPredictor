import polars as pl
import numpy as np
import pandas as pd # Añadimos pandas para las predicciones
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

class ModeloRegrecionLinealWishlist:
    def __init__(self, df):
        self.modelo = LinearRegression()
        self.r2 = 0
        self.entrenado = False
        self.df = df
        self._entrenar()

    def _entrenar(self):
        try:
            if self.df is None or self.df.height < 5: return
            
            data = self.df.select([
                pl.col("Wishlists").cast(pl.Float64),
                pl.col("Seguidores").cast(pl.Float64),
                pl.col("Precio (USD)").cast(pl.Float64),
                pl.col("Ventas Sem. 1").cast(pl.Float64)
            ]).drop_nulls().to_pandas()
            
            self.X_columns = ["Wishlists", "Seguidores", "Precio (USD)"]
            X = data[self.X_columns]
            y = data["Ventas Sem. 1"]
            
            self.modelo.fit(X, y)
            self.r2 = r2_score(y, self.modelo.predict(X))
            self.entrenado = True
        except Exception as e:
            print(f"Error entrenamiento: {e}")

    def obtener_pesos(self):
        if not self.entrenado: return {"wishlists":0, "seguidores":0, "precio":0}
        return {
            "wishlists": self.modelo.coef_[0],
            "seguidores": self.modelo.coef_[1],
            "precio": self.modelo.coef_[2]
        }

    def predecir(self, w, s, p):
        if not self.entrenado: return 0
        # Creamos un DataFrame para evitar el aviso de "feature names"
        entrada = pd.DataFrame([[float(w), float(s), float(p)]], columns=self.X_columns)
        res = self.modelo.predict(entrada)[0]
        return int(max(0, res))

# Asegúrate de que la clase ControladorWish esté debajo
class ControladorWish:
    def __init__(self, df_completo, almacen_global):
        self.df = df_completo
        self.almacen = almacen_global
        self.ia = ModeloRegrecionLinealWishlist(df_completo)

    def obtener_anios(self):
        if self.df is None or self.df.is_empty(): return []
        return sorted(self.df.select(pl.col("Año")).unique().to_series().to_list(), reverse=True)

    def pedir_prediccion_ia(self, w, s, p):
        return self.ia.predecir(w, s, p)

    def procesar(self, anio):
        # ... (mantén tu método procesar igual que antes)
        if not anio or self.df is None: return None
        df_filt = self.df.filter(pl.col("Año") == int(anio))
        if df_filt.is_empty(): return None
        m_wish = df_filt.select(pl.col("Wishlists").median())[0,0]
        m_s1 = df_filt.select(pl.col("Ventas Sem. 1").median())[0,0]
        return {"anio": anio, "wish": m_wish, "s1_num": m_s1, "s1_porc": (m_s1/m_wish*100) if m_wish > 0 else 0}