import random


class MonopolyEngine:
    def __init__(self):
        self.players = [
            {'id': 1, 'name': 'Joueur 1', 'color': '#3498db', 'position': 0, 'money': 1500},
            {'id': 2, 'name': 'Joueur 2', 'color': '#e74c3c', 'position': 0, 'money': 1500}
        ]
        self.current_player_index = 0  # 0 pour Joueur 1, 1 pour Joueur 2
        self.game_log = ["Bienvenue ! La partie commence."]
        self.last_dice_roll = None
        self.state = "WAITING_ROLL"  # États: WAITING_ROLL, MOVED

    def get_current_player(self):
        return self.players[self.current_player_index]

    def roll_dice(self):
        if self.state != "WAITING_ROLL":
            return None

        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        total = die1 + die2
        self.last_dice_roll = total

        player = self.get_current_player()
        old_pos = player['position']
        new_pos = (old_pos + total) % 40  # 40 cases sur le plateau
        player['position'] = new_pos

        self.game_log.insert(0, f"{player['name']} a fait {total} ({die1}+{die2}) et va case {new_pos}.")
        self.state = "MOVED"

        # Passage automatique au tour suivant pour cette simulation simple
        # Dans un vrai jeu, on attendrait que l'animation finisse
        self.next_turn()

        return total

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.state = "WAITING_ROLL"
        next_player = self.get_current_player()
        self.game_log.insert(0, f"C'est au tour de {next_player['name']}.")

    def get_state(self):
        return {
            'players': self.players,
            'current_player': self.get_current_player(),
            'logs': self.game_log[:5],  # Les 5 derniers messages
            'last_roll': self.last_dice_roll
        }


# Instance globale du jeu
game_instance = MonopolyEngine()