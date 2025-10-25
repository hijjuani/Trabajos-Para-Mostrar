import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ticker = "EWZ"
sma_long_period = 90
sma_short_period = 30
period = "3y"

# Descargar datos
data = yf.download(ticker, period=period)
data = data[["Close"]]
data.rename(columns={"Close": "Price"}, inplace=True)

# Crear medias móviles
data["SMA_short"] = data["Price"].rolling(window=sma_short_period).mean()
data["SMA_long"] = data["Price"].rolling(window=sma_long_period).mean()

# Señales de compra/venta
data["Signal"] = 0
data.loc[data["SMA_short"] > data["SMA_long"], "Signal"] = 1  # posición larga --> porcentaje pasa a positivo
data.loc[data["SMA_short"] < data["SMA_long"], "Signal"] = -1 # posición corta --> porcentaje pasa a negativo

# Retornos logarítmicos del activo
data["LogReturn"] = np.log(data["Price"] / data["Price"].shift(1))

# Retornos de la estrategia (posición * retorno del activo)
data["StrategyReturn"] = data["Signal"].shift(1) * data["LogReturn"]

# Retorno acumulado
data["CumulativeAsset"] = data["LogReturn"].cumsum().apply(np.exp)
data["CumulativeStrategy"] = data["StrategyReturn"].cumsum().apply(np.exp)


"""
Sumo los retornos logarítmicos diarios del activo.
    Como no puedo sumar los retornos porcentuales, utilizo propiedades de los logaritmos: ln(a*b) = ln(a) + ln(b)
    Entonces, al sumar los ln de los retornos diarios, estoy acumulando los retornos
    Luego aplico np.exp() para pasar de escala logarítmica (suma de ln) a escala real (factor multiplicativo e^x),
    Es decir, cuánto se multiplicó el dinero desde el inicio.

Hago lo mismo, pero con los retornos de la estrategia.
    Cada StrategyReturn ya tiene en cuenta si estábamos long (+1) o short (-1). 
    Entonces, al acumular y aplicar np.exp(), obtengo cómo habría crecido $1 siguiendo la estrategia, considerando entradas, salidas y cambios de posición.

"""


fig, axes = plt.subplots(2, 1, figsize=(12,10), sharex=True)

# ---------- 1️⃣ Precio y señales ----------
axes[0].plot(data["Price"], label=ticker, alpha=0.6)
axes[0].plot(data["SMA_short"], label=f"SMA {sma_short_period}", alpha=0.8, linestyle='--')
axes[0].plot(data["SMA_long"], label=f"SMA {sma_long_period}", alpha=0.8, linestyle='--')

# Marcamos señales
buy_signals = data[data["Signal"] == 1]
sell_signals = data[data["Signal"] == -1]

axes[0].scatter(buy_signals.index, buy_signals["Price"], label="Compra", marker="^", color="green", alpha=0.9)
axes[0].scatter(sell_signals.index, sell_signals["Price"], label="Venta", marker="v", color="red", alpha=0.9)

axes[0].set_title("Cruce de Medias Móviles - Señales de Compra/Venta")
axes[0].legend()
axes[0].grid(True)

# ---------- 2️⃣ Retornos acumulados ----------
axes[1].plot(data["CumulativeAsset"], label=f"{ticker} (Buy & Hold)")
axes[1].plot(data["CumulativeStrategy"], label=f"Estrategia SMA {sma_short_period}/{sma_long_period}")
axes[1].set_title("Backtesting: Crecimiento de $1 invertido")
axes[1].set_xlabel("Fecha")
axes[1].set_ylabel("Crecimiento de $1")
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.show()




###################################
##### Métricas de rendimiento #####
###################################


# Retorno total (de todo el período)
total_return_asset = data["CumulativeAsset"].iloc[-1] - 1
total_return_strategy = data["CumulativeStrategy"].iloc[-1] - 1

# Volatilidad anualizada
volatility_asset = data["LogReturn"].std() * np.sqrt(252)
volatility_strategy = data["StrategyReturn"].std() * np.sqrt(252)

# Sharpe Ratio (suponiendo tasa libre de riesgo = 0)
sharpe_asset = (data["LogReturn"].mean() / data["LogReturn"].std()) * np.sqrt(252)
sharpe_strategy = (data["StrategyReturn"].mean() / data["StrategyReturn"].std()) * np.sqrt(252)

print("Rendimiento total (Buy & Hold):", round(total_return_asset*100,2), "%")
print("Rendimiento total (Estrategia):", round(total_return_strategy*100,2), "%")
print("Volatilidad (Buy & Hold):", round(volatility_asset*100,2), "%")
print("Volatilidad (Estrategia):", round(volatility_strategy*100,2), "%")
print("Sharpe Ratio (Buy & Hold):", round(sharpe_asset,2))
print("Sharpe Ratio (Estrategia):", round(sharpe_strategy,2))