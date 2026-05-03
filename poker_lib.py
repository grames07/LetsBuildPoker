import random
from itertools import combinations

# ─── suit symbols ─────────────────────────────────────────────────────────────
C = '\u2663'   # ♣ Clubs
D = '\u2662'   # ♢ Diamonds
H = '\u2661'   # ♡ Hearts
S = '\u2660'   # ♠ Spades

# ─── card value lookup — defined once at module level ─────────────────────────
CARD_VALUES = {"2": 2,  "3": 3,  "4": 4,  "5": 5,  "6": 6, "7": 7,  "8": 8,  "9": 9,  "10": 10,"J": 11, "Q": 12, "K": 13, "A": 14}


def create_deck():
    suits   = [C, D, H, S]
    numbers = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"] # cards now look like "Q♡" or "10♣"
    return [f"{n}{s}" for s in suits for n in numbers]

def get_card_value(card):
    number = card[:-1]        # everything except the last character (the suit symbol)
    return CARD_VALUES[number]

def get_card_suit(card):
    return card[-1]           # the last character is always the suit symbol

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


def best_hand_rank(hole_cards, community_cards): # takes the player's 2 cards & 5 other cards, finds best hand
    all_cards = list(hole_cards) + list(community_cards) # complile all 7 cards into one list
    best = None # place to store best hand we find
    for combo in combinations(all_cards, 5): # check every combination of 5 cards from the 7 available
        rank = evaluate_five_card_hand(list(combo)) # use the evaluate_five_card_hand function on every 5 card combo
        if best is None or compare_hands(rank, best) == 1: # if it is the first check or if it is the best hand so far, save it
            best = rank # store our best hand found so far
    return best # when we've checked all combos, return the best hand we found


def compare_hands(hand1, hand2): # hands look like tuples: (rank_int, [sorted card values]) - need to compare ranks, than deal with tiebreakers
    hand1_wins = 1
    hand2_wins = -1
    tie = 0

    # CASE 1: one hand has a higher rank integer, so it wins immediately
    if hand1[0] > hand2[0]:
        return hand1_wins
    elif hand2[0] > hand1[0]:
        return hand2_wins

    # CASE 2: both hands have the same rank integer, so we need tiebreakers
    # save the rank and value lists so they are easier to work with below
    rank = hand1[0]   # the rank integer both hands share (e.g. 1 = One Pair)
    v1   = hand1[1]   # the sorted card values list for hand 1 (high to low)
    v2   = hand2[1]   # the sorted card values list for hand 2 (high to low)

    # ── Royal Flush (rank 9) ──────────────────────────────────────────────────
    if rank == 9:
        return tie   # two royal flushes are always a tie — only one exists per suit

    # ── Straight Flush (rank 8) ───────────────────────────────────────────────
    elif rank == 8:
        # the straight flush with the highest top card wins
        if v1[0] > v2[0]: return hand1_wins
        if v2[0] > v1[0]: return hand2_wins
        return tie   # identical straight flushes — split the pot

    # ── Four of a Kind (rank 7) ───────────────────────────────────────────────
    elif rank == 7:
        # step 1: find the value of the four matching cards in each hand
        quad1 = 0   # will store the repeated value for hand 1
        quad2 = 0   # will store the repeated value for hand 2
        for v in v1:
            if v1.count(v) == 4:   # if this value appears 4 times, it's the quad
                quad1 = v
                break   # found it — no need to keep looking
        for v in v2:
            if v2.count(v) == 4:
                quad2 = v
                break
        if quad1 > quad2: return hand1_wins
        if quad2 > quad1: return hand2_wins
        # step 2: quads are equal — compare the kicker (the one leftover card)
        kicker1 = 0
        kicker2 = 0
        for v in v1:
            if v1.count(v) == 1:   # the card that appears only once is the kicker
                kicker1 = v
                break
        for v in v2:
            if v2.count(v) == 1:
                kicker2 = v
                break
        if kicker1 > kicker2: return hand1_wins
        if kicker2 > kicker1: return hand2_wins
        return tie

    # ── Full House (rank 6) ───────────────────────────────────────────────────
    elif rank == 6:
        # step 1: compare the three-of-a-kind part first
        triple1 = 0
        triple2 = 0
        for v in v1:
            if v1.count(v) == 3:   # the value that appears 3 times
                triple1 = v
                break
        for v in v2:
            if v2.count(v) == 3:
                triple2 = v
                break
        if triple1 > triple2: return hand1_wins
        if triple2 > triple1: return hand2_wins
        # step 2: triples are equal — compare the pair part
        pair1 = 0
        pair2 = 0
        for v in v1:
            if v1.count(v) == 2:   # the value that appears 2 times
                pair1 = v
                break
        for v in v2:
            if v2.count(v) == 2:
                pair2 = v
                break
        if pair1 > pair2: return hand1_wins
        if pair2 > pair1: return hand2_wins
        return tie

    # ── Flush (rank 5) ────────────────────────────────────────────────────────
    elif rank == 5:
        # compare all 5 cards from highest to lowest until one hand wins
        for i in range(5):   # range(5) gives us indexes 0,1,2,3,4 — index 0 is the highest card
            if v1[i] > v2[i]: return hand1_wins
            if v2[i] > v1[i]: return hand2_wins
        return tie   # every card matched — split the pot

    # ── Straight (rank 4) ─────────────────────────────────────────────────────
    elif rank == 4:
        # the straight with the highest top card wins
        if v1[0] > v2[0]: return hand1_wins
        if v2[0] > v1[0]: return hand2_wins
        return tie   # identical straights — split the pot

    # ── Three of a Kind (rank 3) ──────────────────────────────────────────────
    elif rank == 3:
        # step 1: find and compare the triple value
        triple1 = 0
        triple2 = 0
        for v in v1:
            if v1.count(v) == 3:
                triple1 = v
                break
        for v in v2:
            if v2.count(v) == 3:
                triple2 = v
                break
        if triple1 > triple2: return hand1_wins
        if triple2 > triple1: return hand2_wins
        # step 2: triples are equal — collect and compare the two kicker cards
        kickers1 = []
        kickers2 = []
        for v in v1:
            if v != triple1:        # any card that isn't the triple is a kicker
                kickers1.append(v)
        for v in v2:
            if v != triple2:
                kickers2.append(v)
        kickers1.sort(reverse=True)   # sort kickers from high to low
        kickers2.sort(reverse=True)
        for i in range(len(kickers1)):   # compare kickers one by one
            if kickers1[i] > kickers2[i]: return hand1_wins
            if kickers2[i] > kickers1[i]: return hand2_wins
        return tie

    # ── Two Pair (rank 2) ─────────────────────────────────────────────────────
    elif rank == 2:
        # step 1: collect both pair values for each hand
        pairs1 = []
        pairs2 = []
        for v in v1:
            if v1.count(v) == 2 and v not in pairs1:   # appears twice and not already added
                pairs1.append(v)
        for v in v2:
            if v2.count(v) == 2 and v not in pairs2:
                pairs2.append(v)
        pairs1.sort(reverse=True)   # sort so the higher pair is at index 0
        pairs2.sort(reverse=True)
        # step 2: compare the higher pair first
        if pairs1[0] > pairs2[0]: return hand1_wins
        if pairs2[0] > pairs1[0]: return hand2_wins
        # step 3: higher pairs are equal — compare the lower pair
        if pairs1[1] > pairs2[1]: return hand1_wins
        if pairs2[1] > pairs1[1]: return hand2_wins
        # step 4: both pairs are equal — compare the kicker
        kicker1 = 0
        kicker2 = 0
        for v in v1:
            if v1.count(v) == 1:   # the one card that isn't part of a pair
                kicker1 = v
                break
        for v in v2:
            if v2.count(v) == 1:
                kicker2 = v
                break
        if kicker1 > kicker2: return hand1_wins
        if kicker2 > kicker1: return hand2_wins
        return tie

    # ── One Pair (rank 1) ─────────────────────────────────────────────────────
    elif rank == 1:
        # step 1: find and compare the pair value
        pair1 = 0
        pair2 = 0
        for v in v1:
            if v1.count(v) == 2:   # the value that appears twice is the pair
                pair1 = v
                break
        for v in v2:
            if v2.count(v) == 2:
                pair2 = v
                break
        if pair1 > pair2: return hand1_wins
        if pair2 > pair1: return hand2_wins
        # step 2: pairs are equal — collect and compare the three kicker cards
        kickers1 = []
        kickers2 = []
        for v in v1:
            if v != pair1:    # any card that isn't the pair is a kicker
                kickers1.append(v)
        for v in v2:
            if v != pair2:
                kickers2.append(v)
        kickers1.sort(reverse=True)   # sort kickers from high to low
        kickers2.sort(reverse=True)
        for i in range(len(kickers1)):   # compare kickers one by one
            if kickers1[i] > kickers2[i]: return hand1_wins
            if kickers2[i] > kickers1[i]: return hand2_wins
        return tie

    # ── High Card (rank 0) ────────────────────────────────────────────────────
    elif rank == 0:
        # neither player has any matching cards — just compare all 5 cards one by one
        # the player with the single highest card wins, working down through all 5 if needed
        for i in range(5):   # range(5) gives us indexes 0,1,2,3,4 — index 0 is the highest card
            if v1[i] > v2[i]: return hand1_wins   # hand 1's card at this position is higher
            if v2[i] > v1[i]: return hand2_wins   # hand 2's card at this position is higher
            # if they are equal, the loop continues to the next card down
        return tie   # all 5 cards were identical — split the pot

    return tie   # fallback safety net — should never actually be reached



# ─────────────────────────────────────────────────────────────────────────────
# BETTING FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def format_money(amount):
    """Format a money amount nicely for display.
    Whole numbers show as $10, decimals show as $10.50"""
    if amount == int(amount):      # check if the amount has no decimal part
        return f'${int(amount)}'   # display as a whole number e.g. $100
    else:
        return f'${amount:.2f}'    # display with 2 decimal places e.g. $10.50



def player_action(bank, current_bet=0):
    """Ask the current player what they want to do.
    If current_bet is 0, the player can fold, check, or raise.
    If current_bet is greater than 0, the player must fold, call, or raise.
    Returns the player's chosen action and the dollar amount (0 if no money involved)."""

    # decide which options to show based on whether there is a bet to match
    if current_bet == 0:
        options = ['fold', 'check', 'raise']              # no bet on the table — can check
        prompt  = '  Your move (fold / check / raise): '
    else:
        options = ['fold', 'call', 'raise']               # bet on the table — must call or raise to stay in
        prompt  = f'  Your move (fold / call {format_money(current_bet)} / raise): '

    while True:   # keep asking until the player gives a valid answer
        move = input(prompt).strip().lower()   # read the player's input, remove extra spaces, make lowercase

        if move not in options:
            print(f'  Invalid choice. Please choose: {" / ".join(options)}')   # remind them of valid options
            continue   # go back to the top of the loop and ask again

        if move == 'raise':
            while True:   # keep asking until the player gives a valid raise amount
                try:
                    amount = float(input('  Raise amount: $'))   # read the raise amount as a number
                    if amount <= 0:
                        print('  Raise amount must be more than zero. Try again.')      # must bet at least something
                    elif amount > bank:
                        print(f'  You only have {format_money(bank)}. You cannot bet more than that.')   # FIXED: was fmt(bank), now format_money(bank)
                    else:
                        return 'raise', amount   # valid raise — return the action and amount
                except ValueError:
                    print('  Please type a number.')   # they typed something that isn't a number

        elif move == 'call':
            actual_call = min(current_bet, bank)   # can't call more than the player actually has (all-in protection)
            return 'call', actual_call             # return the call action and the capped amount

        else:
            return move, 0   # fold or check — no money changes hands so amount is 0

