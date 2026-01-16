from scipy.optimize import linprog

print("------- Método Simplex -------")

def resolver_lp(c, A_eq=None, b_eq=None, A_ub=None, b_ub=None, bounds=None, tipo="min"):
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


# Ejemplo de función objetivo: Min(-x1 - x2)
c = [1, 1, 1]                     

# Ejemplo de restricción de igualdad: 9200x1 + 8800x2 = 61000
A_eq = [[9200, 8800, 0], [1000, 1200, 300]]            
b_eq = [6100, 7000]
# Ejemplo de restricciones de desigualdad (max de las variables): x1 ≤ 100, x2 ≤ 100
A_ub = [[1, 1, 0], [0, 1, 1]]
b_ub = [10000, 10000]

"""
Si A_ub y b_ub son None, no hay restricciones de desigualdad.
"""

# Mínimos de las variables
mins = [0, 0, 0]
bounds = [(m, None) for m in mins]  # Límites de las variables: x1 ≥ 1, x2 ≥ 1

# Llamar a la función para resolver el problema
resolver_lp(c, A_eq, b_eq, A_ub, b_ub, bounds, tipo="max")