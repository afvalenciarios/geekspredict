from sklearn.metrics import mean_absolute_error
import numpy as np


class EvaluacionModeloService:

    def calcular_metricas(self, y_real, y_pred):

        mae = mean_absolute_error(y_real, y_pred)

        y_real = np.array(y_real)
        y_pred = np.array(y_pred)

        y_real_seguro = np.where(y_real == 0, 1, y_real)

        mape = np.mean(np.abs((y_real - y_pred) / y_real_seguro)) * 100

        return {
            "mae": round(float(mae), 2),
            "mape": round(float(mape), 2)
        }