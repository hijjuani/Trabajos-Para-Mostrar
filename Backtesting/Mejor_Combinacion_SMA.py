import numpy as np
import pandas as pd
import yfinance as yf
import seaborn as sns
import matplotlib.pyplot as plt

# ======================
# CONFIGURACIÓN INICIAL
# ======================

"""
Este script busca la mejor combinación de medias móviles simples (SMA)
para utilizar en una estrategia de cruce de medias móviles (Estrategia_SMA.py).
Se prueban múltiples combinaciones de períodos para las SMA corta y larga,
y se evalúa el rendimiento de la estrategia para cada combinación.
Finalmente, se muestra un resumen de las mejores combinaciones y un mapa de calor.
"""

ticker = "EWZ"     # Cambiá por el activo que quieras
period = "3y"        # Ej: "1y", "5y", "10y", "max"

# Descargamos datos
data = yf.download(ticker, period=period)
data["LogReturn"] = np.log(data["Close"] / data["Close"].shift(1))
data = data.dropna()

# Rangos de medias móviles a probar
short_windows = range(5, 105, 5)     # ej. 5,10,15,20,25,...
long_windows = range(20, 210, 10)   # ej. 20,30,40,...,190

results = []

# ======================
# BUCLE DE OPTIMIZACIÓN
# ======================

for short in short_windows:
    for long in long_windows:
        if short >= long:
            continue  # ignoramos combinaciones inválidas

        # 🔹 CREO UNA COPIA LIMPIA DE LOS DATOS
        df = data.copy()

        # Medias móviles
        df["SMA_short"] = df["Close"].rolling(window=short).mean()
        df["SMA_long"] = df["Close"].rolling(window=long).mean()

        # Señales de compra/venta
        df["Signal"] = np.where(df["SMA_short"] > df["SMA_long"], 1, -1)

        """
        Uso el shift(1) porque:
        - La decisión de estar long/short se toma al final del día anterior.
        - El retorno del día actual se realiza durante el día actual.
        Así, la señal del día anterior se aplica al retorno del día actual.
        """


        # Retorno de la estrategia (señal del día anterior * retorno del día actual)
        df["StrategyReturn"] = df["Signal"].shift(1) * df["LogReturn"]
        df = df.dropna()        # eliminamos filas con NaN

        # Métricas
        total_return = np.exp(df["StrategyReturn"].sum()) - 1

        """
        1️⃣ data["StrategyReturn"]
            Son los retornos logarítmicos diarios de la estrategia, ya ajustados por las señales (es decir, comprando o vendiendo según el cruce).
        2️⃣ .sum()
            Si sumás todos los retornos logarítmicos diarios, obtenés el retorno logarítmico total de todo el período.
            Recordá que los log-returns se suman en lugar de multiplicarse, lo que es una de sus grandes ventajas.
        3️⃣ np.exp(...)
            La exponencial revierte el logaritmo.
            Con esto convertimos el retorno logarítmico acumulado en un retorno porcentual real.
        4️⃣ - 1
            Restamos 1 para expresar el resultado en formato clásico:
            0.25 significa +25%
            -0.10 significa -10%
        """

        volatility = df["StrategyReturn"].std() * np.sqrt(252)
        sharpe = (df["StrategyReturn"].mean() / df["StrategyReturn"].std()) * np.sqrt(252)

        results.append([short, long, total_return, volatility, sharpe])


# ======================
# RESULTADOS
# ======================

results_df = pd.DataFrame(results, columns=["SMA_corta", "SMA_larga", "Rendimiento", "Volatilidad", "Sharpe"])
results_df = results_df.sort_values(by="Sharpe", ascending=False)

print("\n" + "----"*20)
print(f"Resultados de la optimización de SMA para {ticker}:\n")
print(results_df.head(10))
print("----"*20 + "\n")

# ======================
# HEATMAP DEL SHARPE
# ======================

# Pivotamos el DataFrame
heatmap_data = results_df.pivot(index="SMA_corta", columns="SMA_larga", values="Sharpe")

plt.figure(figsize=(10, 7))
sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".3f",
    cmap="RdYlGn",        # Verde = mejor Sharpe
    cbar_kws={"label": "Sharpe Ratio"},
    linewidths=0.5,
    vmax=heatmap_data.max().max(),
    vmin=heatmap_data.min().min(),
    linecolor="gray"
)

best = results_df.iloc[0]
plt.scatter(best["SMA_larga"] + 0.5, best["SMA_corta"] + 0.5,
            s=200, edgecolor="black", facecolor="none", linewidth=2)


plt.title(f"Mapa de calor del Sharpe Ratio\n({ticker} - Estrategia de Cruce de Medias Móviles)")
plt.xlabel("SMA Larga")
plt.ylabel("SMA Corta")
plt.tight_layout()
plt.show()
