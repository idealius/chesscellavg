
import chess
import chess.pgn
import io
from collections import defaultdict
import argparse
import os

# Current bugs:
# None known but I'm sure there's some.

print("--help for more options\n")
import pygame
print("\n")


# Calculate square size based on screen dimensions
screen_width = 800  # Example screen dimensions
screen_height = 600
board_size = min(screen_width, screen_height)  # Use the smaller dimension
square_size = board_size // 8


# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LBLUE = (127, 127, 192)
DBLUE = (0, 0, 127)
RED = (255, 0, 0)
# BLUE = (0, 0, 255)
DEFAULT_SIZE = 20 #font size

VERBOSE = False
board_display = "percent"
default_filename = "wexample.pgn" # Not used for command line mode

def parse_arguments():
    global VERBOSE
    global screen_height
    global screen_width
    global board_size
    global square_size
    global board_display


    parser = argparse.ArgumentParser(description="Chess PGN Processor")

    # Define default values
    parser.add_argument('--pgnfile', type=str, help='Path to the PGN file.')
    parser.add_argument('--verbose', action='store_true', help='Enable debug output.')
    parser.add_argument('--screen_width', type=int, default=screen_width, help='Width of the screen.')
    parser.add_argument('--screen_height', type=int, default=screen_height, help='Height of the screen.')
    parser.add_argument('--search_mode', type=int, choices=[1, 2], help='Search mode: 1 for Piece Type, 2 for Starting Position.')
    parser.add_argument('--piece_type', type=str, help='Type of piece to search for (K)ing, (P)awn, etc. Required for piece type search mode')
    parser.add_argument('--starting_position', type=str, help='Starting position to search for (e.g., a1, b2). Required for starting position search mode')
    parser.add_argument('--piece_color', type=str, help='Color of the piece to search for (white or black). Required for piece type search mode')
    parser.add_argument('--timeout', type=int, default=-1, help='Timeout in seconds. Default is -1, meaning no timeout. Adding a timeout automatically saves a screenshot before exiting. Doesn\'t start until calculating is finished. Prints a countdown every quarter of the total timeout.')
    parser.add_argument('--board_display', type=str, default=board_display, help='Show board positions in (percent) or (totals)')
    args = parser.parse_args()

    if '--help' in vars(args):
        parser.print_help()
        return

    # Extract arguments
    pgnfile = args.pgnfile
    VERBOSE = args.verbose
    screen_width = args.screen_width
    screen_height = args.screen_height
    search_mode = args.search_mode
    piece_type = args.piece_type if search_mode == 1 else None
    starting_position = args.starting_position if search_mode == 2 else None
    piece_color = args.piece_color if search_mode == 1 and args.piece_color else None
    board_display = args.board_display
    timeout = args.timeout

    board_size = min(screen_width, screen_height)  # Use the smaller dimension
    square_size = board_size // 8

    # Validate piece_color if required
    if search_mode == 1 and piece_color is None:
        parser.error("--piece_color is required for search_mode 1")

    if search_mode == 2 and starting_position is None:
        parser.error("--a starting_position is required for search_mode 2")

    if parser.usage is not None and pgnfile is None:
        parser.error("You need to supply a filename if you're going to use arguments.")


    return {
        'pgnfile': pgnfile,
        'VERBOSE': VERBOSE,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'search_mode': search_mode,
        'piece_type': piece_type,
        'starting_position': starting_position,
        'piece_color': piece_color,
        'board_display': board_display,
        'timeout': timeout
    }



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
    # Strip the file extension to get the base filename
    base_filename, _ = os.path.splitext(file_path)
    suffix = 0
    file_name = f"{base_filename}.png"
    while os.path.exists(file_name):
        suffix += 1
        file_name = f"{base_filename}_{suffix}.png"
    pygame.image.save(screen, file_name)
    print(f"Screenshot saved as {file_name}")

# Function to draw chessboard
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
        # Center the text around the given position
        text_rect.center = position
    else:
        # Position text based on the top-left corner
        text_rect.topleft = position

    # Optional: Add shadow for better readability
    shadow_surface = font.render(text, True, (0, 0, 0))  # Black shadow
    shadow_position = (text_rect.x + 1, text_rect.y + 1)
    screen.blit(shadow_surface, shadow_position)
    
    # Render the actual text
    screen.blit(text_surface, text_rect.topleft)

    if update_screen_immediately:
        pygame.display.flip()

def render_counts(screen, total_positions_seen):
    global board_display
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
        if board_display == "percent":
            count_text = font.render(f"{(count / true_max * 100):.1f}%", True, WHITE)
        else:
            count_text = font.render(f"{count}", True, WHITE)
        text_rect = count_text.get_rect(center=circle_center)
        surface.blit(count_text, text_rect)
    
    screen.blit(surface, (0, 0))
    
    render_text(screen, "↑" + str(true_max), (square_size * 8 + 5, 10) , WHITE, 16)
    render_text(screen, "Top square's total!", (square_size * 8 + 5, 30) , WHITE, 12)
    render_text(screen, "(All %'s are based on the total)", (square_size * 8 + 5, 50) , WHITE, 12)
    render_text(screen, "Promotions still considered pawns", (square_size * 8 + 5, 70) , WHITE, 12)
    render_text(screen, "More options in commandline!", (square_size * 8 + 5, 90) , WHITE, 12)

    render_text(screen, "ESC = Exit", (square_size * 8 + 5, screen_height - 90), WHITE, 12)
    render_text(screen, "PRTSCRN screenshot path_1.png", (square_size * 8 + 5, screen_height - 60), WHITE, 12)
    render_text(screen, "ENTER = New Query", (square_size * 8 + 5, screen_height - 30), WHITE, 12)



# Function to process a single game
def process_single_game(game_data, starting_positions, total_positions_seen, xy_coords):
    positions = initialize_positions()
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

    game_moves = game.mainline_moves()

    if game_moves is None:
        print("No moves found in game! Processing next game.")
        return

    if game is None:
        print("No game entirely! Processing next game.")
        return

    board = game.board()
    positions_found = False
    for move in game_moves:
        from_square = str(move)[:2]
        to_square = str(move)[2:4]

        # Check if to_position is occupied and if so mark the other piece with an 'x' because it has been taken and isn't relevant to this part of the algo
        for path in positions:
            if path[-1] == to_square:
                path.append('x')

        # Check for en passant capture
        piece = board.piece_at(chess.parse_square(from_square))
        if piece and piece.piece_type == chess.PAWN:
            if abs(chess.parse_square(from_square) - chess.parse_square(to_square)) in [7, 9]:  # Diagonal move
                if (from_square[1] == '5' and to_square[1] == '6') or (from_square[1] == '4' and to_square[1] == '3'):
                    # If the destination square is empty, it's an en passant capture
                    if board.piece_at(chess.parse_square(to_square)) is None:
                        # Determine the captured pawn's square
                        if from_square[0] != to_square[0]:
                            captured_pawn_square = to_square[0] + from_square[1]
                            for path in positions:
                                if path[-1] == captured_pawn_square:
                                    path.append('x')
                                    break

        # Update the piece's position
        for path in positions:
            if path[-1] == from_square:
                path.append(to_square)
                positions_found = True
                break

        # Check for castling, the above code handles the king's movement already, without this the rook's movement gets lost.
        piece = board.piece_at(chess.parse_square(from_square))
        if piece and piece.piece_type == chess.KING:
            if from_square == 'e1' and to_square == 'g1':
                # Kingside castling for White
                for path in positions:
                    if path[-1] == 'h1':
                        path.append('f1')
            elif from_square == 'e1' and to_square == 'c1':
                # Queenside castling for White
                for path in positions:
                    if path[-1] == 'a1':
                        path.append('d1')
            elif from_square == 'e8' and to_square == 'g8':
                # Kingside castling for Black
                for path in positions:
                    if path[-1] == 'h8':
                        path.append('f8')
            elif from_square == 'e8' and to_square == 'c8':
                # Queenside castling for Black
                for path in positions:
                    if path[-1] == 'a8':
                        path.append('d8')



        board.push(move)

    if positions == [] or not positions_found:
        print("No positions found in game! Processing next game.")
        return

    if VERBOSE:
        print(positions)
        print('\n')


    
    # Iterate through positions to count occurrences
    for path in positions:
        if path[0] in starting_positions:
            # Check and remove 'x' if it's the last element
            if path[-1] == 'x':
                path.pop()  # Remove 'x' from the list

            for pos in path:
                
                if pos != 'x':
                    if VERBOSE:
                        print(pos)
                    if xy_coords:
                        x, y = chess_notation_to_indices(pos)
                        coord_str = f"{x},{y}"
                    else:
                        coord_str = pos
                    positions_seen[coord_str] += 1

    # Aggregate counts from positions_seen into total_positions_seen
    for coord, count in positions_seen.items():
        if VERBOSE:
            print(coord, count)
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
    
        games = content.split('\n[Event ')
        games = ['[Event ' + game for game in games if game]

    return games

def main():
    
    settings = parse_arguments()
    
    # for key, value in settings.items():
    #     print(f"{key}: {value}")
    
    file_path = ""
    if settings["pgnfile"] is None:
        file_path = input(f"Enter the path to the PGN file (default={file_path}): ")
    else:
        file_path = settings["pgnfile"]
    if file_path == "":
        file_path = "wexample.pgn"
    games = parse_pgn(file_path)
    xy_coords = True  # Don't set this to False as this will mess up some of the code with the rendering in pygame

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Chessboard")

    clock = pygame.time.Clock()
    running = True
    
    first_run = True

    input_mode = 'choose_mode'  # Start by asking for the mode (position or piece type)
    piece_type = ""
    piece_color = ""
    starting_position = ""
    stats = {}

    time = 0

    while running:
        screen.fill(LBLUE)  # White background
        draw_board(screen)

        if stats:
            render_counts(screen, stats)
            
        if (settings["timeout"] == -1):
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
                stats = analyze_games_by_piece_type(games, settings["piece_type"], settings["piece_color"], xy_coords)
            else:
                render_text(screen, "Calculating...", (screen_width / 2, screen_height / 2), WHITE, 70, True, True)
                stats = update_positions(games, [settings["starting_position"]], xy_coords)
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

                    if input_mode == 'choose_mode':
                        if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                            input_mode = 'piece_type'
                        elif event.key == pygame.K_2 or event.key == pygame.K_KP1:
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
                            stats = analyze_games_by_piece_type(games, piece_type, piece_color, xy_coords)
                        elif event.key == pygame.K_BACKSPACE:
                            piece_color = piece_color[:-1]
                        else:
                            piece_color += event.unicode

                    elif input_mode == 'position':
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            input_mode = 'analyze_position'
                            render_text(screen, "Calculating...", (screen_width / 2, screen_height / 2), WHITE, 70, True, True)
                            stats = update_positions(games, [starting_position], xy_coords)
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