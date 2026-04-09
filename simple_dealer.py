suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
numbers = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
deck = []

for suit in suits:
    for number in numbers:
        card = number + " of " + suit
        deck.append(card)

print(deck)

for player in number_of_players: #need to figure out how to define number of players
    player_hand = 
