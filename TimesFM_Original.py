from matplotlib import pyplot as plt
import torch
import numpy as np
import timesfm
import yfinance as yf
import pandas as pd

"""***********

- DESCRIPCIÓN -

Utiliza la librería TimesFM para predecir el precio de un activo.

**********"""

# ---------------------------
# 1) Descargar datos
# ---------------------------

ticker = "GGAL"

data_1 = yf.Ticker(ticker)
train_data = data_1.history(start="2020-01-01", end="2024-12-31")
test_data = data_1.history(start="2025-01-01")

df_train = train_data.reset_index()[["Date", "Close"]]
df_test = test_data.reset_index()[["Date", "Close"]]

# serie de entrenamiento
train_series = df_train["Close"].values.astype(np.float32)

# ---------------------------
# 2) Modelo TimesFM
# ---------------------------
torch.set_float32_matmul_precision("high")
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch")

model.compile(
    timesfm.ForecastConfig(
        max_context=160,
        max_horizon=90,   # límite de horizontes en cada llamada
        normalize_inputs=True,
        use_continuous_quantile_head=True,
        force_flip_invariance=False,
        infer_is_positive=True,
        fix_quantile_crossing=True,
    )
)

# ---------------------------
# 3) Forecast encadenado para 2025
# ---------------------------
future_idx = pd.bdate_range("2025-01-01", "2025-10-31")  # ~252 días hábiles
target_days = len(future_idx)

context = train_series.tolist()
remaining = target_days
all_preds = []

with torch.no_grad():
    while remaining > 0:
        horizon = min(remaining, 90)  # máximo 90 por bloque
        input_segment = np.array(context[-160:], dtype=np.float32)  # recorte al contexto permitido
        pf, qf = model.forecast(horizon=horizon, inputs=[input_segment])
        pred_chunk = np.asarray(pf)[0]  # batch=1
        all_preds.extend(pred_chunk.tolist())
        context.extend(pred_chunk.tolist())  # extender contexto con predicción
        remaining -= horizon

forecast_series = pd.Series(all_preds, index=future_idx)

# ---------------------------
# 4) EMA 200
# ---------------------------

data_2 = data_1.history(start="2020-01-01", end="2025-12-31")
data_2 = data_2.reset_index()[["Date", "Close"]]
data_2["Close"] = data_2["Close"].values.astype(np.float32)
data_2["EMA200"] = data_2["Close"].ewm(span=200, adjust=False).mean()

# ---------------------------
# 5) Graficar
# ---------------------------
plt.figure(figsize=(14,6))
plt.plot(df_train["Date"], df_train["Close"], label="Train Data", color="black", linewidth=1.2)

if not df_test.empty:
    plt.plot(df_test["Date"], df_test["Close"], label="Test Data", color="gray", linestyle="--")

plt.plot(forecast_series.index, forecast_series.values, label="Predicción TimesFM 2025", color="tab:orange")
plt.title(f"Predicción 2025 - {ticker} con TimesFM")

# Línea vertical punteada al 2025-01-01
plt.axvline(pd.Timestamp("2025-01-01"), color="red", linestyle="--", linewidth=0.6, label=" Inicio Predicción")

plt.axvspan(pd.Timestamp("2025-01-01"), forecast_series.index[-1], color="red", alpha=0.05)

plt.plot(data_2["Date"], data_2["EMA200"], label="EMA 200", color="blue", linewidth=1)

plt.legend()
plt.grid(alpha=0.3)
plt.show()


