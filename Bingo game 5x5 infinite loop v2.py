import random
from collections import defaultdict


class BingoGame:
    def __init__(self, players=1):
        self.max_players = min(5, max(1, players))
        self.players_cards = self.generate_all_cards()
        self.called_numbers = []
        self.winners = defaultdict(list)
        self.game_over = False
        self.mc_calls = 0
        self.max_calls = float('inf')  # Infinite calls until someone wins

    def generate_all_cards(self):
        numbers_per_player = 24  # 5x5 grid with center star
        total_numbers_needed = self.max_players * numbers_per_player

        # Adjust if we need more numbers than available (1-100)
        if total_numbers_needed > 100:
            # Reduce numbers per player to fit within 100
            numbers_per_player = 100 // self.max_players
            total_numbers_needed = numbers_per_player * self.max_players

        # Generate all unique numbers for all players
        all_unique_numbers = random.sample(range(1, 101), total_numbers_needed)

        # Distribute numbers to players
        players_cards = []
        number_iter = iter(all_unique_numbers)

        for _ in range(self.max_players):
            card = []
            # Build 5x5 grid for each player
            for i in range(5):
                row = []
                for j in range(5):
                    if i == 2 and j == 2:  # Center position
                        row.append("★")
                    else:
                        try:
                            row.append(next(number_iter))
                        except StopIteration:
                            # If we run out of unique numbers, fill with random (may have duplicates)
                            row.append(random.randint(1, 100))
                card.append(row)
            players_cards.append(card)

        return players_cards

    def call_number(self):
        if self.game_over or len(self.called_numbers) == 100:
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

        # Calls 21-30: New rule for odd/even alternation
        elif 20 <= self.mc_calls < 30:
            if self.called_numbers[-1] % 2 == 0:
                available = [n for n in range(
                    21, 31) if n % 2 != 0 and n not in self.called_numbers]
            else:
                available = [n for n in range(
                    21, 31) if n % 2 == 0 and n not in self.called_numbers]

        # After first 30 calls, switch to random from all numbers
        else:
            available = [n for n in range(
                1, 101) if n not in self.called_numbers]

        if not available:
            # Fallback to any available number if no numbers left in category
            available = [n for n in range(
                1, 101) if n not in self.called_numbers]
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
        elif 20 <= self.mc_calls < 30:
            print("MC is calling from range 21-30 with odd/even alternation")
        else:
            print("MC is calling from random remaining numbers")

        return number

    def check_almost_lines(self, player_idx):
        card = self.players_cards[player_idx]
        called = self.called_numbers
        almost_lines = []

        # Check rows
        for row_idx, row in enumerate(card):
            missing = [num for num in row if num not in called and num != "★"]
            if len(missing) == 1:
                almost_lines.append(f"Row {row_idx+1} needs {missing[0]}")

        # Check columns
        for col_idx in range(5):
            missing = []
            for row_idx in range(5):
                num = card[row_idx][col_idx]
                if num not in called and num != "★":
                    missing.append(num)
            if len(missing) == 1:
                almost_lines.append(f"Column {col_idx+1} needs {missing[0]}")

        # Check diagonals
        # Top-left to bottom-right
        missing = []
        for i in range(5):
            num = card[i][i]
            if num not in called and num != "★":
                missing.append(num)
        if len(missing) == 1:
            almost_lines.append(f"Diagonal (\\) needs {missing[0]}")

        # Top-right to bottom-left
        missing = []
        for i in range(5):
            num = card[i][4-i]
            if num not in called and num != "★":
                missing.append(num)
        if len(missing) == 1:
            almost_lines.append(f"Diagonal (/) needs {missing[0]}")

        return almost_lines

    def check_card_completion(self, player_idx):
        card = self.players_cards[player_idx]
        called = self.called_numbers
        for row in card:
            for num in row:
                if num not in called and num != "★":
                    return False
        return True

    def check_card(self, player_idx):
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

        if lines_won > 0 and player_idx not in self.winners:
            self.winners[player_idx] = lines_won

        # Check if player completed entire card
        if self.check_card_completion(player_idx):
            print(
                f"\n🎉 Player {player_idx+1} has completed their ENTIRE CARD! 🎉")
            self.game_over = True
            return 99  # Special value indicating full card completion

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
        print(f"MC calls number: {called} (Call #{self.mc_calls})")
        print(f"Called numbers: {sorted(self.called_numbers)}")

        # Show all players' cards and check status
        for i in range(self.max_players):
            self.display_card(i)

            # Check for almost completed lines
            almost_lines = self.check_almost_lines(i)
            if almost_lines:
                print(f"  → Player {i+1} is almost there!")
                for line in almost_lines:
                    print(f"    - {line}")

            # Check for completed lines and full card
            lines = self.check_card(i)
            if lines > 0:
                print(f"  → Player {i+1} completed {lines} line(s)!")
            if lines == 99:  # Full card completed
                return called

        return called

    def get_rankings(self):
        # Sort by: 1) full card completion, 2) number of lines, 3) player number
        ranked = sorted(self.winners.items(),
                        key=lambda x: (-(1 if x[1] == 99 else 0), -x[1], x[0]))
        rankings = [(player+1, "FULL CARD" if lines == 99 else f"{lines} line(s)")
                    for player, lines in ranked]

        # Show 2nd to 5th completed lines and unfinished positions
        report = []
        for i, (player, lines) in enumerate(rankings):
            if i == 0:
                continue  # Skip the first player (winner)
            if i < 4:
                report.append(f"{i+1}. Player {player} - {lines}")
            else:
                report.append(f"{i+1}. Player {player} - Unfinished")

        return report
##################################################################################################################


def play_game():
    print("""
    *************************************
    *           BINGO GAME             *
    *        Center has a star ★       *
    *      Numbers range: 1-100        *
    *  First 10 calls: 1-10, 11-20,...*
    *  Calls 11-15: Prime numbers      *
    *  Calls 16-20: Composite numbers  *
    *  Then random from remaining      *
    *  Game ends when someone          *
    *  completes their entire card     *
    *  Max 5 players                   *
    *  Shows 'almost there' hints      *
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
        if called is None or game.game_over:
            break

    # Game over
    print("\n" + "="*40)
    print("=== GAME OVER ===")
    print(f"Total numbers called: {len(game.called_numbers)}")

    rankings = game.get_rankings()
    if rankings:
        print("\nFinal Rankings:")
        for rank in rankings:
            # Each rank is already a tuple of (player_number, status)
            print(f"{rank[0]}. Player {rank[0]} - {rank[1]}")
    else:
        print("\nNo winners this game!")

    print("\nThanks for playing!")


def confirm_exit():
    while True:
        answer = input(
            "Type 'exit' to close: or 'restart to restart the game: ").strip().lower()
        if answer == 'exit':
            confirm = input("Are you sure? (yes/no): ").strip().lower()
            if confirm == 'yes':
                print("Closing the game...")
                return  # Exit the function and end the program
            else:
                print("Resuming...")
        elif answer == 'restart":
            print("Restarting the game...")
            return True  # Restart the game
        else:
            print("Invalid command. Type 'exit' to quit or 'restart' to play again.")")

if __name__ == "__main__":
     while True:  # Main game loop
        play_game()
        should_restart = confirm_exit()
        if not should_restart:
            break  # Exit the loop and end the program