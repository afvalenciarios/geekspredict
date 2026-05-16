from sklearn.linear_model import LinearRegression
import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

class RegresionLinealService:

    def entrenar_modelo(self):

        conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
)

        query = """
        SELECT fecha, cantidad
        FROM venta
        WHERE YEAR(fecha) = 2025
        ORDER BY fecha
        """

        datos = pd.read_sql(query, conexion)

        conexion.close()

        if datos.empty:
            return {
                "prediccion": 0,
                "meses": [],
                "ventas_mensuales": [],
                "mes_prediccion": "Sin datos"
            }

        datos["fecha"] = pd.to_datetime(datos["fecha"])

        datos["mes"] = datos["fecha"].dt.month

        ventas_mensuales = (
            datos.groupby("mes")["cantidad"]
            .sum()
            .reset_index()
        )

        X = ventas_mensuales[["mes"]]
        y = ventas_mensuales["cantidad"]

        modelo = LinearRegression()
        modelo.fit(X, y)

        ultimo_mes = int(ventas_mensuales["mes"].max())

        if ultimo_mes == 12:
            siguiente_mes_numero = 1
        else:
            siguiente_mes_numero = ultimo_mes + 1

        siguiente_mes = np.array([[siguiente_mes_numero]])

        prediccion = modelo.predict(siguiente_mes)

        nombres_meses = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre"
        ]

        labels = [
            nombres_meses[m - 1]
            for m in ventas_mensuales["mes"]
        ]

        valores = ventas_mensuales["cantidad"].tolist()

        return {
            "prediccion": round(float(prediccion[0]), 2),
            "meses": labels,
            "ventas_mensuales": valores,
            "mes_prediccion": nombres_meses[siguiente_mes_numero - 1]
        }