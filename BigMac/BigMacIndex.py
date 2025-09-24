import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

df = pd.read_excel("BigMac/BigMac.xlsx")


df["Dolar_BigMac_Teoric"] = df["Price_ARS"] / df["Price_USA"]
df["Brecha"] = (df["Dolar_Blue"] *100 / df["Dolar_BigMac_Teoric"]) - 100


plt.style.use("dark_background")
colors = {
    "brecha": "#ffffffff",   # magenta
    "usa": "#00e5ff",      # celeste
    "arg": "#ffaa00",      # naranja
    }

fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor("#141823")
ax.set_facecolor("#151E38")

# Graficar precios Big Mac en dólares
ax.plot(df["Date"], df["Price_USD"], color=colors["usa"], label="Big Mac ARG (USD)", linewidth=2)
ax.plot(df["Date"], df["Price_USA"], color=colors["arg"], label="Big Mac USA (USD)", linewidth=2)

# Segundo eje Y para la brecha

ax2 = ax.twinx()
yabs_max = abs(max(ax.get_ylim(), key=abs))
ax2.set_ylim(ymin=-yabs_max*30, ymax=yabs_max*30)
ax2.plot(df["Date"], 
         df["Brecha"], 
         color=colors["brecha"], 
         linestyle="--", 
         linewidth=0.2, 
         label="Brecha Dolar (%)", 
         marker='o', 
         markersize=2,
         markerfacecolor=colors["brecha"],
         markeredgewidth=0.5,)


for x, y in zip(df.index.values, df['Brecha']):
    ax2.annotate(
        f"{y:.2f}",
        (x, y),
        textcoords="offset points",
        xytext=(8, 8),
        ha='center',
        fontsize=100,
        color='white'
    )

# Títulos y etiquetas
ax.set_title("Big Mac Index Argentina", fontsize=16, fontweight="bold", color="white")
ax.set_xlabel("Fecha", fontsize=12, color="white")
ax.set_ylabel("Precio (USD)", fontsize=12, color="white")
ax2.set_ylabel("Sobreprecio (%)", fontsize=12, color="white")

# Grilla suave
ax.grid(alpha=0.3, linestyle="--")

# Ticks blancos
ax.tick_params(axis="x", colors="white", rotation=30)
ax.tick_params(axis="y", colors="white")
ax2.tick_params(axis="y", colors="white")

# Leyendas
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=10)


fig.text(0.99, 0.01, "Juani © 2025",
         ha='right', va='bottom',
         fontsize=12, color='gray', alpha=0.8)


plt.tight_layout()
plt.show()