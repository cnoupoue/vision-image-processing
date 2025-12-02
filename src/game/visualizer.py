import cv2
import math
import time


def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return (rgb[2], rgb[1], rgb[0])


def draw_game_state(warped_img, players, squares, ownership, current_player_id, effects, flash_info):
    """
    Dessine Pions, Propriétés, Effets et Flash.
    """
    if squares is None:
        return warped_img

    # 1. DESSINER LES PROPRIÉTÉS
    for square_idx, owner_id in ownership.items():
        if square_idx in squares:
            (x, y, w, h) = squares[square_idx]
            owner_color = (100, 100, 100)
            for p in players:
                if p['id'] == owner_id:
                    owner_color = hex_to_bgr(p['color'])
                    break

            overlay = warped_img.copy()
            cv2.rectangle(overlay, (x, y), (x + w, y + h), owner_color, -1)
            cv2.addWeighted(overlay, 0.3, warped_img, 0.7, 0, warped_img)
            cv2.rectangle(warped_img, (x, y), (x + w, y + h), owner_color, 3)

    # 2. DESSINER LE FLASH (SI ACTIF)
    if flash_info and (time.time() - flash_info['time'] < 0.5):
        idx = flash_info['index']
        if idx in squares:
            (x, y, w, h) = squares[idx]
            # Carré blanc pur
            cv2.rectangle(warped_img, (x, y), (x + w, y + h), (255, 255, 255), -1)

    # 3. DESSINER LES PIONS (Indentation corrigée : alignée à gauche)
    players_on_square = {}
    for player in players:
        pos = player['position']
        color_hex = player['color']
        color_bgr = hex_to_bgr(color_hex)

        if pos in squares:
            (x, y, w, h) = squares[pos]
            center_x = x + w // 2
            center_y = y + h // 2

            count = players_on_square.get(pos, 0)
            offset_x = (count * 25) - 10
            players_on_square[pos] = count + 1

            # Animation Pulse
            base_radius = 18
            radius = base_radius
            if player['id'] == current_player_id:
                pulse = math.sin(time.time() * 8)
                radius = int(base_radius + (pulse * 4))
                cv2.circle(warped_img, (center_x + offset_x, center_y), radius + 5, (255, 255, 255), 2)

            cv2.circle(warped_img, (center_x + offset_x, center_y), radius, color_bgr, -1)
            cv2.circle(warped_img, (center_x + offset_x, center_y), radius + 2, (0, 0, 0), 2)

    # 4. DESSINER LES TEXTES FLOTTANTS
    for effect in effects:
        pos = effect['pos']
        text = effect['text']
        color = effect['color']
        start_t = effect['start_time']

        if pos in squares:
            (x, y, w, h) = squares[pos]
            center_x = x + w // 2
            center_y = y + h // 2

            elapsed = time.time() - start_t
            move_up = int(elapsed * 50)

            # Ombre noire + Texte couleur
            cv2.putText(warped_img, text, (center_x - 20, center_y - move_up),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4)
            cv2.putText(warped_img, text, (center_x - 20, center_y - move_up),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

    return warped_img