import numpy as np
from scipy.optimize import minimize

def objective(x):
    return temp_func(x)

def temp_func(x):
    return x[0]**2 + x[1]**2 + np.sin(x[0])

def callback_log(x):
    """Callback функция, вызываемая на каждой итерации"""
    f_val = objective(x)
    print(f"Итерация: x={x}, f(x)={f_val:.6f}")

# Минимизация с callback
result = minimize(objective, x0=[1, 1], method='BFGS', callback=callback_log)
print(f"\nРезультат: {result.x}")