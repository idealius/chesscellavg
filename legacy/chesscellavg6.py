import pygame
import chess
import chess.pgn
import io
from collections import defaultdict

# Current bugs:
# Castling only counts King movements
# Sometimes starting positions are missed
# Likely en passant is not handled properly
# Likely other rare-ish bugs with counting algo

# Initialize pygame
pygame.init()

# Calculate square size based on screen dimensions
screen_width = 800  # Example screen dimensions
screen_height = 600
board_size = min(screen_width, screen_height)  # Use the smaller dimension
square_size = board_size // 8

# Define colors
WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
LBLUE = (127, 127, 192)
DBLUE = (0, 0, 127)
RED = (255, 0, 0)
# BLUE = (0, 0, 255)

VERBOSE = True

# Initial positions for white and black pieces
white_piece_type = [
    ["R", "a1", "h1"],
    ["N", "b1", "g1"],
    ["B", "c1", "f1"],
    ["Q", "d1"],
    ["K", "e1"],
    ["P", "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2"]
]

black_piece_type = [
    ["R", "a8", "h8"],
    ["N", "b8", "g8"],
    ["B", "c8", "f8"],
    ["Q", "d8"],
    ["K", "e8"],
    ["P", "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7"]
]


piece_starting_positions = [
    "a1", "b1", "c1", "d1",
    "e1", "f1", "g1", "h1",
    "a2", "b2", "c2", "d2",
    "e2", "f2", "g2", "h2",
    "a7", "b7", "c7", "d7",
    "e7", "f7", "g7", "h7",
    "a8", "b8", "c8", "d8",
    "e8", "f8", "g8", "h8"
]

def chess_notation_to_indices(notation):
    file = ord(notation[0]) - ord('a') + 1
    rank = int(notation[1])
    return (file, rank)

# Function to draw chessboard
def draw_board(screen):
    for row in range(8):
        for col in range(8):
            color = LBLUE if (row + col) % 2 == 0 else DBLUE
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

def render_text(screen, text, position, color):
    font = pygame.font.SysFont("Arial", 20)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def render_counts(screen, total_positions_seen):
    surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        # Find the maximum value
    # Find the maximum value
    true_max = max(total_positions_seen.values(), default=1)
    threshold = 20 #if moves to position is within this threshold of the top position then it and the max are removed from the circle alpha calculation

    # Remove all values within 5 of the maximum value
    filtered_values = [v for v in total_positions_seen.values() if abs(v - true_max) > threshold]

    # Find the second maximum value
    max_count = max(filtered_values, default=true_max) if filtered_values else true_max

    font = pygame.font.SysFont("Arial", 16)  # Small font for counts

    for coord, count in total_positions_seen.items():
        x, y = map(int, coord.split(','))
        # Reverse the y-coordinate
        y = 9 - y
        intensity = int((count / max_count) * 255)
        if intensity > 255:
            intensity = 255
        radius = square_size // 4
        color = (255, 0, 0, intensity)  # Red with varying opacity
        circle_center = ((x - 1) * square_size + square_size // 2, (y - 1) * square_size + square_size // 2)

        # Draw circle
        pygame.draw.circle(surface, color, circle_center, radius)

        # Render count number
        count_text = font.render(f"{(count / true_max * 100):.1f}%", True, WHITE)
        text_rect = count_text.get_rect(center=circle_center)
        surface.blit(count_text, text_rect)
    
    screen.blit(surface, (0, 0))
    
    render_text(screen, "↑" + str(max_count), (square_size * 8 + 5, 10) , WHITE)



# Function to process a single game
def process_single_game(game_data, starting_positions, total_positions_seen, xy_coords):
    # positions = initialize_positions()
    positions = []
    positions_seen = defaultdict(int)

    if VERBOSE:
        print('\n')

    if isinstance(game_data, str):
        game_stream = io.StringIO(game_data)
        game = chess.pgn.read_game(game_stream)
    elif isinstance(game_data, chess.pgn.Game):
        game = game_data
    else:
        raise ValueError("Invalid game_data format. Expected str or chess.pgn.Game.")

    if game is None:
        return

    board = game.board()

    for move in game.mainline_moves():
        from_square = str(move)[:2]
        to_square = str(move)[2:4]

        # Check if to_position is occupied and if so mark the other piece with an x
        for pos in positions:
            if pos[-1] == to_square:
                pos.append('x')

        # Check if from_position exists in positions, if not, add it
        from_position_exists = False
        for pos in positions:
            if pos[-1] == from_square:
                from_position_exists = True
                break

        if not from_position_exists:
            positions.append([from_square])

        # Update the piece's position
        for pos in positions:
            if pos[-1] == from_square:
                pos.append(to_square)
                break

        board.push(move)

    found_start_positions = []
    for start_pos in piece_starting_positions:
        for path in positions:
            if start_pos == path[0]:
                found_start_positions.append(start_pos)

                    
            
    for start_pos in piece_starting_positions:
        found = False
        for found_pos in found_start_positions:    
            if found_pos == start_pos:
                found = True
        if not found:
            positions.append([start_pos])
            if VERBOSE:
                print("+"+str([start_pos]) + ",", end="")


    if VERBOSE:
        print('\n')
        print(positions)

    
    # Iterate through positions to count occurrences
    for pos in positions:
        if pos[0] in starting_positions:
            # Check and remove 'x' if it's the last element
            if pos[-1] == 'x':
                pos.pop()  # Remove 'x' from the list

            for coord in pos:
                if VERBOSE:
                    print(coord)
                if coord != 'x':
                    if xy_coords:
                        x, y = chess_notation_to_indices(coord)
                        coord_str = f"{x},{y}"
                    else:
                        coord_str = coord
                    positions_seen[coord_str] += 1

    # Aggregate counts from positions_seen into total_positions_seen
    for coord, count in positions_seen.items():
        total_positions_seen[coord] += count

# Function to update positions for all games
def update_positions(games, starting_positions, xy_coords):
    total_positions_seen = defaultdict(int)

    for game_data in games:
        process_single_game(game_data, starting_positions, total_positions_seen, xy_coords)

    return total_positions_seen

# Function to get starting positions by piece type
def get_starting_positions_by_piece_type(piece_type, piece_color):
    if piece_color == 'white' or piece_color == 'w':
        piece_array = white_piece_type
    else:
        piece_array = black_piece_type

    for piece in piece_array:
        if piece[0].upper() == piece_type.upper():
            return piece[1:]
    return []

# Function to analyze games by piece type
def analyze_games_by_piece_type(games, piece_type, piece_color, xy_coords):
    starting_positions = get_starting_positions_by_piece_type(piece_type, piece_color)
    if not starting_positions:
        print(f"No starting positions found for piece type {piece_type} and color {piece_color}.")
        return {}

    total_positions_seen = update_positions(games, starting_positions, xy_coords)
    return total_positions_seen

def parse_pgn(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
        games = content.split('\n[Event')
        games = ['[Event' + game for game in games if game]

    return games

def main():
    file_path = input("Enter the path to the PGN file: ")
    if file_path == "":
        file_path = "wexample.pgn"
    games = parse_pgn(file_path)
    xy_coords = True  # Don't set this to False as this will mess up some of the code with the rendering in pygame

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Chessboard")

    clock = pygame.time.Clock()
    running = True

    input_mode = 'choose_mode'  # Start by asking for the mode (position or piece type)
    piece_type = ""
    piece_color = ""
    starting_position = ""
    stats = {}

    while running:
        screen.fill(LBLUE)  # White background
        draw_board(screen)

        if stats:
            render_counts(screen, stats)

        if input_mode == 'choose_mode':
            render_text(screen, "Choose search mode (1: Piece Type, 2: Starting Position): ", (10, screen_height - 70), WHITE)

        elif input_mode == 'piece_type':
            render_text(screen, "Enter piece type (e.g., K, Q, N): " + piece_type, (10, screen_height - 70), WHITE)

        elif input_mode == 'piece_color':
            render_text(screen, "Enter piece color (white/black): " + piece_color, (10, screen_height - 70), WHITE)

        elif input_mode == 'position':
            render_text(screen, "Enter starting position (e.g., a1, b2): " + starting_position, (10, screen_height - 70), WHITE)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if input_mode == 'choose_mode':
                    if event.key == pygame.K_1:
                        input_mode = 'piece_type'
                    elif event.key == pygame.K_2:
                        input_mode = 'position'

                elif input_mode == 'piece_type':
                    if event.key == pygame.K_RETURN:
                        input_mode = 'piece_color'
                    elif event.key == pygame.K_BACKSPACE:
                        piece_type = piece_type[:-1]
                    else:
                        piece_type += event.unicode

                elif input_mode == 'piece_color':
                    if event.key == pygame.K_RETURN:
                        input_mode = 'analyze_piece_type'
                        stats = analyze_games_by_piece_type(games, piece_type, piece_color, xy_coords)
                    elif event.key == pygame.K_BACKSPACE:
                        piece_color = piece_color[:-1]
                    else:
                        piece_color += event.unicode

                elif input_mode == 'position':
                    if event.key == pygame.K_RETURN:
                        input_mode = 'analyze_position'
                        stats = update_positions(games, [starting_position], xy_coords)
                    elif event.key == pygame.K_BACKSPACE:
                        starting_position = starting_position[:-1]
                    else:
                        starting_position += event.unicode

                elif input_mode == 'analyze_piece_type' or input_mode == 'analyze_position':
                    if event.key == pygame.K_RETURN:
                        input_mode = 'choose_mode'  # After analysis, go back to choosing mode

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
