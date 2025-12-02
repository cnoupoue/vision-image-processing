# Définition des types de cases
TYPE_PROPERTY = "property"      # Rue/Personnage
TYPE_STATION = "station"        # Gare (Ici ce sont des lieux ou persos de soutien)
TYPE_UTILITY = "utility"        # Compagnie (Eau/Elec)
TYPE_CHANCE = "chance"          # Carte Mission (Chance)
TYPE_COMMUNITY = "community"    # Carte Entrainement (Caisse de communauté)
TYPE_TAX = "tax"                # Taxe
TYPE_SPECIAL = "special"        # Départ, Prison, Parc, Allez en Prison

# CODE COULEUR (Pour l'affichage HTML/CSS futur)
COLOR_BROWN = "#8e44ad"       # Marron (Konohamaru/Iruka)
COLOR_LIGHT_BLUE = "#3498db"  # Bleu Ciel
COLOR_PINK = "#e91e63"        # Rose
COLOR_ORANGE = "#e67e22"      # Orange
COLOR_RED = "#c0392b"         # Rouge
COLOR_YELLOW = "#f1c40f"      # Jaune
COLOR_GREEN = "#27ae60"       # Vert
COLOR_DARK_BLUE = "#2c3e50"   # Bleu Foncé (Naruto/Sakura)

board_map = [
    # --- BAS (De Droite à Gauche) ---
    {"index": 0, "name": "DÉPART", "type": TYPE_SPECIAL, "price": None, "color": None},
    {"index": 1, "name": "Konohamaru", "type": TYPE_PROPERTY, "price": 60, "rent": 2, "color": COLOR_BROWN},
    {"index": 2, "name": "Entraînement", "type": TYPE_COMMUNITY, "price": None, "color": None},
    {"index": 3, "name": "Iruka", "type": TYPE_PROPERTY, "price": 60, "rent": 4, "color": COLOR_BROWN},
    {"index": 4, "name": "Taxe sur le Revenu", "type": TYPE_TAX, "price": None, "amount": 200, "color": None},
    {"index": 5, "name": "Ramen Ichiraku", "type": TYPE_STATION, "price": 200, "rent": 25, "color": "station"},
    {"index": 6, "name": "Kiba", "type": TYPE_PROPERTY, "price": 100, "rent": 6, "color": COLOR_LIGHT_BLUE},
    {"index": 7, "name": "Mission", "type": TYPE_CHANCE, "price": None, "color": None},
    {"index": 8, "name": "Hinata", "type": TYPE_PROPERTY, "price": 100, "rent": 6, "color": COLOR_LIGHT_BLUE},
    {"index": 9, "name": "Shino", "type": TYPE_PROPERTY, "price": 120, "rent": 8, "color": COLOR_LIGHT_BLUE},

    # --- GAUCHE (De Bas en Haut) ---
    {"index": 10, "name": "Prison / Visite", "type": TYPE_SPECIAL, "price": None, "color": None},
    {"index": 11, "name": "Ino", "type": TYPE_PROPERTY, "price": 140, "rent": 10, "color": COLOR_PINK},
    {"index": 12, "name": "Compagnie Élec.", "type": TYPE_UTILITY, "price": 150, "color": "utility"},
    {"index": 13, "name": "Choji", "type": TYPE_PROPERTY, "price": 140, "rent": 10, "color": COLOR_PINK},
    {"index": 14, "name": "Shikamaru", "type": TYPE_PROPERTY, "price": 160, "rent": 12, "color": COLOR_PINK},
    {"index": 15, "name": "Barbecue", "type": TYPE_STATION, "price": 200, "rent": 25, "color": "station"},
    {"index": 16, "name": "Kisame", "type": TYPE_PROPERTY, "price": 180, "rent": 14, "color": COLOR_ORANGE},
    {"index": 17, "name": "Entraînement", "type": TYPE_COMMUNITY, "price": None, "color": None},
    {"index": 18, "name": "Rock Lee", "type": TYPE_PROPERTY, "price": 180, "rent": 14, "color": COLOR_ORANGE},
    {"index": 19, "name": "Tenten", "type": TYPE_PROPERTY, "price": 200, "rent": 16, "color": COLOR_ORANGE},

    # --- HAUT (De Gauche à Droite) ---
    {"index": 20, "name": "Parc Gratuit", "type": TYPE_SPECIAL, "price": None, "color": None},
    {"index": 21, "name": "Neji", "type": TYPE_PROPERTY, "price": 220, "rent": 18, "color": COLOR_RED},
    {"index": 22, "name": "Mission", "type": TYPE_CHANCE, "price": None, "color": None},
    {"index": 23, "name": "Kankuro", "type": TYPE_PROPERTY, "price": 220, "rent": 18, "color": COLOR_RED},
    {"index": 24, "name": "Temari", "type": TYPE_PROPERTY, "price": 240, "rent": 20, "color": COLOR_RED},
    {"index": 25, "name": "Pain (Akatsuki)", "type": TYPE_STATION, "price": 200, "rent": 25, "color": "station"},
    {"index": 26, "name": "Gaara", "type": TYPE_PROPERTY, "price": 260, "rent": 22, "color": COLOR_YELLOW},
    {"index": 27, "name": "Itachi", "type": TYPE_PROPERTY, "price": 260, "rent": 22, "color": COLOR_YELLOW},
    {"index": 28, "name": "Compagnie Eaux", "type": TYPE_UTILITY, "price": 150, "color": "utility"},
    {"index": 29, "name": "Orochimaru", "type": TYPE_PROPERTY, "price": 280, "rent": 24, "color": COLOR_YELLOW},

    # --- DROITE (De Haut en Bas) ---
    {"index": 30, "name": "ALLEZ EN PRISON", "type": TYPE_SPECIAL, "price": None, "color": None},
    {"index": 31, "name": "Tsunade", "type": TYPE_PROPERTY, "price": 300, "rent": 26, "color": COLOR_GREEN},
    {"index": 32, "name": "Jiraiya", "type": TYPE_PROPERTY, "price": 300, "rent": 26, "color": COLOR_GREEN},
    {"index": 33, "name": "Entraînement", "type": TYPE_COMMUNITY, "price": None, "color": None},
    {"index": 34, "name": "Kakashi", "type": TYPE_PROPERTY, "price": 320, "rent": 28, "color": COLOR_GREEN},
    {"index": 35, "name": "Sai", "type": TYPE_STATION, "price": 200, "rent": 25, "color": "station"},
    {"index": 36, "name": "Mission", "type": TYPE_CHANCE, "price": None, "color": None},
    {"index": 37, "name": "Sakura", "type": TYPE_PROPERTY, "price": 350, "rent": 35, "color": COLOR_DARK_BLUE},
    {"index": 38, "name": "Taxe de Luxe", "type": TYPE_TAX, "price": None, "amount": 100, "color": None},
    {"index": 39, "name": "Naruto", "type": TYPE_PROPERTY, "price": 400, "rent": 50, "color": COLOR_DARK_BLUE},
]

def get_square_data(index):
    """Récupère les données d'une case via son index (0-39)"""
    for square in board_map:
        if square['index'] == index:
            return square
    return None