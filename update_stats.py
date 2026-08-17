import os
import json
import requests

API_KEY = os.environ.get('ROOTME_API_KEY')

UID = "1075663" 

if not API_KEY:
    print("Erreur : ROOTME_API_KEY introuvable.")
    exit(1)

url = f"https://api.www.root-me.org/auteurs/{UID}"
headers = {"Cookie": f"api_key={API_KEY}"}

try:
    print(f"Récupération des stats pour l'UID {UID}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Erreur API Profil (Code {response.status_code}): {response.text}")
        exit(1)
        
    profil_data = response.json()
    
    points = int(profil_data.get("score", 0))
    rank = int(profil_data.get("position", 0))
    
    with open("stats.json", "w") as f:
        json.dump({"points": points, "rank": rank}, f, indent=4)
        
    print(f"Succès ! {points} points, Rang {rank}")
    
except Exception as e:
    print(f"Erreur lors de la mise à jour : {e}")