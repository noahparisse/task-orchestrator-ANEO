import json
import matplotlib.pyplot as plt

def measure_time_vs_N(data):
    """
    Mesure le temps d'exécution de l'algorithme en faisant varier le nombre de tâches N,
    pour un nombre fixe de machines.
    """
    x = data["time_vs_N"]["N_values"]
    y = data["time_vs_N"]["times"]
    plt.figure()
    plt.plot(x, y, marker='o')
    plt.xlabel("Nombre de tâches (N)")
    plt.ylabel("Temps d'exécution (secondes)")
    plt.title("Temps d'exécution vs Nombre de tâches (machines fixées)")
    plt.grid(True)
    plt.show()

def measure_time_vs_M(data):
    """
    Mesure le temps d'exécution en faisant varier le nombre de machines (M) pour un nombre fixe de tâches.
    """
    x = data["time_vs_M"]["M_values"]
    y = data["time_vs_M"]["times"]
    plt.figure()
    plt.plot(x, y, marker='o')
    plt.xlabel("Nombre de machines (M)")
    plt.ylabel("Temps d'exécution (secondes)")
    plt.title("Temps d'exécution vs Nombre de machines (tâches fixées)")
    plt.grid(True)
    plt.show()

def measure_memory_vs_N(data):
    """
    Mesure l'utilisation mémoire de l'algorithme en faisant varier le nombre de tâches N.
    Nécessite memory_profiler.
    """
    x = data["memory_vs_N"]["N_values"]
    y = data["memory_vs_N"]["peak_memories"]
    plt.figure()
    plt.plot(x, y, marker='o')
    plt.xlabel("Nombre de tâches (N)")
    plt.ylabel("Mémoire maximale (MB)")
    plt.title("Utilisation mémoire vs Nombre de tâches")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    
    with open("response.json", "r") as file:
        data = json.load(file)
    # Pour mesurer le temps d'exécution en fonction de N (avec M fixé, par exemple M=2)
    if "time_vs_N" in data:
        measure_time_vs_N(data)
    
    # Pour mesurer le temps d'exécution en fonction de M (avec N fixé, par exemple N=1000)
    if "time_vs_M" in data:
        measure_time_vs_M(data)
    
    # Pour mesurer l'utilisation mémoire en fonction de N
    if "memory_vs_N" in data:
        measure_memory_vs_N(data)