import boto3
import json

def lambda_handler(event, context):
    try:
        # Configuration du client S3
        s3 = boto3.client('s3')
        
        # S3 bucket et clé de l'objet à lire
        bucket_name = "central-supelec-data-groupe1"
        input_key = "input_data/graph.json"  # Remplacez par la clé réelle du fichier JSON

        # Télécharger le fichier JSON depuis S3
        local_file_path = "/tmp/graph.json"
        s3.download_file(bucket_name, input_key, local_file_path)

        # Charger les données JSON depuis le fichier téléchargé
        with open(local_file_path, "r") as file:
            data = json.load(file)

        # Traitement des données JSON (par exemple, ajouter un champ 'processed')
        data['processed'] = True

        # Enregistrer le fichier modifié localement
        output_file_path = "/tmp/resultat.json"
        with open(output_file_path, "w") as file:
            json.dump(data, file)

        # Spécifier le chemin de destination sur S3 pour le fichier de sortie
        destination_key = "output_data/resultat.json"  # Le fichier sera enregistré dans output_data/

        # Télécharger le fichier modifié vers S3
        s3.upload_file(output_file_path, bucket_name, destination_key)

        return {
            "statusCode": 200,
            "body": f"Le fichier {destination_key} a été téléchargé avec succès dans {bucket_name}!"
        }

    except Exception as e:
        # En cas d'erreur, loguer l'erreur
        print(f"Erreur : {str(e)}")
        return {
            "statusCode": 500,
            "body": f"Une erreur s'est produite : {str(e)}"
        }
