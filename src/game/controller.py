import cv2
from camera.camera import Camera
from game.engine import game_instance
from game.visualizer import draw_game_state

# Instanciation unique de la caméra
camera = Camera()


def get_video_stream_generator():
    """
    Boucle principale qui gère la Vision, le Jeu et l'Affichage.
    """
    while True:
        # 1. ACQUISITION & TRAITEMENT D'IMAGE
        # La caméra nous donne l'image traitée et les coordonnées des cases
        frame, squares = camera.process_frame()

        # 2. LOGIQUE DE JEU (DÉTECTION DÉS -> ACTION)
        # Si la caméra a stabilisé une valeur de dé...
        if camera.validated_dice_value is not None:
            # ... et que le jeu attend un lancer
            if game_instance.state == "WAITING_ROLL":
                print(f"🎲 ACTION CAMÉRA : Lancer validé de {camera.validated_dice_value}")
                # On déclenche le mouvement dans le moteur
                game_instance.roll_dice(manual_value=camera.validated_dice_value)

        # 3. RÉALITÉ AUGMENTÉE (DESSIN)
        if camera.is_board_detected and squares is not None:
            # Récupération des données du jeu
            current_players = game_instance.players
            current_ownership = game_instance.ownership  # <--- NOUVEAU : On récupère les achats

            # On dessine tout (Pions + Propriétés colorées)
            # Note : on passe maintenant 4 arguments
            frame = draw_game_state(frame, current_players, squares, current_ownership)


        # 4. ENCODAGE POUR LE WEB
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret: continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def get_camera_status():
    """Retourne l'état de la caméra pour l'API /status"""
    return camera.is_board_detected