import random
import time
from game.board_data import get_square_data, TYPE_PROPERTY, TYPE_STATION, TYPE_UTILITY, TYPE_TAX


class MonopolyEngine:
    def __init__(self):
        self.players = [
            {'id': 1, 'name': 'Joueur 1', 'color': '#3498db', 'position': 0, 'money': 1500},
            {'id': 2, 'name': 'Joueur 2', 'color': '#e74c3c', 'position': 0, 'money': 1500}
        ]
        self.current_player_index = 0
        self.game_log = ["En attente du démarrage..."]
        self.last_dice_roll = None
        self.state = "NOT_STARTED"
        self.ownership = {}

        # Effets visuels
        self.visual_effects = []
        self.last_flash = {'index': -1, 'time': 0}

    def add_floating_text(self, text, square_index, color_bgr):
        """Ajoute un texte flottant à la liste"""
        self.visual_effects.append({
            'text': text,
            'pos': square_index,
            'color': color_bgr,
            'start_time': time.time()
        })

    def get_current_player(self):
        return self.players[self.current_player_index]

    def start_game(self):
        self.state = "WAITING_ROLL"
        self.game_log.insert(0, "🏁 LA PARTIE COMMENCE !")
        return True

    def roll_dice(self, manual_value=None):
        if self.state != "WAITING_ROLL":
            return None

        # 1. Valeur des dés
        if manual_value is not None:
            total = manual_value
        else:
            total = random.randint(1, 6) + random.randint(1, 6)

        self.last_dice_roll = total
        player = self.get_current_player()

        # 2. Déplacement
        old_pos = player['position']
        new_pos = (old_pos + total) % 40
        player['position'] = new_pos

        # Salaire Départ
        if new_pos < old_pos:
            player['money'] += 200
            self.game_log.insert(0, f"💰 {player['name']} passe par DÉPART (+200$).")
            self.add_floating_text("+200 $", 0, (0, 255, 0))

        # 3. Logique de la case
        square = get_square_data(new_pos)
        s_name = square['name']
        s_type = square['type']

        log_msg = f"{player['name']} fait {total} -> {s_name}."
        owner_id = self.ownership.get(new_pos)

        # GESTION PRISON (Case 30)
        if new_pos == 30:
            self.game_log.insert(0, f"👮 POLICE ! {player['name']} va en Prison !")
            self.state = "MOVED"
            return total  # Le controller gérera l'anim

        # GESTION PROPRIETES
        if s_type in [TYPE_PROPERTY, TYPE_STATION, TYPE_UTILITY]:
            if owner_id is None:
                # C'EST ICI QUE LE BOUTON ACHETER EST ACTIVÉ
                price = square['price']
                if player['money'] >= price:
                    log_msg += f" (A VENDRE: {price}$)"
                    self.state = "CAN_BUY"  # <--- IMPORTANT
                else:
                    log_msg += " (Trop cher)"
                    self.state = "MOVED"
            elif owner_id == player['id']:
                log_msg += " (Chez vous)."
                self.state = "MOVED"
            else:
                rent = square.get('rent', 0)
                self.pay_rent(player, owner_id, rent, new_pos)
                log_msg += f" (Loyer: -{rent}$)"
                self.state = "MOVED"

        elif s_type == TYPE_TAX:
            amount = square.get('amount', 0)
            player['money'] -= amount
            self.add_floating_text(f"-{amount} $", new_pos, (0, 0, 255))
            log_msg += f" (Taxe: -{amount}$)"
            self.state = "MOVED"

        else:
            self.state = "MOVED"

        self.game_log.insert(0, log_msg)
        return total

    def pay_rent(self, current_player, owner_id, amount, pos):
        current_player['money'] -= amount
        self.add_floating_text(f"-{amount} $", pos, (0, 0, 255))
        for p in self.players:
            if p['id'] == owner_id:
                p['money'] += amount
                break

    def buy_current_property(self):
        if self.state != "CAN_BUY": return False, "Impossible"

        player = self.get_current_player()
        pos = player['position']
        square = get_square_data(pos)
        price = square['price']

        if player['money'] >= price:
            player['money'] -= price
            self.ownership[pos] = player['id']
            self.state = "MOVED"

            # Effets : Texte Jaune + Flash
            self.add_floating_text(f"-{price} $", pos, (0, 255, 255))
            self.last_flash = {'index': pos, 'time': time.time()}

            msg = f"💸 {player['name']} achète {square['name']} !"
            self.game_log.insert(0, msg)
            return True, msg

        return False, "Pas assez d'argent"

    def send_to_jail(self):
        player = self.get_current_player()
        player['position'] = 10
        self.add_floating_text("POOF!", 30, (100, 100, 100))

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.state = "WAITING_ROLL"
        next_player = self.get_current_player()
        self.game_log.insert(0, f"--- Tour de {next_player['name']} ---")

    def get_state(self):
        current_player = self.get_current_player()
        current_square = get_square_data(current_player['position'])
        return {
            'players': self.players,
            'current_player': current_player,
            'logs': self.game_log[:6],
            'last_roll': self.last_dice_roll,
            'game_state': self.state,
            'current_square': current_square,
            'ownership': self.ownership
        }


game_instance = MonopolyEngine()