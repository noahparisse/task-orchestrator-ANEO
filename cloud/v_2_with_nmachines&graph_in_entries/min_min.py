import boto3
import networkx as nx
import json
from utilities import *

def parse_time(time_str):
    """
    Convertit une durée au format hh:mm:ss.ssssss en secondes.
    """
    parts = time_str.split(":")
    h, m = int(parts[0]), int(parts[1])
    
    if "." in parts[2]:  # S'il y a des décimales
        s, fraction = parts[2].split(".")
        s = int(s)
        fraction = float("0." + fraction)  
    else:  # S'il n'y a que des secondes
        s = int(parts[2])
        fraction = 0.0
    
    return h * 3600 + m * 60 + s + fraction 

def read_graphe(json_path="graph.json", data=None):
    """
    Charge un graphe de tâches depuis un fichier json.
    Les tâches utilisent leur attribut "id" comme nom.
    """
    try :
        local_file_path = "/tmp/graph.json"
        download_from_bucket(local_file_path, json_path)
        
        # Charger les données JSON depuis le fichier téléchargé
        with open(local_file_path, "r") as file:
            data = json.load(file)

        G = nx.DiGraph()
        
        for task in data["tasks"]:
            # On utilise "id" pour nommer la tâche
            G.add_node(task["id"], time=task["duration"], memory=task["memory"])
            for dep in task["dependencies"]:
                G.add_edge(dep, task["id"])
        
        return G
    except Exception as e :
        return 

def get_ready_tasks(G, unscheduled, schedule):
    """
    Retourne la liste des tâches prêtes à être planifiées.
    Une tâche est prête si toutes ses dépendances (prédécesseurs)
    sont déjà planifiées.
    """
    ready_tasks = []
    for task in unscheduled:
        preds = list(G.predecessors(task))
        if all(pred in schedule for pred in preds):
            ready_tasks.append(task)
    return ready_tasks

def best_assignment_for_task(G, task, schedule, machine_ready):
    """
    Pour une tâche donnée, détermine sur quelle machine et à quel moment elle peut être exécutée
    pour se terminer le plus tôt possible.
    """
    task_time = G.nodes[task].get("time", 1)
    preds = list(G.predecessors(task))
    earliest_dep_finish = max([schedule[pred][2] for pred in preds], default=0)
    
    best_machine = None
    best_start_time = None
    best_finish_time = float('inf')
    
    for m, ready_time in enumerate(machine_ready):
        start_time = max(ready_time, earliest_dep_finish)
        finish_time = start_time + task_time
        if finish_time < best_finish_time:
            best_finish_time = finish_time
            best_machine = m
            best_start_time = start_time
    return best_machine, best_start_time, best_finish_time

def min_min_schedule(G, num_machines):
    """
    Implémente l'algorithme Min-Min pour le scheduling sur 'num_machines' machines.
    
    Retourne un dictionnaire de planning sous la forme :
      { tâche: (machine, start_time, finish_time) }
    ainsi que le makespan global.
    """
    machine_ready = [0] * num_machines  # Temps de disponibilité initial pour chaque machine
    schedule = {}
    unscheduled = set(G.nodes())
    
    while unscheduled:
        ready_tasks = get_ready_tasks(G, unscheduled, schedule)
        if not ready_tasks:
            raise Exception("Aucune tâche prête : le graphe comporte peut-être un cycle.")
        
        best_task = None
        best_machine = None
        best_start = None
        best_finish = float('inf')
        
        for task in ready_tasks:
            m, start, finish = best_assignment_for_task(G, task, schedule, machine_ready)
            if finish < best_finish:
                best_finish = finish
                best_task = task
                best_machine = m
                best_start = start
                
        # Planification de la tâche sélectionnée
        schedule[best_task] = (best_machine, best_start, best_finish)
        machine_ready[best_machine] = best_finish  # Mise à jour de la disponibilité de la machine
        unscheduled.remove(best_task)
    
    makespan = max(machine_ready)
    return schedule, makespan

def convert_schedule_to_json(schedule, num_machines):
    """
    Convertit le planning calculé au format JSON souhaité.
    
    Format final :
    {
      "core_0": [{"task": "task1", "start_time": 0}, ...],
      "core_1": [{"task": "task2", "start_time": 21}, ...],
      ...
    }
    """
    final_schedule = {}
    for m in range(num_machines):
        final_schedule[f"core_{m}"] = []
        
    for task, (machine, start, finish) in schedule.items():
        final_schedule[f"core_{machine}"].append({"task": task, "start_time": start})
    
    # Tri des tâches sur chaque core par ordre croissant de start_time
    for core in final_schedule:
        final_schedule[core] = sorted(final_schedule[core], key=lambda x: x["start_time"])
    return final_schedule