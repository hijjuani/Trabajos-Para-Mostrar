import yfinance as yf
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


"""
- DESCRIPCIÓN -
Muestra la rotación de flujos de dinero entre distintos sectores del mercado utilizando ETFs representativos.
Se calcula el flujo de dinero como la variación del precio multiplicada por el volumen negociado.
Luego se normalizan los flujos por sector y se visualizan en un heatmap.
Finalmente, se analiza la rotación entre sectores de crecimiento (growth) y sectores defensivos (value).
"""

# === CONFIGURACIÓN ===
ETF = {
    # Índices amplios
    "S&P 500": "SPY",
    "Nasdaq 100": "QQQ",
    "Dow Jones": "DIA",
    "Russell 2000": "IWM",

    # Metales y Tierras
    "Gold": "GLD",
    "Silver": "SLV",
    "Copper": "CPER",
    "Platinum": "PPLT",
    "Lithium & Battery Tech": "LIT",
    "Rare Earth Metals": "REMX",
    "Petroleum": "WTI",

    # Sectores
    "Technology": "XLK",
    "Energy": "XLE",
    "Financials": "XLF",
    "Consumer Staples": "XLP",
    "Consumer Discretionary": "XLY",
    "Health Care": "XLV",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Aerospace & Defense": "ITA",
    "Semiconductors": "SOXX",
    "Biotechnology": "IBB",
    "Cybersecurity": "HACK",
    "Cloud Computing": "CLOU",
    "Commodities": "DBC",
    "Real Assets": "RLY",
    "Infrastructure": "TOLZ",
    "Agriculture": "MOO",

    # ETFs cripto
    "Bitcoin": "IBIT",
    "Ethereum": "ETHA"
}

PERIODO = "6mo"
INTERVALO = "1wk"

# === DESCARGA DE DATOS ===
print("📥 Descargando datos de ETF sectoriales y cripto...")
data = yf.download(
    list(ETF.values()), 
    period=PERIODO, 
    interval=INTERVALO, 
    group_by="ticker", 
    progress=False, 
    auto_adjust=True  # precios ajustados
)

# === CÁLCULO DE FLUJOS DE DINERO ===
flujos = {}
for sector, ticker in ETF.items():
    try:
        df = data[ticker][["Close", "Volume"]].dropna()
        # Calcular flujo de dinero: ΔPrecio * Volumen
        df["delta"] = df["Close"].diff()
        df["Flow"] = df["delta"] * df["Volume"]
        # Agrupar por mes para visualizar en heatmap
        df["Day"] = df.index.to_period("D").start_time
        flujos[sector] = df.groupby("Day")["Flow"].sum()
    except KeyError:
        print(f"⚠️ No se pudo obtener datos para {ticker} ({sector})")

# === UNIR TODO EN UN SOLO DF ===
flujos_df = pd.DataFrame(flujos).fillna(0)

# Normalización por sector (z-score)
flujos_norm = (flujos_df - flujos_df.mean()) / flujos_df.std()

# === ANÁLISIS DE ROTACIÓN SECTORIAL ===

growth_sectors = [
    # Tecnología y disrupción
    "Technology",              # XLK
    "Semiconductors",          # SOXX
    "Biotechnology",           # IBB
    "Cybersecurity",           # HACK
    "Cloud Computing",         # CLOU

    # Consumo cíclico y expansión
    "Consumer Discretionary",  # XLY

    # Cíclicos de crecimiento
    "Industrials",             # XLI
    "Financials",              # XLF
    "Real Estate",             # XLRE
    "Aerospace & Defense",     # ITA
    "Infrastructure",          # TOLZ

    # Metales ligados a transición energética
    "Lithium & Battery Tech",  # LIT
    "Rare Earth Metals",       # REMX

    # Cripto (alto beta / growth puro)
    "Bitcoin",                 # IBIT
    "Ethereum"                 # ETHA
]
value_sectors = [
    # Defensivos clásicos
    "Consumer Staples",        # XLP
    "Utilities",               # XLU
    "Health Care",             # XLV

    # Sectores de cash flow y ciclo maduro
    "Energy",                  # XLE
    "Materials",               # XLB
    "Agriculture",             # MOO

    # Commodities y real assets
    "Gold",                    # GLD
    "Silver",                  # SLV
    "Copper",                  # CPER
    "Platinum",                # PPLT
    "Commodities",             # DBC
    "Real Assets"              # RLY
]

# Filtrar los sectores que efectivamente existen en el DF
growth_valid = [s for s in growth_sectors if s in flujos_norm.columns]
value_valid = [s for s in value_sectors if s in flujos_norm.columns]

# Calcular flujos promedio por grupo
flow_growth = flujos_norm[growth_valid].mean(axis=1)
flow_value = flujos_norm[value_valid].mean(axis=1)

# Diferencia entre ambos: rotación neta
rotacion = flow_growth - flow_value

# === VISUALIZACIÓN ===
# Heatmap de flujos normalizados

plt.figure(figsize=(14, 7))
ax = sns.heatmap(
    flujos_norm.T,
    cmap="RdYlGn",
    center=0,
    cbar_kws={"label": "Salida  <──  Flujo Normalizado  ──>  Entrada", "pad": 0.02},
    linewidths=0.5,
    linecolor="white",
    vmax=2,
    vmin=-2
)

# Estilo más limpio
plt.style.use("seaborn-v0_8-whitegrid")
ax.set_facecolor("white")

# --- Etiquetas más prolijas ---
fechas = flujos_norm.index.to_pydatetime()
ax.set_xticks(np.arange(len(fechas)) + 0.5)
ax.set_xticklabels([f.strftime("%d %b") for f in fechas], rotation=45, ha="right", fontsize=9)
ax.tick_params(axis='x', pad=10)
ax.tick_params(axis='y', pad=8)

# --- Títulos más claros ---
fecha_inicio = flujos_norm.index.min().strftime("%d %b %Y")
fecha_fin = flujos_norm.index.max().strftime("%d %b %Y")
plt.title(f"Rotación de Flujos entre ETFs ({fecha_inicio} - {fecha_fin})",
          fontsize=15, fontweight="bold", pad=20)
plt.xlabel("Fecha", labelpad=10)
plt.ylabel("Sector / Categoría", labelpad=12)

plt.tight_layout()
plt.show()

# === GRÁFICO DE LÍNEAS PARA ROTACIÓN GROWTH VS VALUE ===

plt.figure(figsize=(12, 4))
plt.plot(rotacion.index, rotacion, label="Rotación hacia Growth (+) o Value (-)", color="steelblue", linewidth=2)
plt.axhline(0, color="gray", linestyle="--", linewidth=1)
plt.fill_between(rotacion.index, rotacion, 0, where=rotacion>0, color="green", alpha=0.3, label="Hacia Growth")
plt.fill_between(rotacion.index, rotacion, 0, where=rotacion<0, color="red", alpha=0.3, label="Hacia Value/Defensivo")

plt.title("Rotación Sectorial: Growth vs Value", fontsize=13, fontweight="bold")
plt.xlabel("Fecha")
plt.ylabel("Flujo Relativo Normalizado")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()