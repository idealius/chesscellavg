import chess
import chess.pgn
import io
from collections import defaultdict

positions = None

positions_seen = None

def initialize_positions():
    global positions
    positions = [
        ["a1"], ["b1"], ["c1"], ["d1"],
        ["e1"], ["f1"], ["g1"], ["h1"],
        ["a2"], ["b2"], ["c2"], ["d2"],
        ["e2"], ["f2"], ["g2"], ["h2"],
        ["a7"], ["b7"], ["c7"], ["d7"],
        ["e7"], ["f7"], ["g7"], ["h7"],
        ["a8"], ["b8"], ["c8"], ["d8"],
        ["e8"], ["f8"], ["g8"], ["h8"]
    ]
    return positions

def chess_notation_to_indices(notation):
    file = ord(notation[0]) - ord('a') + 1
    rank = int(notation[1])
    return (file, rank)

def update_positions(games, starting_position_filter):
    
    global positions
    global positions_seen
    # Initialize defaultdict to count occurrences
    
    total_positions_seen = defaultdict(int)
    i=0
    c=0
    for game_text in games:

        positions_seen = defaultdict(int)
        game_stream = io.StringIO(game_text)
        positions = initialize_positions()
        game = chess.pgn.read_game(game_stream)
        if not game:
            continue


        board = game.board()
        i=i+1
        print(i)
        for move in game.mainline_moves():

            c=c+1
            print(c)
            from_square = str(move)[:2]
            to_square = str(move)[2:4]

            # Check if to_position is occupied
            for pos in positions:
                if pos[-1] == to_square:
                    pos.append('x')
            
            # Update the piece's position
            for pos in positions:
                if pos[-1] == from_square:
                    pos.append(to_square)
                    break
            
            board.push(move)

            # Iterate through positions to count occurrences
            for pos in positions:
                if pos[0] == starting_position_filter:
                    # Check and remove 'x' if it's the last element
                    if pos[-1] == 'x':
                        pos.pop()  # Remove 'x' from the list
                    
                    for coord in pos[1:]:
                        # Example using chess_notation_to_indices with 'x' handling
                        if coord != 'x':                    
                            x, y = chess_notation_to_indices(coord)
                            # Convert tuple (x, y) to string for using as a dictionary key
                            coord_str = f"{x},{y}"
                            positions_seen[coord_str] += 1

            for coord, count in positions_seen.items():
                total_positions_seen[coord] += count

            # Print positions with their counts
            for pos in positions:
                print(pos)
            for coord, count in positions_seen.items():
                print(f"Coordinate {coord} has been seen {count} times.")

    
    for coord, count in total_positions_seen.items():
        print(f"Total coordinate {coord} has been seen {count} times.")

    return positions_seen




def parse_pgn(file_path):
    with open(file_path, 'r') as f:
        games = f.read().split('\n\n\n')
    return games

def main():
    
    file_path = input("Enter the path to the PGN file: ")
    if file_path == "":
        file_path = "example3.pgn"
    games = parse_pgn(file_path)

    # analyze_by_type = input("Analyze by piece type? (y/n): ").strip().lower() == 'y'
    analyze_by_type = False

    # update_positions(games)

    # stats = update_positions(games)



    # while True:
    #     if analyze_by_type:
    #         piece_filter = input("Enter the piece or piece type to analyze (e.g., K for king, q for queen, N for knight, etc.): ").strip()
    #         stats = analyze_games_by_piece_type(games, piece_filter, position_count)
    #         display_board_stats(stats)
    #     else:
    #         break  # Exit the loop if not analyzing by piece type

    #     continue_choice = input("Do you want to analyze another piece/type? (y/n): ").strip().lower()
    #     if continue_choice != 'y':
    #         break

    while not analyze_by_type:  # Only enter if not analyzing by piece type
        position_filter = input("Enter the starting board position in algebraic notation (e.g., a1, b2, c4, etc.): ").strip()
        stats = update_positions(games, position_filter)
        # display_board_stats(stats)
        for pos in stats:
            print(pos)

        continue_choice = input("Do you want to analyze another position? (y/n): ").strip().lower()
        if continue_choice != 'y':
            break

if __name__ == "__main__":
    main()