import cv2


def hex_to_bgr(hex_color):
    """Convertit '#3498db' (Web) en (219, 152, 52) (OpenCV BGR)"""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return (rgb[2], rgb[1], rgb[0])


def draw_game_state(warped_img, players, squares, ownership):
    """
    Dessine les pions ET les propriétés achetées.
    """
    if squares is None:
        return warped_img

    # 1. DESSINER LES PROPRIÉTÉS (Background)
    # On parcourt toutes les cases achetées
    for square_idx, owner_id in ownership.items():
        if square_idx in squares:
            (x, y, w, h) = squares[square_idx]

            # Trouver la couleur du proprio
            owner_color = (100, 100, 100)  # Gris par défaut
            for p in players:
                if p['id'] == owner_id:
                    owner_color = hex_to_bgr(p['color'])
                    break

            # Dessiner un cadre épais intérieur
            # On dessine un rectangle translucide (overlay) c'est plus joli
            overlay = warped_img.copy()
            cv2.rectangle(overlay, (x, y), (x + w, y + h), owner_color, -1)  # Remplissage

            # Transparence (alpha) : 0.3 (30% de couleur, 70% d'image originale)
            cv2.addWeighted(overlay, 0.3, warped_img, 0.7, 0, warped_img)

            # Et une bordure solide pour bien marquer
            cv2.rectangle(warped_img, (x, y), (x + w, y + h), owner_color, 3)

    # 2. DESSINER LES PIONS (Foreground)
    players_on_square = {}

    for player in players:
        pos = player['position']
        color_hex = player['color']
        color_bgr = hex_to_bgr(color_hex)

        if pos in squares:
            (x, y, w, h) = squares[pos]

            center_x = x + w // 2
            center_y = y + h // 2

            # Gestion collision (plusieurs joueurs même case)
            count = players_on_square.get(pos, 0)
            offset_x = (count * 25) - 10
            players_on_square[pos] = count + 1

            # Cercle du joueur
            cv2.circle(warped_img, (center_x + offset_x, center_y), 18, color_bgr, -1)
            cv2.circle(warped_img, (center_x + offset_x, center_y), 20, (255, 255, 255), 2)

    return warped_img