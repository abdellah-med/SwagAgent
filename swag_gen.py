import json
from desc_gen import generate_description, agent  # Importer les fonctions de desc_gen.py

def extract_tags_and_endpoints(swagger_json_path, output_path):
    # Charger le fichier JSON Swagger
    with open(swagger_json_path, 'r', encoding='utf-8') as f:
        swagger_data = json.load(f)
    
    # Créer une liste pour stocker les résultats
    tags_list = []
    
    # Extraire les informations des tags
    for tag in swagger_data.get('tags', []):
        tag_name = tag.get('name')
        if tag_name:
            # Collecter les opérations associées à ce tag
            operations = []
            for path, methods in swagger_data.get('paths', {}).items():
                for method, operation in methods.items():
                    if tag_name in operation.get('tags', []):
                        operations.append({
                            'method': method,
                            'path': path,
                            'summary': operation.get('summary', '')
                        })
            
            # Générer la description en utilisant la fonction de desc_gen.py
            description = generate_description(tag_name, tag, operations)
            
            # Créer un dictionnaire pour chaque tag avec sa description
            tag_dict = {
                "name": tag_name,
                "description": description,
                "endpoints": []
            }
            tags_list.append(tag_dict)
    
    # Parcourir tous les chemins et collecter les endpoints pour chaque tag
    for path, methods in swagger_data.get('paths', {}).items():
        for method, operation in methods.items():
            # Obtenir les tags associés à cette opération
            operation_tags = operation.get('tags', [])
            
            # Ajouter le chemin à chaque tag associé
            for tag_name in operation_tags:
                # Trouver le dictionnaire correspondant au tag
                for tag_dict in tags_list:
                    if tag_dict["name"] == tag_name and path not in tag_dict["endpoints"]:
                        tag_dict["endpoints"].append(path)
    
    # Écrire le résultat dans un nouveau fichier JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tags_list, f, indent=2, ensure_ascii=False)
    
    print(f"Extraction terminée. {len(tags_list)} tags extraits vers {output_path}")
    return tags_list

# Exemple d'utilisation
if __name__ == "__main__":
    # Chemin d'entrée et de sortie
    input_file = "swagger.json"  # Chemin vers votre fichier swagger.json
    output_file = "tags_endpoints.json"  # Fichier de sortie
    
    result = extract_tags_and_endpoints(input_file, output_file)
    
    # Afficher le résultat
    print("\nAperçu du résultat:")
    print(json.dumps(result, indent=2, ensure_ascii=False))