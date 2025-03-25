import networkx as nx
import json
from utilities import *


def read_graphe(input_key="input_data/graph.json", data=None):
    """
    Charge un graphe de tâches depuis un fichier json.
    Les tâches utilisent leur attribut "id" comme nom.
    """
    local_file_path = "/tmp/"+get_file_name(input_key)
    download_from_bucket(local_file_path, input_key)
    
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

def update_ready_tasks(G, ready_tasks, unscheduled, schedule, completed_task):
    """
    Met à jour l'ensemble des tâches prêtes (ready_tasks) en vérifiant, pour chaque successeur
    de la tâche complétée, si toutes ses dépendances sont désormais planifiées.
    """
    for succ in G.successors(completed_task):
        if succ in unscheduled and all(pred in schedule for pred in G.predecessors(succ)):
            ready_tasks.add(succ)

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
    Implémente l'algorithme Min-Min pour le scheduling sur num_machines machines en utilisant une approche
    incrémentale pour ne recalculer que les tâches potentiellement prêtes.
    
    Retourne le planning sous la forme d'un dictionnaire : { tâche: (machine, start_time, finish_time) }
    ainsi que le makespan global.
    """
    machine_ready = [0] * num_machines  # Temps de disponibilité initial pour chaque machine
    schedule = {}
    unscheduled = set(G.nodes())
    
    # Initialisation : tâches sans prédécesseurs sont prêtes
    ready_tasks = { task for task in unscheduled if not list(G.predecessors(task)) }
    
    while unscheduled:
        if not ready_tasks:
            raise Exception("Aucune tâche prête : le graphe comporte peut-être un cycle.")
        
        best_task = None
        best_machine = None
        best_start = None
        best_finish = float('inf')
        
        # Sélection de la tâche optimale parmi ready_tasks
        for task in ready_tasks:
            m, start, finish = best_assignment_for_task(G, task, schedule, machine_ready)
            if finish < best_finish:
                best_finish = finish
                best_task = task
                best_machine = m
                best_start = start
        
        # Planification de la tâche sélectionnée
        schedule[best_task] = (best_machine, best_start, best_finish)
        machine_ready[best_machine] = best_finish
        unscheduled.remove(best_task)
        ready_tasks.remove(best_task)
        
        # Mise à jour incrémentale des tâches prêtes pour les successeurs de la tâche planifiée
        update_ready_tasks(G, ready_tasks, unscheduled, schedule, best_task)
    
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