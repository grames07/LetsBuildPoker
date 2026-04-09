import random

suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
numbers = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
deck = []

for suit in suits:
    for number in numbers:
        card = number + " of " + suit
        deck.append(card)

players = ["John", "James", "Jack", "Jodie"]

for player in range(len(players)): #need to figure out how to define number of players
    player_card_1 = random.choice(deck)
    deck.remove(player_card_1)
    player_card_2 = random.choice(deck)
    deck.remove(player_card_2)
    player_hand = player_card_1, player_card_2
    print(f"{players[player]}'s hand: {player_hand}")


