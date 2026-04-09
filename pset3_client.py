### chap05/guess32.py
from socket32 import create_new_socket
import random

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65444        # The port used by the server

client_bank_account = 1000
server_bank_account = 1000




def main(): #this function will contain a single round of poker
    print('## Welcome to POKER! ##')

    with create_new_socket() as s:
        s.connect(HOST, PORT)

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

    client_move = input('Enter your move (fold, check, raise): ')



if __name__ == '__main__':
    main()
