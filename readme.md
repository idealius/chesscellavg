# Intro

I have always been very curious to see what it means to take control of the center in a chess game in terms of bare piece percentages played there.
I've also been curious if certain board positions are just overall very bad for pieces statistically.
This is without considering any openings or defenses, which limits its usefulness, but since I couldn't find anything that did this, I made it.
I used ChatGPT for a lot of it (who doesn't, anymore, especially for Python) but I added quite a bit in a short amount of time.

If you need to find a large number of PGN games to mess with (besides your own) I included a myfile.pgn which is based on a few (4000+) Chess games. Varying ELO, many from Titled Tuesday, other actual tournaments mostly around the 2000 range but some are a bit lower.

I made it from the 9GB PGN file made in 2021 by this guy:
https://www.chess.com/forum/view/general/chess-pgn-database-over-9-million-games

I used a PowerShell -tail command to grab them because I couldn't find much to view a 9GB file on Windows.
You also have to save the file as UTF-8 afterwards as I believe it is UTF-16E

You're probably better off just downloading one of these then filtering it with the included .py file:
https://theweekinchess.com/twic

# Major Changes:

8/2/2024 Trying Claude Sonnet for the first time, because of the advanced number of tokens compared to ChatGPT4: Added threatening opponent and threatened by toggles. This greatly increases calculation time for large PGN files with a large number of games: 100k+, etc.

# Bonus data just for showing up:

Looking at white GM Wins, literally thousands and thousands of games over the last 12 years, black is positions, read is threatened by, green is threatening opponent (P) is pawns, (Qd1) is the white queen:

![gamesofgms_white_wins_queen_positions.png](pngs/gamesofgms_white_wins_queen_positions.png?raw=true "gamesofgms_white_wins_queen_positions.png")

![gamesofgms_white_wins_queen_threatened_by.png](pngs/gamesofgms_white_wins_queen_threatened_by.png?raw=true "gamesofgms_white_wins_queen_threatened_by.png")

![gamesofgms_white_wins_queen_threatening.png](pngs/gamesofgms_white_wins_queen_threatening.png?raw=true "gamesofgms_white_wins_queen_threatening.png")

![gamesofgms_white_wins_pawns_positions.png](pngs/gamesofgms_white_wins_pawns_positions.png?raw=true "gamesofgms_white_wins_pawns_positions.png")

![gamesofgms_white_wins_pawns_threatened_by.png](pngs/gamesofgms_white_wins_pawns_threatened_by.png?raw=true "gamesofgms_white_wins_pawns_threatened_by.png")

![gamesofgms_white_pawns_wins_threatening.png](pngs/gamesofgms_white_pawns_wins_threatening.png?raw=true "gamesofgms_white_pawns_wins_threatening.png")

Here is an example command line to get fullscreen (it defaults to 800 x 600)
```
python chesscellavg.py --pgnfile myfile.pgn --screen_width 1920 --screen_height 1080 --search_mode 1 --piece_type P --piece_color white
```

Here is an example command line to split up a PGN file by wins / losses / draws (you can also just run either of these and it takes user input)
```
python pgnfilter.py --input myfile.pgn --output myfile2 --process split --color white
```
# Details

It has two main modes, one where you choose a piece type for a certain color on the board - specifically for Pawns, mostly, but works for other pieces too, then it totals all the positions in games, across multiple games, for each board tile. It can also do this for one piece at a time, based on starting position.

The totals calculated are somewhat confusing in that it not only totals up the positions a piece moves in a game, if it moves back over that position again, it adds that to the total, too. Then it bases the % on the top held position on the board. So in some cases you'll see weird things like totals less than 100% for the home positions. This is because some other board position gets played multiple times a game. For a very short one game analysis it's not uncommon to see 50% on the home squares.

I tested it mostly with Lichess games, but I just tried it with some Chess.com games and it appears to work even with time information embedded in the moves.

I coded up a little utility called pyfilter.py which can be used to filter out PGN files for wins and losses by player name or color and output them. I'd rather have put them directly in the main .py file but it just seemed easier to make a separate utility. 

They both use the chess python module as trying to decipher PGN notation with a computer from scratch is actually incredibly difficult for something like this - you would be surprised. Like, incredibly difficult. The people talking about PGN notation being a bigger of a hassle than it's actually worth ... are not lying.

I added some commandline features so people can setup batch files to process a bunch and output screenshots - it shows percentages by default and I figured some people would prefer the totals so that's in there.

There's not much to say besides the picture, all of it is pretty self-explanatory in a user-friendly-ish way.

I suppose it would be better if it could track openings and lines alongside the %'s but I'm pretty sure there are other tools that already do that.

It might be useful for programming a simple chessbot or refining a more advanced one.

Use for commercial reasons or use for private reasons at your own risk keeping in mind the licenses of the imported libraries (pygame, chess)


