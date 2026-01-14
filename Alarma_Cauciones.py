import tkinter as tk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time, threading, re, winsound

"""
Avisa cuando la tasa de cauciones supera un cierto umbral (target),
tomando los datos de la tasa desde InvertirOnline con Selenium.
"""

# ---------------- CONFIG ----------------
TARGET_ARS = 50.0
TARGET_USD = 1.4
URL = "https://iol.invertironline.com/mercado/cotizaciones/argentina/cauciones"

# ---------------- SONIDOS ----------------
def beep_1d():
   winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)

def beep_7d():
    winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)

# ---------------- SELENIUM ----------------
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.get(URL)
time.sleep(10)

# ---------------- TKINTER ----------------
root = tk.Tk()
root.title("Monitor de Cauciones")
root.geometry("460x420")
root.configure(bg="#111")

tk.Label(
    root, text="Cauciones",
    font=("Arial", 20, "bold"),
    fg="white", bg="#111"
).pack(pady=10)

# -------- Frame 1D --------
frame_1d = tk.Frame(root, bg="#1b1b1b", bd=2, relief="ridge")
frame_1d.pack(padx=15, pady=8, fill="x")

tk.Label(frame_1d, text="1 DÍA", font=("Arial", 14, "bold"),
         fg="white", bg="#1b1b1b").pack(pady=5)

label_ars_1 = tk.Label(frame_1d, text="ARS: -- %", font=("Arial", 18),
                       fg="cyan", bg="#1b1b1b")
label_usd_1 = tk.Label(frame_1d, text="USD: -- %", font=("Arial", 18),
                       fg="orange", bg="#1b1b1b")
label_ars_1.pack()
label_usd_1.pack()

status_1d = tk.Label(frame_1d, text="Estado: OK",
                     font=("Arial", 12), fg="lightgreen", bg="#1b1b1b")
status_1d.pack(pady=5)

# -------- Frame 7D --------
frame_7d = tk.Frame(root, bg="#1b1b1b", bd=2, relief="ridge")
frame_7d.pack(padx=15, pady=8, fill="x")

tk.Label(frame_7d, text="7 DÍAS", font=("Arial", 14, "bold"),
         fg="white", bg="#1b1b1b").pack(pady=5)

label_ars_7 = tk.Label(frame_7d, text="ARS: -- %", font=("Arial", 18),
                       fg="cyan", bg="#1b1b1b")
label_usd_7 = tk.Label(frame_7d, text="USD: -- %", font=("Arial", 18),
                       fg="orange", bg="#1b1b1b")
label_ars_7.pack()
label_usd_7.pack()

status_7d = tk.Label(frame_7d, text="Estado: OK",
                     font=("Arial", 12), fg="lightgreen", bg="#1b1b1b")
status_7d.pack(pady=5)

# -------- Estado general --------
label_status = tk.Label(
    root, text="Esperando datos...",
    font=("Arial", 14),
    fg="lightgray", bg="#111"
)
label_status.pack(pady=10)

# ---------------- ESTADO PREVIO ----------------
prev = {
    "ars_1": None, "usd_1": None,
    "ars_7": None, "usd_7": None,
    "stress_1d": False,
    "stress_7d": False
}

def arrow(curr, prev):
    if prev is None:
        return ""
    if curr > prev:
        return " ↑"
    if curr < prev:
        return " ↓"
    return ""

# ---------------- LOOP ----------------
def update_loop():
    while True:
        driver.refresh()
        time.sleep(6)

        html = driver.page_source
        tasas = re.findall(r'(\d{1,3}[.,]\d{1,2})\s*%', html)
        tasas = [float(x.replace(",", ".")) for x in tasas]

        if len(tasas) >= 10:
            ars_1, usd_1, ars_7, usd_7 = tasas[0], tasas[1], tasas[8], tasas[7]

            label_ars_1.config(text=f"ARS: {ars_1:.2f}" + " " + arrow(ars_1, prev["ars_1"]))
            label_usd_1.config(text=f"USD: {usd_1:.2f}" + " " + arrow(ars_1, prev["ars_1"]))
            label_ars_7.config(text=f"ARS: {ars_7:.2f}" + " " + arrow(ars_1, prev["ars_1"]))
            label_usd_7.config(text=f"USD: {usd_7:.2f}" + " " + arrow(ars_1, prev["ars_1"]))

            stress_1d = ars_1 >= TARGET_ARS or usd_1 >= TARGET_USD
            stress_7d = ars_7 >= TARGET_ARS or usd_7 >= TARGET_USD

            # ---- 1D ----
            if stress_1d:
                status_1d.config(text="⚠️ Estrés de liquidez", fg="red")
                frame_1d.config(bg="#2b0000")
                if not prev["stress_1d"]:
                    beep_1d()
            else:
                status_1d.config(text="Estado: OK", fg="lightgreen")
                frame_1d.config(bg="#1b1b1b")

            # ---- 7D ----
            if stress_7d:
                status_7d.config(text="⚠️ Estrés", fg="red")
                frame_7d.config(bg="#2b0000")
                if not prev["stress_7d"]:
                    beep_7d()
            else:
                status_7d.config(text="Estado: OK", fg="lightgreen")
                frame_7d.config(bg="#1b1b1b")

            # ---- General ----
            if stress_1d or stress_7d:
                root.config(bg="#220000")
                label_status.config(text="Mercado estresado", fg="red")
            else:
                root.config(bg="#111")
                label_status.config(text="Mercado normal", fg="lightgreen")

            # Guardar estado previo
            prev.update({
                "ars_1": ars_1, "usd_1": usd_1,
                "ars_7": ars_7, "usd_7": usd_7,
                "stress_1d": stress_1d,
                "stress_7d": stress_7d
            })

        time.sleep(20)

threading.Thread(target=update_loop, daemon=True).start()
root.mainloop()

