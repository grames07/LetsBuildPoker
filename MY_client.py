### chap05/guess32.py
from socket32 import create_new_socket
import random

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65444        # The port used by the server

client_bank_account = 1000
server_bank_account = 1000




def main(): # this function will contain a single round of poker
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

    current_pot = 0

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


    # client pre-flop action
    client_preflop = int(input('Enter your move (fold, check, raise): '))
    if client_preflop == 'fold':
        print('You folded. Round over.')
        return
    elif client_preflop == 'check':
        print('You checked.')
    elif client_preflop == 'raise':
        client_raise = int(input('Enter your raise amount: '))
        if client_raise > client_bank_account:
            print('You cannot bet more than your bank account. Please try again.')
            return
        else:
            client_bank_account -= client_raise
            current_pot += client_raise
        print(f"You raised: {client_raise}")

    # server pre-flop action
    s.sendall(str('Enter your move (fold, check, raise): '))






    server_bet =
    print(f"Server bets: {server_bet}")


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
