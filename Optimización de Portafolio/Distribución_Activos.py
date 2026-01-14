from scipy.optimize import linprog
import matplotlib.pyplot as plt
import yfinance as yf

"""
- DESCRIPCIÓN -
Distribuye el monto a invertir según el porcentaje que se quiera asignar a cada activo.
Funciona ingresando un monto máximo de inversión.
Luego se especifica el ticker con sus respectivos porcentajes mínimos y máximos deseados en cartera.
"""

print("------- Método Simplex -------")

def resolver_lp(c, A_eq=None, b_eq=None, A_ub=None, b_ub=None, bounds=None, tipo="min", tickers=[]):
    # Convierte a problema de minimización si es maximización
    if tipo == "max":
        c = [-ci for ci in c]

    # Resolver
    res = linprog(
        c,
        A_eq=A_eq,
        b_eq=b_eq,
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=bounds,
        method="highs"
    )

    # Mostrar resultados
    if res.success:
        print("\n✅ Solución encontrada:")
        for i, val in enumerate(res.x):
            print(f"x{i+1} = {val:.4f}")
        print(f"\n🎯 Valor óptimo de la función objetivo: {res.fun:.4f}")
    else:
        print("\n❌ No se encontró solución:")
        print(res.message)

    # Calcula inversión por activo
    cantidades = res.x
    inversiones = [cantidades[i] * precios[i] for i in range(len(precios))]
    porcentajes = [(inv / presupuesto[0]) * 100 for inv in inversiones]

    # Filtrá activos con porcentaje > 0
    activos_con_inversion = [
        (tickers[i], porcentajes[i]) 
        for i in range(len(porcentajes)) if porcentajes[i] > 0
    ]

    # Separar etiquetas y valores
    labels, values = zip(*activos_con_inversion)

    # Estilo y colores
    colors = plt.cm.tab10.colors
    explode = [0.05] * len(values)

    # Gráfico
    plt.figure(figsize=(8, 8))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, explode=explode, shadow=True)
    plt.title("Distribución óptima del portafolio (%)", fontsize=14)
    plt.tight_layout()
    plt.show()



###################################
##### Definición del problema #####
###################################

# Ejemplo de función objetivo: Min(-x1 - x2)
c = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]                     


# Lista de tickers
tickers = ["AAPL", "GOOGL", "TSLA", "AMZN", "^SPX", 
           "BTC", "KO", "DIS", "NVDA", "INTC"]

precios = []

for t in tickers:
    precio_actual = yf.Ticker(t).info['regularMarketPrice']
    precios.append(precio_actual)


# Presupuesto total
presupuesto = [1000000]

# Porcentajes máximos y mínimos
porcentaje_max = [10, 15, 20, 30, 20, 15, 25, 50, 40, 10]
porcentaje_min = [0, 5, 0, 15, 5, 10, 5, 10, 30, 5]

A_eq = [precios]           
b_eq = presupuesto
A_ub = [[1,0,0,0,0,0,0,0,0,0], [0,1,0,0,0,0,0,0,0,0], [0,0,1,0,0,0,0,0,0,0], [0,0,0,1,0,0,0,0,0,0],
        [0,0,0,0,1,0,0,0,0,0], [0,0,0,0,0,1,0,0,0,0], [0,0,0,0,0,0,1,0,0,0], [0,0,0,0,0,0,0,1,0,0],
        [0,0,0,0,0,0,0,0,1,0], [0,0,0,0,0,0,0,0,0,1]]
b_ub = []
for i in range(len(porcentaje_max)):
    a = (porcentaje_max[i] * presupuesto[0]) / (precios[i] * 100)
    b_ub.append(a)

"""
Si A_ub y b_ub son None, no hay restricciones de desigualdad.
"""

mins = []
for i in range(len(precios)):
    b = (porcentaje_min[i] * presupuesto[0]) / (precios[i] * 100)
    mins.append(b)

bounds = [(m, None) for m in mins]



# Llamar a la función para resolver el problema

resolver_lp(c, A_eq, b_eq, A_ub, b_ub, bounds, tipo="max", tickers = tickers)
