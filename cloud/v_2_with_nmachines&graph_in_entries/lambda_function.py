import networkx as nx
import json
from min_min import read_graphe, min_min_schedule, convert_schedule_to_json
from utilities import *

default_event = {
    "num_machines" : 1,
    "initial_key" : "graph.json",
    "destination_title" : "ordo.json"
}

def lambda_handler(context, event = default_event):
    try:
        """    
        Le planning final est affiché au format JSON souhaité.
        """
        initial_key = default_event["initial_key"]
        num_machines = event['num_machines']
        destination_file_title = event['destination_title']
        
        # Chargement du graphe
        G = read_graphe(initial_key)
        
        # Exécution de l'algo min_min
        schedule, makespan = min_min_schedule(G, num_machines)
        
        # Conversion du planning en format JSON souhaité
        final_schedule = convert_schedule_to_json(schedule, num_machines)

        # Enregistrer le graphe dans un fichier JSON
        output_file_path = '/tmp/ordo.json'
        with open(output_file_path, 'w') as f:
            json.dump(final_schedule, f, indent=4)
        
        upload_on_bucket(output_file_path, destination_file_title)
        
        return {"StatusCode" : 600,
                "body" : f"L'ordonnancement a été téléversé en tant que {destination_file_title} dans le S3. Le makespan est de {makespan}"}

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Une erreur s'est produite : {str(e)}"
        }