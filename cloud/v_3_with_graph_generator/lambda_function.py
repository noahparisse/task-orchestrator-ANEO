import networkx as nx
import json
from min_min import read_graphe, min_min_schedule, convert_schedule_to_json
from utilities import *
import os

default_event = {
    "generate_a_graph" : True,
    "num_tasks" : 1000,
    "num_machines" : 1,
    "input_key" : "input_data/graph.json",
    "output_key" : "output_data/ordo.json",
}

def lambda_handler(event, context):
    try:
        # Pour se prémunir des infos manquantes dans event, on initialise les infos manquantes avec default_event
        for k in default_event:
            if not k in event:
                event[k]=default_event[k]
        
        # Récupération des informations nécessaires au lancement de l'ordonnancement
        if event["generate_a_graph"]:
            input_key = graph_generator(event["num_tasks"])["graph_bucket_key"]
        else :
            input_key = event["input_key"]
        num_machines = event['num_machines']
        output_key = event['output_key']
        
        # Chargement du graphe
        G = read_graphe(input_key)
        
        # Exécution de l'algo min_min
        schedule, makespan = min_min_schedule(G, num_machines)
        
        # Conversion du planning en format JSON souhaité
        final_schedule = convert_schedule_to_json(schedule, num_machines)

        # Enregistrer le graphe dans un fichier JSON
        output_local_path = '/tmp/'+get_file_name(output_key)
        with open(output_local_path, 'w') as f:
            json.dump(final_schedule, f, indent=4)
        
        upload_on_bucket(output_local_path, output_key)
        
        if os.path.exists(output_local_path):  # Supprimer le fichier temporaire après utilisation
            os.remove(output_local_path)
        
        return {"StatusCode" : 600,
                "body" : f"L'ordonnancement a été téléversé en tant que {output_key} dans le S3. Le makespan est de {makespan}"}

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Une erreur s'est produite : {str(e)}"
        }