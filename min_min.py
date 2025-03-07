import networkx as nx
import matplotlib.pyplot as plt
import json

def parse_time(time_str):
    """
    Convertit une durée au format hh:mm:ss.ssssss en secondes
    """
    
    parts = time_str.split(":")
    h, m = int(parts[0]), int(parts[1])
    
    if "." in parts[2]: # Si il y a des décimales
        s, fraction = parts[2].split(".")
        s = int(s)
        fraction = float("0." + fraction)  
    else:  # Si il y a que des secondes
        s = int(parts[2])
        fraction = 0.0
    
    return h * 3600 + m * 60 + s + fraction 

def read_graphe(json_path):
    """
    Charge un graphe de tâches depuis un fichier json
    """
    with open(json_path, "r") as f:
        data = json.load(f)
    G = nx.DiGraph()
    
    for task in data["tasks"]:
        G.add_node(task["id"], time=task["duration"], memory=task["memory"])
        for dep in task["dependencies"]:
            G.add_edge(dep, task["id"])
    
    return G

# rend un graphe avec cette architecture : 
# Nœuds : [('task1', {'duration': 10, 'memory': 512}), ('task2', {'duration': 15, 'memory': 1024}), ('task3', {'duration': 5, 'memory': 256})]
# Arêtes : [('task1', 'task2'), ('task1', 'task3'), ('task1', 'task5'), ('task1', 'task7')]
# Pour obtenir les attributs d'un nœud : G.nodes['task1']
# Pour obtenir le temps d'exécution d'un nœud : G.nodes['task1']['duration']
# Pour obtenir le besoin en mémoire d'un nœud : G.nodes['task1']['memory']

def get_ready_tasks(G, unscheduled, schedule):
    """
    Retourne la liste des tâches prêtes à être planifiées.

    Une tâche est considérée prête si toutes ses dépendances (prédécesseurs)
    sont déjà planifiées (présentes dans le dictionnaire 'schedule').

    Args:
        G (networkx.DiGraph): Le graphe des tâches.
        unscheduled (set): Ensemble des tâches non encore planifiées.
        schedule (dict): Dictionnaire de planification courant.

    Returns:
        list: Liste des tâches prêtes.
    """
    ready_tasks = []
    for task in unscheduled:
        preds = list(G.predecessors(task))
        if all(pred in schedule for pred in preds):
            ready_tasks.append(task)
    return ready_tasks

def best_assignment_for_task(G, task, schedule, machine_ready):
    """
    Détermine la meilleure affectation pour une tâche donnée.

    Pour une tâche, cette fonction calcule le temps de démarrage et d'achèvement
    possible sur chacune des machines en tenant compte :
      - de la disponibilité de la machine,
      - du temps de fin des tâches dont dépend la tâche considérée.
    
    Args:
        G (networkx.DiGraph): Le graphe des tâches.
        task (str): La tâche à planifier.
        schedule (dict): Dictionnaire de planification courant.
        machine_ready (list): Liste des temps de disponibilité pour chaque machine.
    
    Returns:
        tuple: (machine_index, start_time, finish_time) correspondant à la meilleure affectation.
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

    Chaque nœud du graphe G représente une tâche avec un attribut "time" indiquant le temps de traitement.
    L'algorithme sélectionne, parmi les tâches prêtes, celle qui peut être terminée le plus tôt sur une machine donnée.

    Args:
        G (networkx.DiGraph): Le graphe d'ordonnancement (DAG).
        num_machines (int): Nombre de machines homogènes disponibles.

    Returns:
        tuple: (schedule, makespan) où schedule est un dictionnaire de la forme
               {tâche: (machine, start_time, finish_time)} et makespan est le temps global d'exécution.
    """
    # Initialisation des temps de disponibilité pour chaque machine
    machine_ready = [0] * num_machines  
    schedule = {}
    unscheduled = set(G.nodes())
    
    while unscheduled:
        # Sélectionner les tâches prêtes à être planifiées
        ready_tasks = get_ready_tasks(G, unscheduled, schedule)
        if not ready_tasks:
            raise Exception("Aucune tâche prête : le graphe comporte peut-être un cycle.")
        
        # Recherche de la meilleure assignation parmi les tâches prêtes
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

def plot_schedule_graph(G, tasks, title="Graphe d'ordonnancement de tâches"):
    """
    Affiche le graphe d'ordonnancement avec les temps de traitement indiqués sur chaque nœud.

    Args:
        G (networkx.DiGraph): Le graphe des tâches.
        tasks (dict): Dictionnaire associant chaque tâche à son temps de traitement.
        title (str): Titre du graphique.
    """
    pos = nx.spring_layout(G)
    labels = {node: f"{node}\n({tasks[node]})" for node in G.nodes()}
    nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightgreen', 
            node_size=800, font_size=10, arrows=True)
    plt.title(title)
    plt.show()

def example_complex_graph():
    """
    Exemple d'un graphe d'ordonnancement plus complexe.

    Ce graphe utilise 2 machines et 6 tâches avec dépendances. Les temps de traitement
    et les dépendances sont définis explicitement. Le makespan optimal (temps global d'exécution)
    est calculé et affiché.
    """
    # Création du graphe orienté (DAG)
    G = nx.DiGraph()
    
    # Définition des tâches et de leur temps de traitement
    tasks = {
        "A": 2,
        "B": 3,
        "C": 2,
        "D": 4,
        "E": 3,
        "F": 5
    }
    for task, t in tasks.items():
        G.add_node(task, time=t)
    
    # Définition des dépendances
    G.add_edge("A", "C")
    G.add_edge("A", "D")
    G.add_edge("B", "E")
    G.add_edge("C", "E")
    G.add_edge("D", "F")
    G.add_edge("E", "F")
    
    # Application de l'algorithme Min-Min sur 2 machines
    schedule, makespan = min_min_schedule(read_graphe("graph.json"), num_machines=2)
    
    # Affichage du planning des tâches
    print("Planning des tâches:")
    for task, (machine, start, finish) in schedule.items():
        print(f"  Tâche {task} -> Machine {machine} : démarre à {start}, termine à {finish}")
    print("Temps d'exécution global (makespan) :", makespan)
    
    # Affichage du graphe d'ordonnancement
    plot_schedule_graph(G, tasks)

if __name__ == "__main__":
    example_complex_graph()
