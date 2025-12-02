import cv2
import time
import copy
from camera.camera import Camera
from game.engine import game_instance
from game.visualizer import draw_game_state

camera = Camera()


def get_video_stream_generator():
    while True:
        frame, squares = camera.process_frame()

        if camera.validated_dice_value is not None:
            if game_instance.state == "WAITING_ROLL":
                dice_val = camera.validated_dice_value
                print(f"🎲 Lancer: {dice_val}")

                current_player = game_instance.get_current_player()
                start_pos = current_player['position']
                game_instance.roll_dice(manual_value=dice_val)

                # ANIMATION DEPLACEMENT
                steps_to_animate = dice_val
                for i in range(1, steps_to_animate + 1):
                    anim_pos = (start_pos + i) % 40
                    temp_players = copy.deepcopy(game_instance.players)
                    temp_players[game_instance.current_player_index]['position'] = anim_pos

                    # 5 frames par pas
                    for _ in range(5):
                        frame_anim, squares_anim = camera.process_frame()
                        if camera.is_board_detected and squares_anim is not None:
                            curr_own = game_instance.ownership
                            curr_id = current_player['id']
                            curr_fx = game_instance.visual_effects
                            curr_flash = game_instance.last_flash

                            frame_anim = draw_game_state(frame_anim, temp_players, squares_anim, curr_own, curr_id,
                                                         curr_fx, curr_flash)

                        ret, buffer = cv2.imencode('.jpg', frame_anim)
                        if ret: yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                        time.sleep(0.02)

                # ANIMATION FUMÉE (PRISON)
                final_pos = game_instance.get_current_player()['position']
                if final_pos == 30:  # Allez en prison
                    print("🥷 FUMÉE NINJA !")
                    for k in range(15):
                        frame_anim, squares_anim = camera.process_frame()
                        if camera.is_board_detected and squares_anim is not None:
                            # On redessine tout normalement
                            frame_anim = draw_game_state(frame_anim, game_instance.players, squares_anim,
                                                         game_instance.ownership, current_player['id'],
                                                         game_instance.visual_effects, game_instance.last_flash)

                            if 30 in squares_anim:
                                (x, y, w, h) = squares_anim[30]
                                cx, cy = x + w // 2, y + h // 2
                                cv2.circle(frame_anim, (cx, cy), 10 + (k * 4), (100, 100, 100), -1)
                                cv2.putText(frame_anim, "POOF!", (cx - 30, cy), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                            (255, 255, 255), 2)

                        ret, buffer = cv2.imencode('.jpg', frame_anim)
                        if ret: yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                        time.sleep(0.05)

                    game_instance.send_to_jail()

        # DESSIN STANDARD
        if camera.is_board_detected and squares is not None:
            curr_play = game_instance.players
            curr_own = game_instance.ownership
            curr_id = game_instance.get_current_player()['id']
            curr_fx = game_instance.visual_effects
            curr_flash = game_instance.last_flash

            frame = draw_game_state(frame, curr_play, squares, curr_own, curr_id, curr_fx, curr_flash)


        # Nettoyage vieux effets
        current_time = time.time()
        game_instance.visual_effects = [e for e in game_instance.visual_effects if current_time - e['start_time'] < 2.0]

        if frame is None: continue
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret: continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def get_camera_status():
    return camera.is_board_detected