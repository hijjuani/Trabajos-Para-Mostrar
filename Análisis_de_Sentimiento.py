import requests
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import nltk

# === CONFIGURACIÓN ===
API_KEY = "26d19361916f459eac75c6d0abe21104"
KEYWORDS = ["GOOGL stock", "GOOGL", "Alphabet results", "Alphabet earnings", "GOOGL price"]
TITULO = "Alphabet Inc (GOOGL)"
DIAS_RETROCESO = 3
IDIOMA = "en"

# === 1. Fechas ===
fecha_fin = datetime.today().date()
fecha_inicio = fecha_fin - timedelta(days=DIAS_RETROCESO)
print(f"📅 Analizando desde {fecha_inicio} hasta {fecha_fin}")

# === 2. Extracción desde NewsAPI ===
url = "https://newsapi.org/v2/everything"
articulos_total = []

for kw in KEYWORDS:
    print(f"📰 Extrayendo titulares para: {kw}...")
    params = {
        "q": kw,
        "from": fecha_inicio.isoformat(),
        "to": fecha_fin.isoformat(),
        "language": IDIOMA,
        "sortBy": "publishedAt",
        "pageSize": 100,
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "ok":
        print(f"❌ Error con '{kw}':", data.get("message"))
        continue

    articulos = data.get("articles", [])
    for art in articulos:
        art["keyword"] = kw

    print(f"✅ {len(articulos)} titulares extraídos para '{kw}'.")
    articulos_total.extend(articulos)

print(f"📊 Total de artículos combinados: {len(articulos_total)}")
print("----"*23)

# === 3. Crear DataFrame y normalizar fechas ===
df = pd.DataFrame(articulos_total)
if df.empty:
    print("⚠️ No se encontraron artículos. Revisa las keywords o la API Key.")
    exit()

df = df[["title", "source", "publishedAt", "keyword"]].dropna()
df["date"] = pd.to_datetime(df["publishedAt"]).dt.date
df["media"] = df["source"].apply(lambda x: x.get("name", ""))
df = df.drop_duplicates(subset="title").reset_index(drop=True)

# === 4. Análisis de sentimiento con VADER ===
print("🧠 Analizando sentimiento con VADER...")

nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()

def vader_sentiment(text):
    try:
        return sia.polarity_scores(text)["compound"]
    except:
        return None

df["sentimiento"] = df["title"].apply(vader_sentiment)
df = df[df["sentimiento"].notna()]
df["sentimiento"] = df["sentimiento"].round(2)
df = df[df["sentimiento"] != 0]
df = df.reset_index(drop=True)

print("✅ Análisis de sentimiento completado.")
print("----"*23)
print("\n📋 Resumen estadístico global del sentimiento:")
print(df["sentimiento"].describe())
print("----"*23)

# === 5. Clasificación por categoría ===
def sentiment_label(score):
    if score > 0.05:
        return "Positivo"
    elif score < -0.05:
        return "Negativo"
    else:
        return "Neutro"

df["categoria"] = df["sentimiento"].apply(sentiment_label)
proporciones = df["categoria"].value_counts(normalize=True) * 100

# === 6. Sentimiento medio por keyword ===
sent_por_kw = (
    df.groupby("keyword")["sentimiento"]
    .mean()
    .reset_index()
    .sort_values("sentimiento", ascending=True)
)
print("\n📈 Sentimiento medio por keyword:")
print(sent_por_kw)
print("----"*23)

##############################
# === CONFIGURACIÓN VISUAL ===
##############################

sns.set(style="whitegrid")

# === DISEÑO: UNA SOLA FIGURA ===
fig = plt.figure(figsize=(13, 9))
gs = fig.add_gridspec(2, 2, height_ratios=[2.1, 1.9])

plt.suptitle(
    f"Análisis de Sentimiento - {TITULO}\n"
    f"({fecha_inicio} → {fecha_fin})",
    fontsize=15, fontweight="bold"
)

# --- (1) HISTOGRAMA (fila 1, abarca ambas columnas) ---
ax1 = fig.add_subplot(gs[0, :])
sns.histplot(df["sentimiento"], bins=20, kde=True, color="skyblue", ax=ax1)
ax1.axvline(0, color="gray", linestyle="--", linewidth=1)
ax1.set_title("Distribución General de Sentimiento (VADER)", fontsize=12)
ax1.set_xlabel("Puntuación de Sentimiento")
ax1.set_ylabel("Frecuencia")

# Leyenda dentro del histograma
ax1.text(
    0.02, 0.95,
    f"Media global: {df['sentimiento'].mean():.2f}\n"
    f"Titulares: {len(df)}\n"
    f"Periodo: {DIAS_RETROCESO} días",
    transform=ax1.transAxes,
    fontsize=10,
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray", alpha=0.8),
    ha="left", va="top"
)

# --- (2) PROPORCIÓN POR CATEGORÍA (fila 2, col 1) ---
ax2 = fig.add_subplot(gs[1, 0])
color_map = {"Positivo": "green", "Neutro": "gray", "Negativo": "red"}
colors = [color_map[c] for c in proporciones.index]

sns.barplot(
    y=proporciones.index,
    x=proporciones.values,
    hue=proporciones.index,
    palette=colors,
    legend=False,
    ax=ax2
)
ax2.set_title("Proporción por Categoría", fontsize=12)
ax2.set_xlabel("Porcentaje (%)")
ax2.set_ylabel("")
for i, v in enumerate(proporciones.values):
    ax2.text(v + 0.5, i, f"{v:.1f}%", va="center", fontweight="bold")

# --- (3) SENTIMIENTO POR KEYWORD (fila 2, col 2) ---
ax3 = fig.add_subplot(gs[1, 1])
sns.barplot(
    data=sent_por_kw,
    y="keyword",
    x="sentimiento",
    hue="keyword",
    palette="coolwarm",
    legend=False,
    ax=ax3
)
ax3.set_title("Sentimiento Medio por Keyword", fontsize=12)
ax3.set_xlabel("Puntuación Media (VADER)")
ax3.set_ylabel("")
for i, (val, kw) in enumerate(zip(sent_por_kw["sentimiento"], sent_por_kw["keyword"])):
    ax3.text(val + 0.02, i, f"{val:.2f}", va="center", fontweight="bold")

# --- Ajuste de márgenes generales ---
plt.tight_layout(rect=[0, 0, 1, 0.92], h_pad=2.0, w_pad=2.5)
plt.show()
