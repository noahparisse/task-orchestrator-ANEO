import boto3
import networkx as nx
import random
import json
import os

def upload_on_bucket(local_path, bucket_key, bucket_name = "central-supelec-data-groupe1"):
    
    # Configuration du client S3
    s3 = boto3.client('s3')

    # Télécharger le fichier modifié vers S3
    s3.upload_file(local_path, bucket_name, bucket_key)
    
    return {"StatusCode" : 100,
            "body" : f"Le document {local_path} a été téléversé dans {bucket_name}",
            "destination_key" : bucket_key,
            "bucket_name": bucket_name }

def download_from_bucket(local_path, bucket_key, bucket_name = "central-supelec-data-groupe1"):
    
    # Configuration du client S3
    s3 = boto3.client('s3')

    # Télécharger le fichier JSON depuis S3
    s3.download_file(bucket_name, bucket_key, local_path)
    
    return {"StatusCode" : 100,
            "body" : f"Le document {bucket_key} a été téléchargé depuis {bucket_name}",
            "local_path" : local_path}
    
def generate_task_graph(num_tasks, max_dependencies=None, random_seed=None):
    """ Génère un graphe de tâches avec des dépendances aléatoires """

    # Initialiser la graine aléatoire si fournie
    if random_seed is None:
        random_seed = random.randint(0, 99999)  # Générer une graine aléatoire
    random.seed(random_seed)

    G = nx.DiGraph()  # Graphe orienté
    tasks = [f"task{i}" for i in range(1, num_tasks + 1)]  # Création des tâches
    G.add_nodes_from(tasks)  # Ajout des tâches comme nœuds
    
    task_data = {}  # Dictionnaire pour stocker les infos des tâches

    # Déterminer max_dependencies aléatoirement si non fourni
    if max_dependencies is None:
        max_dependencies = random.randint(1, num_tasks - 1)  # Plus de flexibilité

    for task in tasks:
        # Génération aléatoire des attributs
        duration = random.randint(5, 30)  # Durée entre 5 et 30 unités
        memory = random.choice([256, 512, 1024, 2048])  # Mémoire en Mo
        
        # Déterminer les dépendances
        if task != "task1":  # La première tâche n'a pas de dépendances
            num_deps = random.randint(1, min(max_dependencies, len(tasks) - 1))  
            possible_parents = [t for t in tasks if t < task]  # Seulement les tâches précédentes
            selected_parents = random.sample(possible_parents, min(len(possible_parents), num_deps))  # Choix aléatoire
        else:
            selected_parents = []
        
        # Ajouter les infos au dictionnaire
        task_data[task] = {
            "id": task,
            "duration": duration,
            "memory": memory,
            "dependencies": selected_parents
        }
        
        # Ajouter les dépendances dans le graphe
        for dep in selected_parents:
            G.add_edge(dep, task)
    
    return G, task_data, random_seed, max_dependencies

def save_graph_to_json(task_data, num_tasks, max_dependencies, random_seed):
    """ Sauvegarde le graphe sous format JSON """
    graph_json = {
        "graph_id": f"task_graph_ntask_{num_tasks}_max_dep_{max_dependencies}_seed_{random_seed}",
        "random_seed": random_seed,
        "max_dependencies": max_dependencies,
        "tasks": list(task_data.values())  # Convertir le dictionnaire en liste
    }

    filename = f"task_graph_{num_tasks}_{max_dependencies}_seed_{random_seed}.json"
    bucket_key = "output_data/"+filename
    local_path = "/tmp/"+filename
    
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(graph_json, f, indent=4)  # Enregistrement avec indentation
    tmp = upload_on_bucket(local_path, bucket_key)  # Enregistrement du graphe en .json sur le S3
    bucket_name = tmp["bucket_name"]
    
    if os.path.exists(local_path):  # Supprimer le fichier temporaire après utilisation
        os.remove(local_path)
    
    return bucket_key, bucket_name

def graph_generator(num_tasks, random_seed = None, max_dependencies = None):
    """ Fonction principale du générateur de graphes : génère un graphe de tâches avec dépendances aléatoires et l'enregistre en JSON.
            - num_tasks : Nombre de tâches à générer
            - random_seed : Graine aléatoire pour reproduire le graphe (optionnel)
            - max_dependencies : Nombre maximal de dépendances par tâche (optionnel, aléatoire si absent)"""

    # Générer le graphe avec ou sans seed et max_dependencies
    G, task_data, random_seed, max_dependencies = generate_task_graph(num_tasks, max_dependencies, random_seed)

    assert nx.is_directed_acyclic_graph(G), f"Le graphe généré task_graph_{num_tasks}_{max_dependencies}_seed_{random_seed}.json contient un cycle !"

    # Sauvegarde en JSON
    bucket_key, bucket_name = save_graph_to_json(task_data, num_tasks, max_dependencies, random_seed)
    
    return {"body" : f"Le graphe généré {bucket_key} est disponible dans le bucket {bucket_name}",
            "graph_bucket_key" : bucket_key,
            "bucket_name" : bucket_name}

def get_file_name(path):
    n = 0
    for i in range(len(path)-1, -1, -1):
        if path[i]=='/':
            n = i+1
            break
    return path[n:]