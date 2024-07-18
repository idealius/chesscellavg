# Intro

I have always been very curious to see what it means to take control of the center in a chess game in terms of bare piece percentages played there.
I've also been curious if certain board positions are just overall very bad for pieces statistically.
This is without considering any openings or defenses, which limits its usefulness, but since I couldn't find anything that did this, I made it.
I used ChatGPT for a lot of it (who doesn't, anymore, especially for Python) but I added quite a bit in a short amount of time.

If you need to find a large number of PGN games to mess with (besides your own) I included a myfile.pgn which is based on a few (5000+) Chess games.

I made it from the 9GB PGN file made in 2021 by this guy:
https://www.chess.com/forum/view/general/chess-pgn-database-over-9-million-games

I used a PowerShell -tail command to grab them because I couldn't find much to view a 9GB file on Windows.
You also have to save the file as UTF-8 afterwards as I believe it is UTF-16E

# Interface / Output

![what it looks like](myfile_3.png?raw=true "what it looks like")

![raw totals mode](myfile_2.png?raw=true "by piece type (pawns)")

![what it looks like](myfile_4.png?raw=true "what it looks like")

# Details

It has two main modes, one where you choose a piece type for a certain color on the board - specifically for Pawns, mostly, but works for other pieces too.
The totals calculated are somewhat confusing in that it not only totals up the positions a piece moves in a game, if it moves back over that position again, it adds that to the total, too. So in some cases you'll see weird things like totals less than 100% for the home positions. This is because some other board position gets played multiple times a game. For a very short one game analysis it's not uncommon to see 50% on the home squares.
I coded up a little utility called pyfilter.py which can be used to filter out PGN files for wins and losses by player name or color and output them. I'd rather have put them directly in the main .py file but it just seemed easier to make a separate utility. That said I did not add commandline options to the utility, yet.
It can also track movement totals / percentages by piece starting position using standard PGN notation.
It uses the chess python module as trying to decipher PGN notation with a computer from scratch is actually incredibly difficult for something like this - you would be surprised.
I added some commandline features so people can setup batch files to process a bunch and output screenshots - it shows percentages by default and I figured some people would prefer the totals so that's in there.

There's not much to say besides the picture, all of it is pretty self-explanatory in a user-friendly-ish way.

I suppose it would be better if it could track openings and lines alongside the %'s but I'm pretty sure there are other tools that already do that.

It might be useful for programming a simple chessbot or refining a more advanced one.

Use for commercial reasons or use for private reasons at your own risk keeping in mind the licenses of the imported libraries (pygame, chess)
