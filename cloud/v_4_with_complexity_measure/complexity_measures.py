import time
import networkx as nx
from min_min import min_min_schedule
from utilities import generate_task_graph
from memory_profiler import memory_usage

def measure_time_vs_N(machines, N_values):
    """
    Mesure le temps d'exécution de l'algorithme en faisant varier le nombre de tâches N,
    pour un nombre fixe de machines.
    """
    times = []
    for n in N_values:
        G, _, _, _ = generate_task_graph(num_tasks=n, max_dependencies=5)
        start = time.time()
        schedule, makespan = min_min_schedule(G, machines)
        end = time.time()
        exec_time = end - start
        times.append(exec_time)
    return times

def measure_time_vs_M(num_tasks, M_values):
    """
    Mesure le temps d'exécution en faisant varier le nombre de machines (M) pour un nombre fixe de tâches.
    """
    times = []
    # Générer un graphe fixe pour un nombre donné de tâches
    G, _, _, _ = generate_task_graph(num_tasks=num_tasks, max_dependencies=5)
    for m in M_values:
        start = time.time()
        schedule, makespan = min_min_schedule(G, m)
        end = time.time()
        exec_time = end - start
        times.append(exec_time)
    return times

def measure_memory_vs_N(machines, N_values):
    """
    Mesure l'utilisation mémoire de l'algorithme en faisant varier le nombre de tâches N.
    Nécessite memory_profiler.
    """
    peak_memories = []
    for n in N_values:
        G, _, _, _ = generate_task_graph(num_tasks=n, max_dependencies=5)
        # Mesurer la consommation mémoire pendant l'exécution de min_min_schedule 
        mem_usage = memory_usage((min_min_schedule, (G, machines)), interval=0.1)
        peak_memory = max(mem_usage)
        peak_memories.append(peak_memory)
    return peak_memories

def measure_time_and_memory_vs_N(machines, N_values):
    """
    Mesure le temps d'exécution et l'utilisation de la mémoire de l'algorithme en fonction du nombre de tâches N,
    pour un nombre fixe de machines.
    Cette fonction permet de générer 2 fois moins de graphes par rapport à l'utilisation consécutive des fonctions
    measure_time_vs_N() et measure_memory_vs_N().
    """
    times = []
    peak_memories = []
    for n in N_values:
        G, _, _, _ = generate_task_graph(num_tasks=n, max_dependencies=5)
        
        # Calcul du temps que prend l'exécution de l'algorithme d'ordonnancement
        start = time.time()
        schedule, makespan = min_min_schedule(G, machines)
        end = time.time()
        exec_time = end - start
        times.append(exec_time)
        
        # Mesure de l'utilisation mémoire de l'algorithme d'ordonnancement
        mem_usage = memory_usage((min_min_schedule, (G, machines)), interval=0.1)
        peak_memory = max(mem_usage)
        peak_memories.append(peak_memory)
    return times, peak_memories