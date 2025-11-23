import matplotlib.pyplot as plt
import numpy as np

# Configuración general
plt.rcParams['font.family'] = 'sans-serif'

# ==========================================
# 1. DEFINICIÓN DE DATOS (INTACTO)
# ==========================================

coords = {
    0: (5, 5),   # Depósito Central
    1: (1, 8), 2: (3, 8), 3: (1, 6), 4: (3, 6),
    5: (4, 9), 6: (6, 9), 7: (6, 7), 8: (5, 11),
    9: (8, 6), 10: (9, 8), 11: (9, 4), 12: (7, 4)
}

def calculate_route_cost(coords, routes):
    total_distance = 0.0
    for route in routes:
        full_route = [0] + route + [0]
        for i in range(len(full_route) - 1):
            u, v = full_route[i], full_route[i+1]
            total_distance += np.linalg.norm(np.array(coords[u]) - np.array(coords[v]))
    return total_distance

def plot_step_phase(ax, coords, routes, title, highlight_edges=None, movement_type=None, total_cost=None, step_number=0, primary_action_type=None):
    ax.set_facecolor('white')
    route_colors = ['#1E90FF', '#D02090', '#32CD32']

    # DIBUJAR RUTAS
    for idx, route in enumerate(routes):
        color = route_colors[idx % len(route_colors)]
        full_route = [0] + route + [0]
        x = [coords[node][0] for node in full_route]
        y = [coords[node][1] for node in full_route]

        alpha_val = 0.2 if movement_type in ['cut', 'add'] else 0.8
        width_val = 1.5 if movement_type in ['cut', 'add'] else 2.0

        ax.plot(x, y, color=color, linestyle='-', linewidth=width_val, alpha=alpha_val, zorder=1)

    # RESALTAR MOVIMIENTOS
    if highlight_edges:
        for u, v, tipo in highlight_edges:
            ux, uy = coords[u]
            vx, vy = coords[v]

            current_alpha = 1.0
            if primary_action_type is not None and tipo != primary_action_type:
                current_alpha = 0.2

            if tipo == 'cut':
                ax.plot([ux, vx], [uy, vy], color='red', linestyle='--', linewidth=2.5, zorder=4, alpha=current_alpha)
                # Cruz en el medio
                ax.text((ux+vx)/2, (uy+vy)/2, '✖', color='red', fontsize=14, ha='center', va='center', zorder=5, fontweight='bold', alpha=current_alpha)
            elif tipo == 'add':
                ax.plot([ux, vx], [uy, vy], color='#00AA00', linestyle='-', linewidth=2.5, zorder=4, alpha=current_alpha)

    # DIBUJAR NODOS (INTACTO)
    dx, dy = coords[0]
    ax.scatter(dx, dy, c='gold', marker='s', s=200, zorder=10, edgecolors='black')
    ax.text(dx, dy, 'D', color='black', fontsize=10, ha='center', va='center', zorder=11, fontweight='bold')

    for node_id, pos in coords.items():
        if node_id == 0: continue
        cx, cy = pos
        border_color = 'gray'
        for r_idx, r in enumerate(routes):
            if node_id in r:
                border_color = route_colors[r_idx]
                break
        ax.scatter(cx, cy, c='white', s=200, zorder=10, edgecolors=border_color, linewidth=2)
        ax.text(cx, cy, f'C{node_id}', color='black', fontsize=9, ha='center', va='center', zorder=11, fontweight='bold')

    # Habilitar los ejes de coordenadas y añadir etiquetas
    ax.set_xticks(np.arange(0, 11, 2))
    ax.set_yticks(np.arange(0, 12, 2))
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_aspect('equal')

    # Eliminar el título del gráfico
    # Reemplazar ax.set_title con ax.text para posicionar el título dentro del recuadro
    # title_text = ""
    # if total_cost:
    #     title_text = f"{step_number}. {title}\nCosto: {total_cost:.2f}"
    # else:
    #     title_text = f"{step_number}. {title}"

    # ax.text(0.5, 0.98, title_text,
    #         horizontalalignment='center',
    #         verticalalignment='top',
    #         transform=ax.transAxes,
    #         fontsize=9,
    #         fontweight='bold',
    #         bbox=dict(boxstyle="round,pad=0.3", fc='white', ec='none', lw=0, alpha=0.8))

# ==========================================
# 2. ESCENARIO SECUENCIAL (LÓGICA INVERSA)
# ==========================================

# Definimos las rutas igual que antes para mantener consistencia de datos
r1_bad = [1, 4, 3, 2]
r2_bad = [5, 8, 6, 7]
r3_init = [12, 11, 9, 10]
routes_0 = [r1_bad, r2_bad, r3_init] # El peor estado

r1_fix = [1, 3, 4, 2]
routes_1 = [r1_fix, r2_bad, r3_init] # Después de 2-opt

r2_fix = [5, 6, 8, 7]
routes_2 = [r1_fix, r2_fix, r3_init] # Después de 3-opt

r2_cross = [5, 9, 8, 7]
r3_cross = [12, 11, 6, 10]
routes_3 = [r1_fix, r2_cross, r3_cross] # El mejor estado

# --- DEFINICIÓN DE TRANSICIONES INVERSAS ---

# PASO 1: Deshacer Cross-Exchange (4 Aristas)
# Vamos de routes_3 hacia routes_2
# Lo que antes se AGREGÓ para llegar a 3, ahora hay que CORTARLO para volver a 2.
# Lo que antes se CORTÓ para llegar a 3, ahora hay que AGREGARLO para volver a 2.

# Aristas en routes_3 que eliminamos
rev_4opt_cut = [
    (5, 9, 'cut'), (9, 8, 'cut'),
    (11, 6, 'cut'), (6, 10, 'cut')
]
# Aristas de routes_2 que restauramos
rev_4opt_add = [
    (5, 6, 'add'), (6, 8, 'add'),
    (11, 9, 'add'), (9, 10, 'add')
]

# PASO 2: Deshacer 3-Opt (3 Aristas)
# Vamos de routes_2 hacia routes_1
rev_3opt_cut = [(5, 6, 'cut'), (6, 8, 'cut'), (8, 7, 'cut')] # Las que existen en routes_2
rev_3opt_add = [(5, 8, 'add'), (8, 6, 'add'), (6, 7, 'add')] # Restaurar original

# PASO 3: Deshacer 2-Opt (2 Aristas)
# Vamos de routes_1 hacia routes_0
rev_2opt_cut = [(1, 3, 'cut'), (4, 2, 'cut')] # Las arregladas
rev_2opt_add = [(1, 4, 'add'), (3, 2, 'add')] # Las malas originales


# ==========================================
# 3. GENERACIÓN GRÁFICA (SECUENCIA INVERTIDA)
# ==========================================
fig, axes = plt.subplots(2, 5, figsize=(24, 10))
axes = axes.flatten()
fig.suptitle('Secuencia Inversa: Cross-Exchange (4 aristas) -> 3-Opt (3 aristas) -> 2-Opt (2 aristas)', fontsize=18, fontweight='bold')

# --- FILA 1 ---

# 1. Empezamos con el estado "Final" (routes_3)
c3 = calculate_route_cost(coords, routes_3)
plot_step_phase(axes[0], coords, routes_3, "Estado Inicial", total_cost=c3, step_number=1)

# 2. Aplicamos reversa de 4-Opt (Cortar)
plot_step_phase(axes[1], coords, routes_3, "4-Opt", highlight_edges=rev_4opt_cut, movement_type='cut', step_number=2, primary_action_type='cut')

# 3. Aplicamos reversa de 4-Opt (Agregar)
plot_step_phase(axes[2], coords, routes_3, "4-Opt", highlight_edges=rev_4opt_cut + rev_4opt_add, movement_type='add', step_number=3, primary_action_type='add')

# 4. Resultado intermedio (routes_2)
c2 = calculate_route_cost(coords, routes_2)
plot_step_phase(axes[3], coords, routes_2, "Resultado 4-Opt", total_cost=c2, step_number=4)

# 5. Aplicamos reversa de 3-Opt (Cortar)
plot_step_phase(axes[4], coords, routes_2, "3-Opt", highlight_edges=rev_3opt_cut, movement_type='cut', step_number=5, primary_action_type='cut')

# --- FILA 2 ---

# 6. Aplicamos reversa de 3-Opt (Agregar)
plot_step_phase(axes[5], coords, routes_2, "3-Opt", highlight_edges=rev_3opt_cut + rev_3opt_add, movement_type='add', step_number=6, primary_action_type='add')

# 7. Resultado intermedio (routes_1)
c1 = calculate_route_cost(coords, routes_1)
plot_step_phase(axes[6], coords, routes_1, "Resultado 3-Opt", total_cost=c1, step_number=7)

# 8. Aplicamos reversa de 2-Opt (Cortar)
plot_step_phase(axes[7], coords, routes_1, "2-Opt", highlight_edges=rev_2opt_cut, movement_type='cut', step_number=8, primary_action_type='cut')

# 9. Aplicamos reversa de 2-Opt (Agregar)
plot_step_phase(axes[8], coords, routes_1, "2-Opt", highlight_edges=rev_2opt_cut + rev_2opt_add, movement_type='add', step_number=9, primary_action_type='add')

# 10. Estado Final (routes_0 - El malo original)
c0 = calculate_route_cost(coords, routes_0)
plot_step_phase(axes[9], coords, routes_0, "Resultado Final", total_cost=c0, step_number=10)

plt.tight_layout()
plt.subplots_adjust(top=0.90)
plt.savefig('CVRP_Inverse_kOpt_Sequence.png', dpi=150, facecolor='white')
print("Gráfico generado con éxito: Secuencia invertida (4-Opt -> 3-Opt -> 2-Opt).")
plt.show()