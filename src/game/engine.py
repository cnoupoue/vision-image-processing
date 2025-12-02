import random
from game.board_data import get_square_data, TYPE_PROPERTY, TYPE_STATION, TYPE_UTILITY, TYPE_TAX


class MonopolyEngine:
    def __init__(self):
        self.players = [
            {'id': 1, 'name': 'Joueur 1', 'color': '#3498db', 'position': 0, 'money': 1500},
            {'id': 2, 'name': 'Joueur 2', 'color': '#e74c3c', 'position': 0, 'money': 1500}
        ]
        self.current_player_index = 0
        self.game_log = ["Bienvenue dans Naruto Monopoly !"]
        self.last_dice_roll = None
        self.state = "WAITING_ROLL"  # États: WAITING_ROLL, MOVED, CAN_BUY

        # Qui possède quoi ? { index_case: id_joueur }
        # Ex: { 39: 1 } veut dire que Naruto appartient au Joueur 1
        self.ownership = {}

    def get_current_player(self):
        return self.players[self.current_player_index]

    def roll_dice(self, manual_value=None):
        if self.state != "WAITING_ROLL":
            return None

        # 1. Gestion des dés
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

        # Règle : Passage par la case départ (si on boucle)
        if new_pos < old_pos:
            player['money'] += 200
            self.game_log.insert(0, f"💰 {player['name']} passe par DÉPART (+200$).")

        # 3. Analyse de la case
        square = get_square_data(new_pos)
        s_name = square['name']
        s_type = square['type']

        log_msg = f"{player['name']} a fait {total} et atterrit sur {s_name}."

        # --- LOGIQUE D'INTERACTION ---
        owner_id = self.ownership.get(new_pos)

        # CAS A : Case achetable (Propriété, Gare, Compagnie)
        if s_type in [TYPE_PROPERTY, TYPE_STATION, TYPE_UTILITY]:
            if owner_id is None:
                # Personne ne l'a -> On peut acheter !
                price = square['price']
                if player['money'] >= price:
                    log_msg += f" (A VENDRE: {price}$)"
                    self.state = "CAN_BUY"  # Nouvel état spécial !
                else:
                    log_msg += " (Trop cher pour vous)"
                    self.state = "MOVED"
            elif owner_id == player['id']:
                log_msg += " (Vous êtes chez vous)."
                self.state = "MOVED"
            else:
                # Appartient à un autre -> PAYER LOYER !
                rent = square.get('rent', 0)
                # (On fera le calcul complexe des loyers plus tard)
                self.pay_rent(player, owner_id, rent)
                log_msg += f" (Chez Joueur {owner_id}. Loyer payé: -{rent}$)"
                self.state = "MOVED"

        # CAS B : Taxes
        elif s_type == TYPE_TAX:
            amount = square.get('amount', 0)
            player['money'] -= amount
            log_msg += f" (Taxe payée: -{amount}$)"
            self.state = "MOVED"

        else:
            # Autres cases (Chance, Prison...)
            self.state = "MOVED"

        self.game_log.insert(0, log_msg)
        return total

    def pay_rent(self, current_player, owner_id, amount):
        """Transfert l'argent d'un joueur à un autre"""
        # 1. Retirer au payeur
        current_player['money'] -= amount

        # 2. Donner au receveur
        for p in self.players:
            if p['id'] == owner_id:
                p['money'] += amount
                break

    def buy_current_property(self):
        """Appelé quand le joueur clique sur 'ACHETER'"""
        if self.state != "CAN_BUY":
            return False, "Action impossible"

        player = self.get_current_player()
        pos = player['position']
        square = get_square_data(pos)
        price = square['price']

        if player['money'] >= price:
            player['money'] -= price
            self.ownership[pos] = player['id']
            self.state = "MOVED"  # Achat fait, on repasse en mode normal
            msg = f"💸 {player['name']} a acheté {square['name']} pour {price}$ !"
            self.game_log.insert(0, msg)
            return True, msg

        return False, "Pas assez d'argent"

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.state = "WAITING_ROLL"
        next_player = self.get_current_player()
        self.game_log.insert(0, f"--- Tour de {next_player['name']} ---")

    def get_state(self):
        # On ajoute l'info de la case actuelle pour le Front-End
        current_player = self.get_current_player()
        current_square = get_square_data(current_player['position'])

        return {
            'players': self.players,
            'current_player': current_player,
            'logs': self.game_log[:6],
            'last_roll': self.last_dice_roll,
            'game_state': self.state,  # WAITING_ROLL, MOVED, CAN_BUY
            'current_square': current_square,
            'ownership': self.ownership
        }


# Instance globale
game_instance = MonopolyEngine()