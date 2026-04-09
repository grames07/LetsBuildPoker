### chap05/guess32.py
from socket32 import create_new_socket
import random

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65444        # The port used by the server

moves = ['rock','paper','scissors']



def main(): #this function will contain a single round of poker
    print('## Welcome to POKER! ##')


###########################################################################################################
###########################################################################################################

    # create a deck of cards to be used for the game
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    numbers = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
    deck = []

    for suit in suits:
        for number in numbers:
            card = number + " of " + suit
            deck.append(card)


    # deal to the server
    server_card_1 = random.choice(deck)
    deck.remove(server_card_1)
    server_card_2 = random.choice(deck)
    deck.remove(server_card_2)
    server_hand = server_card_1, server_card_2
    server_hand_message=f"Your hand: {server_hand}"
    s.sendall(str(server_hand_message))

    # deal to the client
    client_card_1 = random.choice(deck)
    deck.remove(client_card_1)
    client_card_2 = random.choice(deck)
    deck.remove(client_card_2)
    client_hand = client_card_1, client_card_2
    client_hand_message=f"Your hand: {client_hand}"
    print(client_hand_message)

    # deal the flop
    flop = random.sample(deck, 3)
    for card in flop:
        deck.remove(card)
    flop_message = f"The flop: {flop}"
    s.sendall(str(flop_message))
    print(flop_message)
    
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
