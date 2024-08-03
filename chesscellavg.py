import chess
import chess.pgn
import io
from collections import defaultdict
import argparse
import os
import pygame
import math

print("--help for more options\n")
print("\n")

# Known bugs:
# Positions seems to not calculate considering pawns get promoted, while threaten situations it does.

# Calculate square size based on screen dimensions
screen_width = 800
screen_height = 600
board_size = min(screen_width, screen_height)
square_size = board_size // 8

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LBLUE = (127, 127, 192)
DBLUE = (0, 0, 127)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DEFAULT_SIZE = 20  # font size

VERBOSE = False

board_display = "percent"
default_filename = "myfile.pgn"
settings = None
total_games = 0

def parse_arguments():
    global VERBOSE, screen_height, screen_width, board_size, square_size, board_display

    parser = argparse.ArgumentParser(description="Chess PGN Processor")

    parser.add_argument('--pgnfile', type=str, help='Path to the PGN file.')
    parser.add_argument('--verbose', action='store_true', help='Enable debug output.')
    parser.add_argument('--screen_width', type=int, default=screen_width, help='Width of the screen.')
    parser.add_argument('--screen_height', type=int, default=screen_height, help='Height of the screen.')
    parser.add_argument('--search_mode', type=int, choices=[1, 2], help='Search mode: 1 for Piece Type, 2 for Starting Position.')
    parser.add_argument('--piece_type', type=str, help='Type of piece to search for (K)ing, (P)awn, etc. Required for piece type search mode')
    parser.add_argument('--starting_position', type=str, help='Starting position to search for (e.g., a1, b2). Required for starting position search mode')
    parser.add_argument('--piece_color', type=str, help='Color of the piece to search for (white or black). Required for piece type search mode')
    parser.add_argument('--timeout', type=int, default=-1, help='Timeout in seconds. Default is -1, meaning no timeout.')
    parser.add_argument('--board_display', type=str, default=board_display, help='Show board positions in (percent) or (totals)')
    args = parser.parse_args()

    if '--help' in vars(args):
        parser.print_help()
        return

    VERBOSE = args.verbose
    screen_width = args.screen_width
    screen_height = args.screen_height
    board_size = min(screen_width, screen_height)
    square_size = board_size // 8
    board_display = args.board_display

    return vars(args)

# Initialize pygame
pygame.init()



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


def initialize_positions():
    return [
        ["a1"], ["b1"], ["c1"], ["d1"],
        ["e1"], ["f1"], ["g1"], ["h1"],
        ["a2"], ["b2"], ["c2"], ["d2"],
        ["e2"], ["f2"], ["g2"], ["h2"],
        ["a7"], ["b7"], ["c7"], ["d7"],
        ["e7"], ["f7"], ["g7"], ["h7"],
        ["a8"], ["b8"], ["c8"], ["d8"],
        ["e8"], ["f8"], ["g8"], ["h8"]
    ]



def chess_notation_to_indices(notation):
    file = ord(notation[0]) - ord('a') + 1
    rank = int(notation[1])
    return (file, rank)

def save_screenshot(screen, file_path):
    base_filename, _ = os.path.splitext(file_path)
    suffix = 0
    file_name = f"{base_filename}.png"
    while os.path.exists(file_name):
        suffix += 1
        file_name = f"{base_filename}_{suffix}.png"
    pygame.image.save(screen, file_name)
    print(f"Screenshot saved as {file_name}")

def draw_board(screen):
    for row in range(8):
        for col in range(8):
            color = LBLUE if (row + col) % 2 == 0 else DBLUE
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

def render_text(screen, text, position, color, size=DEFAULT_SIZE, update_screen_immediately=False, center=False):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if center:
        text_rect.center = position
    else:
        text_rect.topleft = position

    shadow_surface = font.render(text, True, (0, 0, 0))
    shadow_position = (text_rect.x + 1, text_rect.y + 1)
    screen.blit(shadow_surface, shadow_position)
    
    screen.blit(text_surface, text_rect.topleft)

    if update_screen_immediately:
        pygame.display.flip()

def render_counts(screen, total_positions_seen, total_threatened_positions, total_threat_positions, display_mode):
    global board_display, total_games, settings
    surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

    if display_mode == 'positions':
        data_to_display = total_positions_seen
    elif display_mode == 'threatened':
        data_to_display = total_threatened_positions
    else:
        data_to_display = total_threat_positions

    true_max = max(data_to_display.values(), default=1)
    true_min = min(data_to_display.values(), default=0)

    font = pygame.font.SysFont("Arial", 16)

    for coord, count in data_to_display.items():
        x, y = map(int, coord.split(','))
        y = 9 - y
        
        if display_mode == 'positions':
            threshold = true_max * 0.004
            filtered_values = [v for v in data_to_display.values() if abs(v - true_max) > threshold]
            max_count = max(filtered_values, default=true_max) if filtered_values else true_max
            intensity = int((count / max_count) * 255)
        else:
            # For threatened positions, use a logarithmic scale
            if true_max > true_min:
                log_min = math.log(true_min + 1)  # Add 1 to avoid log(0)
                log_max = math.log(true_max + 1)
                log_count = math.log(count + 1)
                intensity = int(((log_count - log_min) / (log_max - log_min)) * 255)
            else:
                intensity = 255 if count > 0 else 0
        intensity = max(0, min(intensity, 255))  # Ensure intensity is between 0 and 255
        
        radius = square_size // 4
        if display_mode == 'positions':
            color = (0, 0, 0, intensity)
        elif display_mode == 'threatened':
            color = (255, 0, 0, intensity)
        else:
            color = (0, 255, 0, intensity)

        circle_center = ((x - 1) * square_size + square_size // 2, (y - 1) * square_size + square_size // 2)

        pygame.draw.circle(surface, color, circle_center, radius)

        if board_display == "percent":
            count_text = font.render(f"{(count / true_max * 100):.1f}%", True, WHITE)
        else:
            count_text = font.render(f"{count}", True, WHITE)
        text_rect = count_text.get_rect(center=circle_center)
        surface.blit(count_text, text_rect)
    
    screen.blit(surface, (0, 0))
    
    if settings["piece_type"] is not None:
        render_text(screen, "Tracking " + settings["piece_type"], (square_size * 8 + 5, 0), WHITE, 16)
    render_text(screen, "↑" + str(true_max), (square_size * 8 + 5, 20) , WHITE, 16)
    render_text(screen, "Top square's total!", (square_size * 8 + 5, 40) , WHITE, 16)
    render_text(screen, "(All %'s are based on the total)", (square_size * 8 + 5, 60) , WHITE, 12)
    # render_text(screen, "Promotions still considered pawns", (square_size * 8 + 5, 80) , WHITE, 12)
    render_text(screen, "More options in commandline!", (square_size * 8 + 5, 100) , WHITE, 12)
    render_text(screen, settings["pgnfile"], (square_size * 8 + 5, 120) , WHITE, 12)
    render_text(screen, settings["piece_color"], (square_size * 8 + 5, 140) , WHITE, 12)
    render_text(screen, "Total games: " + str(total_games), (square_size * 8 + 5, 160) , WHITE, 12)
    if display_mode == 'positions':
        render_text(screen, "Displaying: Positions", (square_size * 8 + 5, 180), WHITE, 12)
    elif display_mode == 'threatened':
        render_text(screen, "Displaying: Threatened at", (square_size * 8 + 5, 180), WHITE, 12)
    else:
        render_text(screen, "Displaying: Threatening", (square_size * 8 + 5, 180), WHITE, 12)

    render_text(screen, "T=Toggle Positions, Threatened at,", (square_size * 8 + 5, screen_height - 180), WHITE, 12)
    render_text(screen, "Threatening opponent", (square_size * 8 + 5, screen_height - 150), WHITE, 12)
    
    render_text(screen, "ESC=Exit", (square_size * 8 + 5, screen_height - 120), WHITE, 12)
    render_text(screen, "PRTSCRN screenshot path_1.png", (square_size * 8 + 5, screen_height - 90), WHITE, 12)
    render_text(screen, "ENTER=New Query", (square_size * 8 + 5, screen_height - 60), WHITE, 12)
    

import chess
import chess.pgn
import io
from collections import defaultdict

def process_single_game(game_data, starting_positions, total_positions_seen, total_threatened_positions, total_threat_positions, xy_coords):
    global total_games
    positions = initialize_positions()
    positions_seen = defaultdict(int)
    threatened_positions = defaultdict(int)
    threat_positions = defaultdict(int)

    if isinstance(game_data, str):
        game_stream = io.StringIO(game_data)
        game = chess.pgn.read_game(game_stream)
    elif isinstance(game_data, chess.pgn.Game):
        game = game_data
    else:
        raise ValueError("Invalid game_data format. Expected str or chess.pgn.Game.")

    game_moves = game.mainline_moves()

    if game_moves is None or game is None:
        print("No moves or game found! Processing next game.")
        return

    board = game.board()
    positions_found = False
    for move in game_moves:
        from_square = chess.SQUARE_NAMES[move.from_square]
        to_square = chess.SQUARE_NAMES[move.to_square]

        # Update positions and handle special moves (castling, en passant)
        for path in positions:
            if path[-1] == to_square:
                path.append('x')
            if path[-1] == from_square:
                path.append(to_square)
                positions_found = True

        # Handle castling
        if board.is_castling(move):
            if to_square == 'g1':
                for path in positions:
                    if path[-1] == 'h1':
                        path.append('f1')
            elif to_square == 'c1':
                for path in positions:
                    if path[-1] == 'a1':
                        path.append('d1')
            elif to_square == 'g8':
                for path in positions:
                    if path[-1] == 'h8':
                        path.append('f8')
            elif to_square == 'c8':
                for path in positions:
                    if path[-1] == 'a8':
                        path.append('d8')

        # Push the move only if it is legal
        if move in board.legal_moves:
            board.push(move)
        else:
            print(f"Illegal move found: {move}. Skipping the rest of the game.")
            return

    if not positions_found:
        print("No positions found in game! Processing next game.")
        return

    total_games += 1

    # Count positions
    for path in positions:
        if path[0] in starting_positions:
            for pos in path:
                if pos != 'x':
                    if xy_coords:
                        x, y = chess_notation_to_indices(pos)
                        coord_str = f"{x},{y}"
                    else:
                        coord_str = pos
                    positions_seen[coord_str] += 1
                    
                    # Since we just found a new position, this is an opportune time to calculate its threatened positions
                    piece_square = chess.parse_square(pos)
                    if piece_square is not None and board.piece_type_at(piece_square) is not None:
                        piece_color = board.color_at(piece_square)
                        piece_type = board.piece_type_at(piece_square)
                        if VERBOSE:
                            print(f"Piece at {pos}: {chess.PIECE_NAMES[piece_type]} ({chess.COLOR_NAMES[piece_color]})")
                        
                        # threatened by opponent
                        for square in chess.SQUARES:
                            if board.piece_type_at(square) is not None:
                                if board.color_at(square) != piece_color:
                                    if board.is_attacked_by(board.color_at(square), piece_square):
                                        threatened_square = chess.SQUARE_NAMES[piece_square]
                                        if xy_coords:
                                            x, y = chess_notation_to_indices(threatened_square)
                                            threatened_coord = f"{x},{y}"
                                        else:
                                            threatened_coord = threatened_square
                                        threatened_positions[threatened_coord] += 1
                                        if VERBOSE:
                                            print(f"Position {threatened_coord} is threatened by opponent")
                        
                        # threatening opponent)
                        for square in chess.SQUARES:
                            if board.is_attacked_by(piece_color, square):
                                if board.piece_type_at(square) is not None and board.color_at(square) != piece_color:
                                    threatened_square = chess.SQUARE_NAMES[square]
                                    if xy_coords:
                                        x, y = chess_notation_to_indices(threatened_square)
                                        threat_coord = f"{x},{y}"
                                    else:
                                        threat_coord = threatened_square
                                    threat_positions[threat_coord] += 1
                                    if VERBOSE:
                                        print(f"Position {threat_coord} is threatened by {chess.PIECE_NAMES[piece_type]}")
    if VERBOSE:
        print("Final threatened positions:", threatened_positions)
        print("Final threat positions:", threat_positions)

    # Aggregate counts
    for coord, count in positions_seen.items():
        total_positions_seen[coord] += count
    for coord, count in threatened_positions.items():
        total_threatened_positions[coord] += count
    for coord, count in threat_positions.items():
        total_threat_positions[coord] += count


def update_positions(games, starting_positions, xy_coords):
    global settings
    total_positions_seen = defaultdict(int)
    total_threatened_positions = defaultdict(int)
    total_threat_positions = defaultdict(int)

    settings["piece_color"] = None
    for piece_type in white_piece_type + black_piece_type:
        for piece in piece_type[1:]:
            if piece in starting_positions:
                settings["piece_color"] = "white" if piece_type in white_piece_type else "black"
                settings["piece_type"] = piece_type[0] + (starting_positions[0] if len(starting_positions) == 1 else "")
                break
        if settings["piece_color"]:
            break

    for game_data in games:
        process_single_game(game_data, starting_positions, total_positions_seen, total_threatened_positions, total_threat_positions, xy_coords)

    return total_positions_seen, total_threatened_positions, total_threat_positions

def get_starting_positions_by_piece_type(piece_type, piece_color):
    global settings
    piece_array = white_piece_type if piece_color.lower() in ['white', 'w'] else black_piece_type
    settings["piece_color"] = "white" if piece_color.lower() in ['white', 'w'] else "black"

    for piece in piece_array:
        if piece[0].upper() == piece_type.upper():
            return piece[1:]
    return []

def analyze_games_by_piece_type(games, piece_type, piece_color, xy_coords):
    starting_positions = get_starting_positions_by_piece_type(piece_type, piece_color)
    if not starting_positions:
        print(f"No starting positions found for piece type {piece_type} and color {piece_color}.")
        return {}, {}

    return update_positions(games, starting_positions, xy_coords)

def parse_pgn(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    games = content.split('\n[Event ')
    games = ['[Event ' + game for game in games if game]

    return games

def main():
    global settings, total_games
    settings = parse_arguments()
    
    file_path = settings["pgnfile"] or input(f"Enter the path to the PGN file (default={default_filename}): ") or default_filename
    settings["pgnfile"] = file_path
    games = parse_pgn(file_path)
    xy_coords = True

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Chessboard Position and Threat Frequency")

    clock = pygame.time.Clock()
    running = True
    
    first_run = True

    input_mode = 'choose_mode'
    piece_type = ""
    piece_color = ""
    starting_position = ""
    position_stats = {}
    threatened_stats = {}
    threat_stats = {}
    display_mode = 'positions'  # Start with displaying positions

    time = 0
    total_games = 0

    while running:
        screen.fill(LBLUE)
        draw_board(screen)

        if position_stats or threatened_stats or threat_stats:
            render_counts(screen, position_stats, threatened_stats, threat_stats, display_mode)
            
        if settings["timeout"] == -1:
            if input_mode == 'choose_mode':
                render_text(screen, "Choose search mode (1) Piece Type, (2) Starting Position): ", (10, screen_height - 70), WHITE)
            elif input_mode == 'piece_type':
                render_text(screen, "Enter piece type (K)ing, (P)awn, etc: " + piece_type, (10, screen_height - 70), WHITE)
            elif input_mode == 'piece_color':
                render_text(screen, "Enter piece color (w)hite / (b)lack: " + piece_color, (10, screen_height - 70), WHITE)
            elif input_mode == 'position':
                render_text(screen, "Enter starting position (e.g., a1, b2): " + starting_position, (10, screen_height - 70), WHITE)

        pygame.display.flip()
                    
        if settings["timeout"] != -1 and first_run == False:
            time += 1
            
            if (time * 0.01667) >= settings["timeout"]: 
                running = False
                save_screenshot(screen, file_path)
            elif time % (settings["timeout"] * 60 // 4) == 0:
                print(str(settings["timeout"] - int(time * 0.01667)) + " seconds left until exiting.")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
        elif isinstance(settings["search_mode"], int) and first_run:
            if settings["search_mode"] == 1:
                render_text(screen, "Calculating...", (screen_width / 2, screen_height / 2), WHITE, 70, True, True)
                position_stats, threatened_stats, threat_stats = analyze_games_by_piece_type(games, settings["piece_type"], settings["piece_color"], xy_coords)
            else:
                render_text(screen, "Calculating...", (screen_width / 2, screen_height / 2), WHITE, 70, True, True)
                position_stats, threatened_stats, threat_stats = update_positions(games, [settings["starting_position"]], xy_coords)
            first_run = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_PRINTSCREEN:
                        save_screenshot(screen, file_path)
                    elif event.key == pygame.K_t:
                        if display_mode == 'positions':
                            display_mode = 'threat'
                        elif display_mode == 'threat':
                            display_mode = 'threatened'
                        elif display_mode == 'threatened':
                            display_mode = 'positions'

                    if input_mode == 'choose_mode':
                        total_games = 0
                        if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                            input_mode = 'piece_type'
                        elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                            input_mode = 'position'

                    elif input_mode == 'piece_type':
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            input_mode = 'piece_color'
                        elif event.key == pygame.K_BACKSPACE:
                            piece_type = piece_type[:-1]
                        else:
                            piece_type += event.unicode

                    elif input_mode == 'piece_color':
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            input_mode = 'analyze_piece_type'
                            
                            render_text(screen, "Calculating...", (screen_width / 2, screen_height / 2), WHITE, 70, True, True)
                            position_stats, threatened_stats, threat_stats = analyze_games_by_piece_type(games, piece_type, piece_color, xy_coords)
                        elif event.key == pygame.K_BACKSPACE:
                            piece_color = piece_color[:-1]
                        else:
                            piece_color += event.unicode

                    elif input_mode == 'position':
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            input_mode = 'analyze_position'
                            render_text(screen, "Calculating...", (screen_width / 2, screen_height / 2), WHITE, 70, True, True)
                            position_stats, threatened_stats, threat_stats = update_positions(games, [starting_position], xy_coords)
                        elif event.key == pygame.K_BACKSPACE:
                            starting_position = starting_position[:-1]
                        else:
                            starting_position += event.unicode

                    elif input_mode == 'analyze_piece_type' or input_mode == 'analyze_position':
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            input_mode = 'choose_mode'  # After analysis, go back to choosing mode

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()