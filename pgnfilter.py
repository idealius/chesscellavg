import pygame
import chess
import chess.pgn
import io

# Initialize pygame
pygame.init()

# Function to parse PGN file and filter games
def parse_and_filter_pgn(file_path, player_name, result_filter):
    with open(file_path, 'r') as f:
        content = f.read()
    
    games = content.split('\n[Event')
    games = ['[Event' + game for game in games if game]


    filtered_games = []
    for game_data in games:
        
        game_stream = io.StringIO(game_data)
        game = chess.pgn.read_game(game_stream)
        if game:
            white_player = game.headers.get('White', '').strip().lower()
            black_player = game.headers.get('Black', '').strip().lower()
            result = game.headers.get('Result', '*')

            if player_name in [white_player, black_player]:
                if result_filter == 'win':
                    if (player_name == white_player and result == '1-0') or \
                       (player_name == black_player and result == '0-1'):
                        filtered_games.append(game_data)
                elif result_filter == 'loss':
                    if (player_name == white_player and result == '0-1') or \
                       (player_name == black_player and result == '1-0'):
                        filtered_games.append(game_data)
                elif result_filter == 'draw':
                    if result == '1/2-1/2':
                        filtered_games.append(game_data)
                elif result_filter == 'all':
                    filtered_games.append(game_data)
            elif player_name == "":
                if result_filter == 'win':
                    if (result == '1-0'):
                        filtered_games.append(game_data)
                elif result_filter == 'loss':
                    if (result == '0-1'):
                        filtered_games.append(game_data)
                elif result_filter == 'draw':
                    if result == '1/2-1/2':
                        filtered_games.append(game_data)
                elif result_filter == 'all':
                    filtered_games.append(game_data)
    
    return filtered_games

def save_filtered_pgn(filtered_games, save_file_name):
    with open(save_file_name, 'w') as f:
        for game_data in filtered_games:
            f.write(game_data)
            f.write('\n\n\n')

def main():
    file_path = input("Enter the path to the PGN file: ").strip().lower()
    if file_path == "":
        file_path = "example.pgn"
    
    player_name = input("Enter player name to filter games (leave blank to include all players): ").strip().lower()
    if player_name == "":
        print("Because no player name was chosen, wins will be considered 1-0 (white), losses 0-1 (black)")
    result_filter = input("Enter result filter (win/loss/draw/all): ").strip().lower()

    filtered_games = parse_and_filter_pgn(file_path, player_name, result_filter)

    if filtered_games:
        save_file_name = input("Enter the save file name for filtered games (include .pgn): ").strip()
        if not save_file_name:
            save_file_name = "filtered_games.pgn"

        save_filtered_pgn(filtered_games, save_file_name)
        print(f"Filtered games saved to '{save_file_name}'.")

    pygame.quit()

if __name__ == "__main__":
    main()
