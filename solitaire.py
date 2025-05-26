class Karta:
    def __init__(self, typ, rank, face_up, color):
        self.typ = typ
        self.rank = rank
        self.face_up = face_up
        self.color = color

    def __str__(self):
        rank_map = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}
        rank_str = rank_map.get(self.rank, str(self.rank))
        return f"{self.typ}{rank_str}" if self.face_up else "XX"


class Deck:
    def __init__(self):
        self.cards = []
        self.types = ['♥', '♦', '♣', '♠']
        self.ranks = list(range(1, 14))
        self.create_deck()

    def create_deck(self):
        for typ in self.types:
            for rank in self.ranks:
                if typ == '♥' or typ == '♦':
                    self.cards.append(Karta(typ, rank, False, '\033[91m'))
                else:
                    self.cards.append(Karta(typ, rank, False, '\033[0m'))

    def shuffle(self):
        from random import shuffle
        shuffle(self.cards)

    def draw_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        return None


class Pile:
    def __init__(self):
        self.cards = []
        self.tableau_pile = False  # Domyślnie False

    def add_card(self, card):
        self.cards.append(card)

    def remove_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        return None


class Tableau:
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.tableau_piles = [Pile() for _ in range(7)]
        self.foundation_piles = [Pile() for _ in range(4)]
        self.stock = Pile()
        self.waste = Pile()
        self.setup_tableau()

    def setup_tableau(self):
        for i in range(7):
            for j in range(i, 7):
                card = self.deck.draw_card()
                if card:
                    if i == j:
                        card.face_up = True
                    self.tableau_piles[j].add_card(card)

        while self.deck.cards:
            self.stock.add_card(self.deck.draw_card())

    def show_foundations(self):
        foundations = []
        for pile in self.foundation_piles:
            if not pile.cards:
                foundations.append("[   ]")
            else:
                card = pile.cards[-1]
                color_code = '\033[91m' if card.typ in ['♥', '♦'] else '\033[0m'
                foundations.append(f"{color_code}[{card}]\033[0m")
        return " ".join(foundations)

    def show_stock_waste(self):
        if not self.stock.cards:
            stock = "[   ]"
        else:
            stock = f"[{len(self.stock.cards):2d} ]"

        if not self.waste.cards:
            waste = "[   ]"
        else:
            card = self.waste.cards[-1]
            color_code = '\033[91m' if card.typ in ['♥', '♦'] else '\033[0m'
            waste = f"{color_code}[{card}]\033[0m"

        return f"Stos: {stock}    Odrzucone: {waste}"

    def show_tableau_piles(self):
        max_height = max(len(pile.cards) for pile in self.tableau_piles)
        result = []
        for row in range(max_height):
            line = []
            for pile in self.tableau_piles:
                if row < len(pile.cards):
                    card = pile.cards[row]
                    if not card.face_up:
                        line.append(" XX")
                    else:
                        rank_map = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}
                        rank_str = rank_map.get(card.rank, str(card.rank))
                        color_code = '\033[91m' if card.typ in ['♥', '♦'] else '\033[0m'
                        if rank_str == '10':
                            line.append(f" \b{color_code}{card.typ}{rank_str} \033[0m")
                        else:
                            line.append(f" {color_code}{card.typ}{rank_str} \033[0m")
                else:
                    line.append("  ")
            result.append(" ".join(f"{card:4}" for card in line))
        return "\n".join(result)

    def move_card(self, from_pile, to_pile, from_index=None):
        if from_index is None:
            from_index = len(from_pile.cards) - 1
        card = from_pile.cards[from_index]
        to_pile.cards.append(card)
        del from_pile.cards[from_index]

        if from_pile.cards and hasattr(from_pile, 'tableau_pile'):  # Sprawdzamy czy to stos z planszy
            if from_index > 0:
                from_pile.cards[from_index - 1].face_up = True
            elif len(from_pile.cards) > 0:
                from_pile.cards[-1].face_up = True

    def is_valid_move(self, cards, to_pile):
        if not to_pile.cards:
            return cards[0].rank == 13
        top_card = to_pile.cards[-1]
        first_moving_card = cards[0]
        return (first_moving_card.rank == top_card.rank - 1 and
                ((first_moving_card.typ in ['♥', '♦'] and top_card.typ in ['♣', '♠']) or
                 (first_moving_card.typ in ['♣', '♠'] and top_card.typ in ['♥', '♦'])))

    def is_valid_foundation(self, card, foundation_pile):
        if not foundation_pile.cards:
            return card.rank == 1
        top_card = foundation_pile.cards[-1]
        return card.typ == top_card.typ and card.rank == top_card.rank + 1

    def is_valid_sequence(self, cards):
        # Sprawdzamy czy wszystkie karty są odkryte
        if not all(card.face_up for card in cards):
            return False

        for i in range(len(cards) - 1):
            current_card = cards[i]
            next_card = cards[i + 1]
            # Sprawdza czy każda kolejna karta ma przeciwny kolor i wartość o 1 mniejszą
            if not (current_card.rank == next_card.rank + 1 and
                    ((current_card.typ in ['♥', '♦'] and next_card.typ in ['♣', '♠']) or
                     (current_card.typ in ['♣', '♠'] and next_card.typ in ['♥', '♦']))):
                return False
        return True

    def move_cards(self, from_pile, to_pile, from_index):
        # Sprawdź czy indeks jest prawidłowy
        if from_index < 0 or from_index >= len(from_pile.cards):
            return False

        cards_to_move = from_pile.cards[from_index:]

        # Jeśli stos docelowy jest pusty, tylko król może być pierwszą kartą
        if not to_pile.cards:
            if cards_to_move[0].rank != 13:
                return False
        else:
            # Sprawdź czy pierwsza przenoszona karta pasuje do ostatniej na stosie docelowym
            top_card = to_pile.cards[-1]
            first_moving_card = cards_to_move[0]
            if not (first_moving_card.rank == top_card.rank - 1 and
                    ((first_moving_card.typ in ['♥', '♦'] and top_card.typ in ['♣', '♠']) or
                     (first_moving_card.typ in ['♣', '♠'] and top_card.typ in ['♥', '♦']))):
                return False

        # Sprawdź czy karty tworzą prawidłową sekwencję
        if not self.is_valid_sequence(cards_to_move):
            return False

        # Wykonaj ruch
        to_pile.cards.extend(cards_to_move)
        del from_pile.cards[from_index:]

        # Odkryj kartę pod spodem jeśli istnieje
        if from_pile.cards and hasattr(from_pile, 'tableau_pile'):
            from_pile.cards[-1].face_up = True

        return True

    def process_move(self, command):
        try:
            parts = command.split()
            if len(parts) < 2:
                return False

            source, dest = parts[0], parts[1]
            card_count = 1
            if len(parts) == 3:
                try:
                    card_count = int(parts[2])
                except ValueError:
                    return False

            # Obsługa przenoszenia na fundamenty (tylko pojedyncze karty)
            if dest.lower() == 'f':
                source_pile = int(source) - 1
                if 0 <= source_pile <= 7 and self.tableau_piles[source_pile].cards:
                    card = self.tableau_piles[source_pile].cards[-1]
                    if not card.face_up:
                        return False
                    for foundation in self.foundation_piles:
                        if self.is_valid_foundation(card, foundation):
                            self.move_card(self.tableau_piles[source_pile], foundation)
                            return True
                return False

            # Obsługa przenoszenia ze stosu odrzutów (tylko pojedyncze karty)
            elif source.lower() == 's':
                dest_pile = int(dest) - 1
                if 0 <= dest_pile <= 6 and self.waste.cards:
                    card = self.waste.cards[-1]
                    if self.is_valid_move([card], self.tableau_piles[dest_pile]):
                        self.move_card(self.waste, self.tableau_piles[dest_pile])
                        return True
            # Przenoszenie między stosami tableau
            else:
                source_pile = int(source) - 1
                dest_pile = int(dest) - 1

                if (0 <= source_pile <= 6 and
                        0 <= dest_pile <= 6 and
                        source_pile != dest_pile and
                        len(self.tableau_piles[source_pile].cards) >= card_count):

                    from_index = len(self.tableau_piles[source_pile].cards) - card_count
                    # Sprawdź czy wszystkie przenoszone karty są odkryte
                    if not all(card.face_up for card in self.tableau_piles[source_pile].cards[from_index:]):
                        print("Nie można przenosić zakrytych kart!")
                        return False

                    return self.move_cards(
                        self.tableau_piles[source_pile],
                        self.tableau_piles[dest_pile],
                        from_index
                    )
            return False
        except Exception as e:
            print(f"Błąd: {e}")
            return False

    def display(self):
        print("\nPodstawy:", self.show_foundations())
        print("\n" + self.show_stock_waste())
        print("\nPlansza:")
        print("\033[92m 1    2    3    4    5    6    7\033[0m")
        print(self.show_tableau_piles())
        print()

    def check_win(self):
        for foundation in self.foundation_piles:
            if len(foundation.cards) != 13:  # Każdy stos fundamentów powinien mieć 13 kart
                return False
        return True


print("Console Pasjans v0.1")
print(
    "Format ruchu: <źródło> <cel> (<którą kartę od dołu przenieść, przenosi to stos kart>) \n(np. '1 2' przenosi kartę ze stosu 1 na stos 2 albo 's 3' przenosi kartę na stosie dobierania na stos 3)\n lub n aby dobrać kartę ze stosu dobierania, b to odwrotność komendy n. przenoszenie na f przenosi kartę na odpowiednią podstawę")
input("kliknij enter aby kontynuować")
game = Tableau()
while True:
    print("\033[H\033[J", end="")
    game.display()
    print(
        "\nOdrzucone: s | Podstawy: f | Stosy: 1-7 \nPrzenoszenie stosów kart: <stos źródłowy> <stos docelowy> <którą kartę od dołu podnieść>")
    move = input("Podaj ruch (lub 'q' aby wyjść): ").lower()
    try:
        if move == 'q':
            break
        if move == 'n' or move == 'n ':
            if game.stock.cards:
                game.move_card(game.stock, game.waste)
                game.waste.cards[-1].face_up = True
            else:
                print("Stos dobierania pusty!")
            continue
        if move == "b" or move == "b ":
            if game.waste.cards:
                temp_cards = []
                while game.waste.cards:
                    temp_cards.append(game.waste.cards.pop())
                for card in temp_cards:
                    game.stock.cards.append(card)
                    card.face_up = False
            else:
                print("Stos kart odrzuconych pusty!")
            continue
        parts = move.split()
        if len(parts) < 2 and len(parts) != 3:
            print("Nieprawidłowy format ruchu!")
            continue

        if move.split()[0].isdigit():
            source = int(move.split()[0])
        if len(move.split()) > 1 and move.split()[1].isdigit():
            dest = int(move.split()[1])
        else:
            source, dest = parts

        if dest == 'f':
            moved = False
            if source == 's' and game.waste.cards:
                card = game.waste.cards[-1]
                for foundation in game.foundation_piles:
                    if game.is_valid_foundation(card, foundation):
                        game.move_card(game.waste, foundation)
                        moved = True
                        break
            elif source.isdigit() and 0 <= int(source) <= 6:
                source_idx = int(source) - 1
                if game.tableau_piles[source_idx].cards:
                    card = game.tableau_piles[source_idx].cards[-1]
                    for foundation in game.foundation_piles:
                        if game.is_valid_foundation(card, foundation):
                            game.move_card(game.tableau_piles[source_idx], foundation)
                            moved = True
                            break

            if not moved:
                print("Nie można przenieść tej karty na podstawy!")
            continue

        if not game.process_move(move):
            print("Nieprawidłowy ruch!")

    except Exception as e:
        print(e)
    if game.check_win():
        print("\033[H\033[J", end="")
        game.display()
        print("\n🎉 Gratulacje! Wygrałeś grę! 🎉")
        break
