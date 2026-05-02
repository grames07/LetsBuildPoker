from socket32 import create_new_socket   # import our custom socket library
import random                             # used to shuffle the deck


HOST = '127.0.0.1'   # the server's IP address (localhost)
PORT = 65444          # the port the server is listening on

# ─────────────────────────────────────────────────────────────────────────────
# GAME VALUES — change these to adjust the game before running
# ─────────────────────────────────────────────────────────────────────────────

big_blind    = 0.50    # the big blind amount — Player 1 posts this every round
small_blind  = 0.25    # the small blind amount — Player 2 posts this every round
player1_bank = 20.00   # how much money Player 1 starts with
player2_bank = 20.00   # how much money Player 2 starts with
pot          = 0.00    # the pot starts empty at the beginning of the game

