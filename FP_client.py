from socket32 import create_new_socket   # import our custom socket library
import random                             # used to shuffle the deck


HOST = '127.0.0.1'   # the server's IP address (localhost)
PORT = 65444          # the port the server is listening on

# ─────────────────────────────────────────────────────────────────────────────
# CARD AND DECK FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def create_deck(): # I used AI to refine my original deck-building code
    suits   = ["Hearts", "Diamonds", "Clubs", "Spades"]
    numbers = ["2", "3", "4", "5", "6", "7", "8", "9",
               "10", "Jack", "Queen", "King", "Ace"]
    # combine every number with every suit to make 52 unique cards
    return [f"{n} of {s}" for s in suits for n in numbers]


def get_card_value(card):
    number = card.split(" of ")[0]   # grab the value from the card
    vals   = {"2":2,  "3":3,  "4":4,  "5":5,  "6":6,  "7":7,  "8":8, "9":9,  "10":10, "Jack":11, "Queen":12, "King":13, "Ace":14}
    return vals[number]


def get_card_suit(card):
    return card.split(" of ")[1]


# ─────────────────────────────────────────────────────────────────────────────
# HAND EVALUATION
# ─────────────────────────────────────────────────────────────────────────────

# maps hand rank integers to human-readable names
possible_hands = {0: "High Card", 1: "One Pair", 2: "Two Pair", 3: "Three of a Kind", 4: "Straight", 5: "Flush", 6: "Full House", 7: "Four of a Kind", 8: "Straight Flush", 9: "Royal Flush"}


def evaluate_five_card_hand(cards):

    # get numeric values of all 5 cards sorted highest to lowest
    values= sorted([get_card_value(c) for c in cards], reverse=True) # get value of each card, e.g. "Jack" → 11, sorted high to low
    suits = [get_card_suit(c) for c in cards]   # get suit of each card


    # determine hand rank using boulians (they are "true" if the criteria is met)

    is_royal_flush = values == [14, 13, 12, 11, 10] and len(set(suits)) == 1

    is_straight_flush = (len(set(values)) == 5) and (values[0]+values[1]+values[2]+values[3]+values[4] == 5*values[0]-10) and len(set(suits)) == 1 and not is_royal_flush

    is_four_of_kind = len(set(values)) == 2 and (values.count(values[0]) == 4 or values.count(values[1]) == 4)

    is_full_house = len(set(values)) == 2 and not is_four_of_kind  # if only 2 unique values and not four of a kind, must be full house

    is_flush = len(set(suits)) == 1 and not is_royal_flush and not is_straight_flush

    is_straight = (len(set(values)) == 5) and (values[0]+values[1]+values[2]+values[3]+values[4] == 5*values[0]-10) and not is_straight_flush and not is_royal_flush

    is_three_of_kind = len(set(values)) == 3 and (values.count(values[0]) == 3 or values.count(values[2]) == 3 or values.count(values[4]) == 3)  # 3 unique values, one appearing 3 times

    is_two_pair = len(set(values)) == 3 and not is_three_of_kind  # 3 unique values but no triple must be two pair

    is_one_pair = len(set(values)) == 4  # exactly 4 unique values means one pair

    # assign a rank integer to this hand based on the highest-ranking criteria met
    if is_royal_flush:
        return (9, values)
    elif is_straight_flush:
        return (8, values)
    elif is_four_of_kind:
        return (7, values)
    elif is_full_house:
        return (6, values)
    elif is_flush:
        return (5, values)
    elif is_straight:
        return (4, values)
    elif is_three_of_kind:
        return (3, values)
    elif is_two_pair:
        return (2, values)
    elif is_one_pair:
        return (1, values)
    else:
        return (0, values)


def best_hand_rank(hole_cards, community_cards): #use the evaluate_five_card_hand function to find the best 5-card hand from the 7 available cards (2 hole + 5 community)
    #need help here! I want to generate all combinations of 5 cards from the 7 available, evaluate each one, and return the highest rank

def compare_hands(hand1, hand2): # hands look like tuples: (rank_int, [sorted card values]) - need to compare ranks, than deal with tiebreakers
    hand1_wins = 1
    hand2_wins = -1
    tie = 0

    # CASE 1: one hand has a higher rank integer, so it wins immediately

    if hand1[0] > hand2[0]:
        return hand1_wins
    elif hand2[0] > hand1[0]:
        return hand2_wins

    # Case 2: both hands have the same rank integer, so we need to compare the sorted card values to break ties

    elif hand1[0] == hand2[0]:
        if hand1[0] == 0: # high card tie
            for i in range(1,5):
                if hand1[1][i] > hand2[1][i]:
                    return hand1_wins
                elif hand2[1][i] > hand1[1][i]:
                    return hand2_wins

    #need to finish this?



    else:
       return tie
        #help me out here!
