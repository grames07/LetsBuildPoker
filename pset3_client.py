### chap05/guess32.py
from socket32 import create_new_socket
import random

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65444        # The port used by the server

moves = ['rock','paper','scissors']



def main(): #this function will contain a single round of poker
    print('## Welcome to POKER! ##')
    moves = ['rock','paper','scissors']
    cwin_counter = 0
    swin_counter = 0
    match_counter = 0
    # print(f'DEBUG: The secret number is {secret}')
    with create_new_socket() as s:
        s.connect(HOST, PORT)

        while True:   # our game loop

            # Grab the player's guess
            while True:
                    client_move = player_choice()
                    s.sendall(str(client_move))
                    server_move = s.recv()
                    break

###################################################################################################################
################################################################################################################
            #CREATING A MESSAGE TO BE DISPLAYED AT SERVER

            server_message = (f'You: {server_move}   Opponent: {client_move}' + '\n')

            #add message to the latest round:
            if server_move==client_move:
                server_message += "It's a tie!"

            elif (server_move == 'rock' and client_move == 'paper') or  (server_move == 'paper' and client_move == 'scissors') or (server_move == 'scissors' and client_move == 'rock'):
                server_message += 'You lose!'
                cwin_counter += 1
                match_counter += 1

            else:
                server_message += 'You win!'
                swin_counter += 1
                match_counter += 1

            #INSERT SOMETHING HERE THAT MAKES IT BREAK OR REPEAT DEPENDING ON NUMBER OF WINS
            if cwin_counter == 3 or swin_counter == 3:
                server_message += ('\n' + f'rounds = {match_counter}' + f'   wins = {swin_counter}' + f'   losses = {cwin_counter}' + '\n')
                if cwin_counter > swin_counter:
                    server_message += ("You lost the match!")
                if cwin_counter < swin_counter:
                    server_message += ("You won the match!")

            s.sendall(str(server_message))

######################################################################################################################
            #BELOW IS THE CLIENT SIDE DISPLAY

            print(f'You: {client_move}   Opponent: {server_move}')

            if server_move==client_move.lower():
                print("It's a tie!")

            elif (server_move == 'rock' and client_move == 'paper') or  (server_move == 'paper' and client_move == 'scissors') or (server_move == 'scissors' and client_move == 'rock'):
                print('You win!')


            else:
                print('You lose!')


            #INSERT SOMETHING HERE THAT MAKES IT BREAK OR REPEAT DEPENDING ON NUMBER OF WINS
            if cwin_counter == 3 or swin_counter == 3:
                s.sendall(str())
                print(f'rounds = {match_counter}' + f'   wins = {cwin_counter}' + f'   losses = {swin_counter}')
                if cwin_counter > swin_counter:
                    print("You won the match!")
                if cwin_counter < swin_counter:
                    print("You lost the match!")
                break



if __name__ == '__main__':
    main()
