import networkx as nx
import json
from min_min import read_graphe, min_min_schedule, convert_schedule_to_json
from utilities import *
import os

default_event = {
    "generate_a_graph" : True,
    "num_tasks" : 1000,
    "num_machines" : 1,
    "initial_key" : "graph.json",
    "destination_title" : "ordo.json",
}

def lambda_handler(context, event = default_event):
    try:
        # Pour se prémunir des infos manquantes dans event, on initialise les infos manquantes avec default_event
        for k in default_event:
            if not k in event:
                event[k]=default_event[k]
        
        # Récupération des informations nécessaires au lancement de l'ordonnancement
        if event["generate_a_graph"]:
            initial_key = graph_generator(event["num_tasks"])["filename"]
        else :
            initial_key = event["initial_key"]
        num_machines = event['num_machines']
        destination_file_title = event['destination_title']
        
        # Chargement du graphe
        G = read_graphe(initial_key)
        
        # Exécution de l'algo min_min
        schedule, makespan = min_min_schedule(G, num_machines)
        
        # Conversion du planning en format JSON souhaité
        final_schedule = convert_schedule_to_json(schedule, num_machines)

        # Enregistrer le graphe dans un fichier JSON
        output_local_path = '/tmp'+destination_file_title
        with open(output_local_path, 'w') as f:
            json.dump(final_schedule, f, indent=4)
        
        upload_on_bucket(output_local_path, destination_file_title)
        
        if os.path.exists(output_local_path):  # Supprimer le fichier temporaire après utilisation
            os.remove(output_local_path)
        
        return {"StatusCode" : 600,
                "body" : f"L'ordonnancement a été téléversé en tant que {destination_file_title} dans le S3. Le makespan est de {makespan}"}

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Une erreur s'est produite : {str(e)}"
        }