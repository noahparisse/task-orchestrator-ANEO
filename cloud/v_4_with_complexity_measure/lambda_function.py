import networkx as nx
import json
from min_min import read_graphe, min_min_schedule, convert_schedule_to_json
from utilities import *
from complexity_measures import *

def lambda_handler(event, context):
    try:
        # Exemple de paramètres par défaut
        default_event = {
            "measure_time_vs_N": True,
            "measure_time_vs_M": True,
            "measure_memory_vs_N": True,
            "num_tasks_range": [100, 3100, 100],  # [start, stop, step]
            "machines_range": [1, 70, 3],  # [start, stop, step]
            "fixed_machines": 2,
            "fixed_tasks": 1000
        }

        # Initialiser les paramètres manquants dans l'événement
        for key in default_event:
            if not key in event:
                event[key] = default_event[key]

        results = {}
        
        # Si on doit mesurer la complexité en temps et en mémoire, on la calcule sur les mêmes graphes, pour minimiser le nombre de graphes nécessaires à générer
        if event["measure_time_vs_N"] and event["measure_memory_vs_N"]:
            N_values = list(range(event["num_tasks_range"][0], event["num_tasks_range"][1], event["num_tasks_range"][2]))
            times, peak_memories = measure_time_and_memory_vs_N(machines=event["fixed_machines"], N_values=N_values)
            results["time_vs_N"] = {"N_values": N_values, "times": times, "fixed_machines": event["fixed_machines"]}
            results["memory_vs_N"] = {"N_values": N_values, "peak_memories": peak_memories, "fixed_machines": event["fixed_machines"]}

        # Mesurer le temps en fonction du nombre de tâches (N), si pas de mesure de la complexité en mémoire
        if event["measure_time_vs_N"] and not event["measure_memory_vs_N"]:
            N_values = list(range(event["num_tasks_range"][0], event["num_tasks_range"][1], event["num_tasks_range"][2]))
            times = measure_time_vs_N(machines=event["fixed_machines"], N_values=N_values)
            results["time_vs_N"] = {"N_values": N_values, "times": times, "fixed_machines": event["fixed_machines"]}

        # Mesurer le temps en fonction du nombre de machines (M)
        if event["measure_time_vs_M"]:
            M_values = list(range(event["machines_range"][0], event["machines_range"][1], event["machines_range"][2]))
            times = measure_time_vs_M(num_tasks=event["fixed_tasks"], M_values = M_values)
            results["time_vs_M"] = {"M_values": M_values, "times": times, "fixed_tasks": event["fixed_tasks"]}

        # Mesurer la mémoire en fonction du nombre de tâches (N), si pas de mesure de la complexité temporelle
        if event["measure_memory_vs_N"] and not event["measure_time_vs_N"]:
            N_values = list(range(event["num_tasks_range"][0], event["num_tasks_range"][1], event["num_tasks_range"][2]))
            peak_memories = measure_memory_vs_N(machines=event["fixed_machines"], N_values=N_values)
            results["memory_vs_N"] = {"N_values": N_values, "peak_memories": peak_memories, "fixed_machines": event["fixed_machines"]}

        return results

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Une erreur s'est produite : {str(e)}"
        }