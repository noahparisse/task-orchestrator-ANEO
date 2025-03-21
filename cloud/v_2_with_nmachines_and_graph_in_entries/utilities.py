import boto3
import networkx as nx
import argparse
import random
import json

def upload_on_bucket(output_local_path, destination_file_title, bucket_name = "central-supelec-data-groupe1"):
    
    # Configuration du client S3
    s3 = boto3.client('s3')
    
    # Spécifier le chemin de destination sur S3 pour le fichier de sortie
    destination_key = "output_data/"+destination_file_title  # Le fichier sera enregistré dans output_data/

    # Télécharger le fichier modifié vers S3
    s3.upload_file(output_local_path, bucket_name, destination_key)
    
    return {"StatusCode" : 100,
            "body" : f"Le document {destination_file_title} a été téléversé dans {bucket_name}",
            "destination_key" : destination_key}

def download_from_bucket(destination_local_path, input_file_title, bucket_name = "central-supelec-data-groupe1"):
    
    # Configuration du client S3
    s3 = boto3.client('s3')
    
    # S3 bucket et clé de l'objet à lire
    input_key = "input_data/"+input_file_title

    # Télécharger le fichier JSON depuis S3
    s3.download_file(bucket_name, input_key, destination_local_path)
    
    return {"StatusCode" : 100,
            "body" : f"Le document {input_file_title} a été téléchargé depuis {bucket_name}",
            "local_path" : destination_local_path}