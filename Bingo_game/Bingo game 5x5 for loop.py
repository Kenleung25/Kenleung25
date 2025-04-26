import random
from collections import defaultdict


class BingoGame:
    def __init__(self, players=1):
        self.max_players = min(5, max(1, players))
        self.players_cards = [self.generate_card()
                              for _ in range(self.max_players)]
        self.called_numbers = []
        self.winners = defaultdict(list)
        self.game_over = False
        self.mc_calls = 0
        self.max_calls = 40

    def generate_card(self):
        card = []
        # Generate all 24 unique numbers first (1-100)
        all_numbers = random.sample(range(1, 101), 24)
        number_iter = iter(all_numbers)

        # Build 5x5 grid
        for i in range(5):
            row = []
            for j in range(5):
                if i == 2 and j == 2:  # Center position
                    row.append("★")
                else:
                    row.append(next(number_iter))
            card.append(row)
        return card

    def call_number(self):
        if self.mc_calls >= self.max_calls or len(self.called_numbers) == 100:
            self.game_over = True
            return None
            
        # First 10 calls follow sequential ranges
        if self.mc_calls < 10:
            range_start = self.mc_calls * 10 + 1
            range_end = (self.mc_calls + 1) * 10
            available = [n for n in range(range_start, range_end + 1) 
                        if n not in self.called_numbers]
        
        # Calls 11-15: Prime numbers only
        elif 10 <= self.mc_calls < 15:
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 
                     41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
            available = [n for n in primes 
                        if n not in self.called_numbers and 1 <= n <= 100]
        
        # Calls 16-20: Composite numbers only
        elif 15 <= self.mc_calls < 20:
            composites = [n for n in range(1, 101) 
                         if n not in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 
                                     31, 37, 41, 43, 47, 53, 59, 61, 67, 
                                     71, 73, 79, 83, 89, 97] and n != 1]
            available = [n for n in composites 
                        if n not in self.called_numbers]
        
        # After first 20 calls, switch to random from all numbers
        else:
            available = [n for n in range(1, 101) if n not in self.called_numbers]
            
        if not available:
            # Fallback to any available number if no numbers left in category
            available = [n for n in range(1, 101) if n not in self.called_numbers]
            if not available:
                self.game_over = True
                return None
            
        number = random.choice(available)
        self.called_numbers.append(number)
        self.mc_calls += 1
        
        # Print the current range being called
        if self.mc_calls <= 10:
            range_start = (self.mc_calls - 1) * 10 + 1
            range_end = self.mc_calls * 10
            print(f"MC is calling from range {range_start}-{range_end}")
        elif 10 <= self.mc_calls < 15:
            print("MC is calling from prime numbers")
        elif 15 <= self.mc_calls < 20:
            print("MC is calling from composite numbers")
        else:
            print("MC is calling from random remaining numbers")
            
        return number

    def check_card(self, player_idx):
        if player_idx in self.winners:
            return 0

        card = self.players_cards[player_idx]
        marked = [[num in self.called_numbers or num == "★" for num in row]
                  for row in card]
        lines_won = 0

        # Check rows
        for row in marked:
            if all(row):
                lines_won += 1

        # Check columns
        for col in range(5):
            if all(marked[row][col] for row in range(5)):
                lines_won += 1

        # Check diagonals
        if all(marked[i][i] for i in range(5)):
            lines_won += 1
        if all(marked[i][4-i] for i in range(5)):
            lines_won += 1

        if lines_won > 0:
            self.winners[player_idx] = lines_won

        return lines_won

    def display_card(self, player_idx):
        card = self.players_cards[player_idx]
        called = self.called_numbers
        print(f"\nPlayer {player_idx+1}'s card (Marked with ◉):")
        print("+" + "-----+" * 5)
        for row in card:
            print("|", end="")
            for num in row:
                if num == "★":
                    print("  ★  |", end="")
                elif num in called:
                    print(f" ◉{num:2} |", end="")
                else:
                    print(f" {num:3} |", end="")
            print("\n+" + "-----+" * 5)

    def play_round(self):
        called = self.call_number()
        if called is None:
            self.game_over = True
            return None

        print(f"\n{'='*40}")
        print(f"MC calls number: {called} (Call #{self.mc_calls}/{self.max_calls})")
        print(f"Called numbers: {sorted(self.called_numbers)}")

        # Show all players' cards
        for i in range(self.max_players):
            self.display_card(i)
            lines = self.check_card(i)
            if lines > 0:
                print(f"  → Player {i+1} completed {lines} line(s)!")

        if self.mc_calls >= self.max_calls:
            self.game_over = True

        return called

    def get_rankings(self):
        ranked = sorted(self.winners.items(), key=lambda x: (-x[1], x[0]))
        return [(player+1, lines) for player, lines in ranked]


def play_game():
    print("""
    *************************************
    *           BINGO GAME             *
    *        Center has a star ★       *
    *      Numbers range: 1-100        *
    *  First 10 calls: 1-10, 11-20,...*
    *  Then random from remaining      *
    *  Max 40 calls by MC             *
    *  Max 5 players                   *
    *  Real-time card updates         *
    *************************************
    """)

    while True:
        try:
            players = int(input("How many players? (1-5): "))
            if 1 <= players <= 5:
                break
            print("Please enter 1-5 players.")
        except ValueError:
            print("Please enter a number.")

    game = BingoGame(players)

    # Initial cards display
    print("\nInitial Bingo Cards:")
    for i in range(game.max_players):
        game.display_card(i)

    # Game loop
    while not game.game_over:
        input("\nPress Enter for MC to call next number...")
        called = game.play_round()

        if called is None:
            break

    # Game over
    print("\n" + "="*40)
    print("=== GAME OVER ===")
    print(f"Total numbers called: {len(game.called_numbers)}")

    rankings = game.get_rankings()
    if rankings:
        print("\nFinal Rankings:")
        for i, (player, lines) in enumerate(rankings, 1):
            print(f"{i}. Player {player} - {lines} line(s)")
    else:
        print("\nNo winners this game!")

    print("\nThanks for playing!")


if __name__ == "__main__":
    play_game()