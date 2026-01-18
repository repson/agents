# %% Cell 1
import matplotlib.pyplot as plt
import numpy as np

# Datos de ejemplo
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Crear una figura con múltiples subgráficas
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Gráfica 1: Seno y Coseno
axes[0, 0].plot(x, y1, label='sin(x)', color='blue', linewidth=2)
axes[0, 0].plot(x, y2, label='cos(x)', color='red', linewidth=2)
axes[0, 0].set_title('Funciones Trigonométricas')
axes[0, 0].set_xlabel('x')
axes[0, 0].set_ylabel('y')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)
