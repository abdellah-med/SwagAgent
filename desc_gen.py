from agno.agent import Agent
from agno.models.google import Gemini
from dotenv import load_dotenv
import os
import json

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Vérification de la clé API
if not GEMINI_API_KEY:
    raise ValueError("La clé API GEMINI_API_KEY n'est pas définie dans les variables d'environnement.")

# Création de l'agent avec le modèle Gemini - approche "agent"
agent = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=GEMINI_API_KEY, temperature=0.3),
    description="Tu es un expert en documentation d'agents intelligents pour API.",
    instructions=[
        "Personnifie chaque tag Swagger comme un agent intelligent.",
        "Décris les fonctionnalités comme des actions que l'agent peut accomplir.",
        "Utilise des formulations comme 'cet agent peut...' ou 'l'agent s'occupe de...'",
        "La description doit être vivante et engageante (environ 50-75 mots).",
        "Donne la description directe sans rien ajouter, sans introduction ni conclusion."
    ], 
    markdown=True
)

def generate_description(tag_name, tag_info, operations):
    """
    Génère une description pour un tag Swagger en le présentant comme un agent.
    
    Args:
        tag_name (str): Le nom du tag
        tag_info (dict): Les informations du tag (description, externalDocs)
        operations (list): Liste des opérations associées à ce tag
    
    Returns:
        str: Description générée par l'IA
    """
    original_description = tag_info.get('description', '')
    
    # Créer un prompt pour l'agent avec une approche anthropomorphique
    prompt = f"""
Imagine que le tag API '{tag_name}' est un agent intelligent dans un système.

Description originale: {original_description}

Cet agent peut réaliser les actions suivantes:
"""
    
    # Ajouter les détails des opérations
    for op in operations:
        prompt += f"- {op.get('method', 'GET').upper()} {op.get('path', '')}: {op.get('summary', '')}\n"
    
    prompt += """
Rédige une description personnifiée de cet agent en expliquant ce qu'il peut faire, comment il aide les utilisateurs, 
et quelles sont ses principales capacités. Commence par "Cet agent..." ou une formulation similaire.
Assure-toi de décrire ses capacités de manière dynamique (par exemple: "l'agent gère...", "il peut...", "il s'occupe de...").
"""
    
    # Appeler l'agent pour générer la description
    response = agent.run(prompt)
    return response.content

def process_swagger_file(swagger_file_path):
    """
    Traite un fichier Swagger et génère des descriptions pour tous les tags.
    
    Args:
        swagger_file_path (str): Chemin vers le fichier JSON Swagger
        
    Returns:
        dict: Dictionnaire contenant les tags et leurs descriptions générées
    """
    # Charger le fichier JSON Swagger
    with open(swagger_file_path, 'r', encoding='utf-8') as f:
        swagger_data = json.load(f)
    
    # Traiter chaque tag
    results = []
    for tag in swagger_data.get('tags', []):
        tag_name = tag.get('name')
        if tag_name:
            print(f"Génération de description pour le tag '{tag_name}'...")
            
            # Collecter les informations du tag
            tag_info = next((t for t in swagger_data.get('tags', []) if t.get('name') == tag_name), None)
            
            # Collecter les opérations associées
            operations = []
            for path, methods in swagger_data.get('paths', {}).items():
                for method, operation in methods.items():
                    if tag_name in operation.get('tags', []):
                        operations.append({
                            'method': method,
                            'path': path,
                            'summary': operation.get('summary', '')
                        })
            
            # Générer la description
            description = generate_description(tag_name, tag_info, operations)
            
            # Collecter les endpoints
            endpoints = []
            for path, methods in swagger_data.get('paths', {}).items():
                for method, operation in methods.items():
                    if tag_name in operation.get('tags', []):
                        if path not in endpoints:
                            endpoints.append(path)
            
            # Créer l'entrée pour ce tag
            tag_entry = {
                "name": tag_name,
                "description": description,
                "endpoints": endpoints
            }
            results.append(tag_entry)
            print(f"Description générée pour '{tag_name}': {description[:50]}...")
    
    return results
