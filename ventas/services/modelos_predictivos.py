class ModelosPredictivosService:

    def obtener_modelos(self):

        modelos = [
            {
                "nombre": "Regresión Lineal",
                "descripcion": "Modelo utilizado para estimar la tendencia futura de ventas a partir del comportamiento histórico mensual.",
                "estado": "Activo"
            },
            {
                "nombre": "Random Forest",
                "descripcion": "Modelo de aprendizaje automático basado en múltiples árboles de decisión para mejorar la precisión predictiva.",
                "estado": "Disponible"
            },
            {
                "nombre": "XGBoost",
                "descripcion": "Modelo avanzado de boosting utilizado para mejorar el rendimiento en predicciones con datos estructurados.",
                "estado": "Disponible"
            },
            {
                "nombre": "LSTM",
                "descripcion": "Modelo de redes neuronales recurrentes orientado al análisis de series temporales y comportamiento secuencial de ventas.",
                "estado": "Planeado"
            }
        ]

        return modelos