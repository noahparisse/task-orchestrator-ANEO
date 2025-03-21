import boto3
import networkx as nx
import json
from min_min import read_graphe, min_min_schedule, convert_schedule_to_json

def lambda_handler(event, context):
    try:
        """    
        Le planning final est affiché au format JSON souhaité.
        """
        
        # Nombre de machines (cores)
        num_machines = 2
        G = read_graphe()
        schedule, makespan = min_min_schedule(G, num_machines)
        
        # Conversion du planning en format JSON souhaité
        final_schedule = convert_schedule_to_json(schedule, num_machines)
        
        # Configuration du client S3
        s3 = boto3.client('s3')
        
        # S3 bucket et clé de l'objet à lire
        bucket_name = "central-supelec-data-groupe1"

        # Enregistrer le graphe dans un fichier JSON
        output_file_path = '/tmp/ordo.json'
        with open(output_file_path, 'w') as f:
            json.dump(final_schedule, f, indent=4)
        
        # Spécifier le chemin de destination sur S3 pour le fichier de sortie
        destination_key = "output_data/ordo.json"  # Le fichier sera enregistré dans output_data/

        # Télécharger le fichier modifié vers S3
        s3.upload_file(output_file_path, bucket_name, destination_key)
        return {"StatusCode" : 600,
                "body" : f"L'ordonnancement a été téléversé dans {bucket_name} et le makespan est de {makespan}"}

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Une erreur s'est produite : {str(e)}"
        }