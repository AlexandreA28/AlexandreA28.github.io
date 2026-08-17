import os
import json
import requests

API_KEY = os.environ.get('ROOTME_API_KEY')
PSEUDO = "Celestia"

if not API_KEY:
    print("Erreur : ROOTME_API_KEY introuvable.")
    exit(1)

# Paramètres de l'API Root-Me
url = f"https://api.www.root-me.org/auteurs?nom={PSEUDO}"
headers = {"Cookie": f"api_key={API_KEY}"}

try:
    response = requests.get(url, headers=headers)
    data = response.json()
    
    profil = data.get("0", {})
    
    points = int(profil.get("score", 0))
    rank = int(profil.get("position", 0))
    
    with open("stats.json", "w") as f:
        json.dump({"points": points, "rank": rank}, f, indent=4)
        
    print(f"Mise à jour réussie : {points} points, Rang {rank}")
    
except Exception as e:
    print(f"Erreur lors de la mise à jour : {e}")