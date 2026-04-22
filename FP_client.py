from socket32 import create_new_socket   # import our custom socket library
import random                             # used to shuffle the deck
from itertools import combinations        # used to find best 5-card hand from 7 cards
from collections import Counter           # used to count card values for hand evaluation

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
HAND_NAMES = {0: "High Card", 1: "One Pair", 2: "Two Pair", 3: "Three of a Kind", 4: "Straight", 5: "Flush", 6: "Full House", 7: "Four of a Kind", 8: "Straight Flush", 9: "Royal Flush"}


def evaluate_five_card_hand(cards):

    # get numeric values of all 5 cards sorted highest to lowest
    values  = sorted([get_card_value(c) for c in cards], reverse=True) # get value of each card, e.g. "Jack" → 11, sorted high to low
    suits = [get_card_suit(c) for c in cards]   # get suit of each card


    # determine hand rank using boulians (they are "true" if the criteria is met)

    is_royal_flush = values == [14, 13, 12, 11, 10] and len(set(suits)) == 1

    is_straight_flush = (len(set(values)) == 5) and (values[0]+values[1]+values[2]+values[3]+values[4] == 5*(values[0])-10) and len(set(suits)) == 1 and not is_royal_flush # 5 consecutive values, all same suit, but not royal flush

    is_four_of_kind = len(set(values)) == 2 and (values.count(values[0]) == 4 or values.count(values[1]) == 4) # if there are only 2 unique values and one of them occurs 4 times, it's four of a kind

    is_full_house = len(set(values)) == 2 and values.count(values[0]) == 3 and values.count(values[1]) == 2 or values.count(values[1]) == 3 and values.count(values[0]) == 2 # if there are only 2 unique values and one occurs 3 times and the other occurs 2 times, it's a full house

    is_flush = len(set(suits)) == 1 and not is_royal_flush and not is_straight_flush # all suits the same but not straight flush or royal flush

    is_straight = (len(set(values)) == 5) and (values[0]+values[1]+values[2]+values[3]+values[4] == 5*(values[0])-10) # sum of 5 consecutive numbers is 5 times the highest minus 10 (e.g. 10+9+8+7+6 = 5*10-10)

    is_three_of_kind = len(set(values)) == 3 and not is_full_house and not is_four_of_kind # if there are 3 unique values and it's not a full house or four of a kind, it must be three of a kind

    is_two_pair = len(set(values)) == 4 and not is_three_of_kind and not is_full_house and not is_four_of_kind # if there are 4 unique values and it's not three of a kind, full house, or four of a kind, it must be two pair

    is_high_card = not is_royal_flush and not is_straight_flush and not is_four_of_kind and not is_full_house and not is_flush and not is_straight and not is_three_of_kind and not is_two_pair # if it's none of the above, it's just a high card hand



    value_count = Counter(values) # count occurrences of each value
    counts = sorted(value_count.values(), reverse=True) # e.g. [3,2] = full house sort by frequency first, then by value — used for tiebreakers
    groups = sorted(value_count.keys(), key=lambda x: (value_count[x], x), reverse=True) # e.g. [10, 7] = three 10s and two 7s, so 10 is the first tiebreaker, then 7



def best_hand_rank(hole_cards, community_cards): #use the evaluate_five_card_hand function to find the best 5-card hand from the 7 available cards (2 hole + 5 community)


# ─────────────────────────────────────────────────────────────────────────────
# PLAYER INPUT
# ─────────────────────────────────────────────────────────────────────────────

def player_action(bank, current_bet=0):
    """Ask the current player for a betting decision.
    Returns (action_str, amount_int).
    current_bet > 0 means there is a bet on the table to match."""

    if current_bet == 0:
        # no bet to match — player may check instead of calling
        options = ['fold', 'check', 'raise']
        prompt  = '  Your move (fold / check / raise): '
    else:
        # there is a bet on the table — player must call or raise to stay in
        options = ['fold', 'call', 'raise']
        prompt  = f'  Your move (fold / call ${current_bet} / raise): '

    while True:   # keep asking until we get a valid input
        move = input(prompt).strip().lower()   # read input, remove whitespace, lowercase
        if move not in options:
            print(f'  Invalid move. Choose: {" / ".join(options)}')   # invalid — try again
            continue
        if move == 'raise':
            while True:   # keep asking until we get a valid raise amount
                try:
                    amt = int(input('  Raise amount: $'))   # read raise amount as integer
                    if amt <= 0:
                        print('  Amount must be positive.')         # must bet at least $1
                    elif amt > bank:
                        print(f'  You only have ${bank}. Try again.')   # can't bet more than bank
                    else:
                        return 'raise', amt   # valid raise
                except ValueError:
                    print('  Please enter a valid number.')   # non-integer input
        elif move == 'call':
            return 'call', min(current_bet, bank)   # cap call at what the player actually has
        else:
            return move, 0   # 'fold' or 'check' — no money changes hands


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    client_bank = 20   # Player 1 (client) starts with $20
    server_bank = 20   # Player 2 (server) starts with $20
    SMALL_BLIND = .25     # small blind posted by Player 2 each round
    BIG_BLIND   = .50     # big blind posted by Player 1 each round

    print('## Welcome to POKER! ##')

    with create_new_socket() as s:   # open socket, auto-closes when done
        s.connect(HOST, PORT)        # connect to the server

        # ── Protocol reference ───────────────────────────────────────────────
        # Every message from client to server starts with a tag:
        #
        #   DISPLAY:<msg>           → server prints msg,          replies OK
        #   HAND:<msg>              → server prints their hand,   replies OK
        #   BET:<bet>:<pot>:<sbank> → server makes a decision,    replies '<action> <amount>'
        #   CONTINUE                → new round starting,         replies OK
        #   GAME_OVER:<msg>         → server prints msg and exits
        # ────────────────────────────────────────────────────────────────────

        def display(msg):
            """Print msg on the client screen AND send it to the server so
            both screens show exactly the same game log."""
            print(f'  {msg}')              # print on client screen
            s.sendall(f'DISPLAY:{msg}')    # send to server to print the same thing
            s.recv()                        # wait for server to acknowledge with OK

        def betting_round(pot, cb, sb, street):
            """Run one full betting street (Pre-Flop / Flop / Turn / River).
            Player 1 (client) always acts first.
            Returns (new_pot, new_player1_bank, new_player2_bank, who_folded).
            who_folded is 'client', 'server', or None if nobody folded."""

            # show both players the street name and current pot
            display(f'── {street} Betting  |  Pot: ${pot} ──')
            display(f'Player 1 bank: ${cb}  |  Player 2 bank: ${sb}')

            c_act, c_amt = player_action(cb)   # ask Player 1 for their move

            # ── Player 1 folds ────────────────────────────────────────────────
            if c_act == 'fold':
                sb += pot   # Player 2 wins the pot when Player 1 folds
                display(f'Player 1 folds. Player 2 wins the pot of ${pot}!')
                return pot, cb, sb, 'client'   # return with folded='client'

            # ── Player 1 raises ───────────────────────────────────────────────
            elif c_act == 'raise':
                cb  -= c_amt   # deduct raise from Player 1's bank
                pot += c_amt   # add raise to the pot
                display(f'Player 1 raises ${c_amt}. Pot: ${pot}')
                # send BET so the server knows how much to match
                s.sendall(f'BET:{c_amt}:{pot}:{sb}')
                resp  = s.recv()           # server replies with '<action> <amount>'
                s_act = resp.split()[0]    # e.g. 'fold', 'call', or 'raise'
                s_amt = int(resp.split()[1])   # dollar amount (0 for fold/check)

                if s_act == 'fold':
                    cb += pot   # Player 1 wins the pot when Player 2 folds
                    display(f'Player 2 folds. Player 1 wins the pot of ${pot}!')
                    return pot, cb, sb, 'server'   # return with folded='server'

                elif s_act == 'call':
                    actual  = min(s_amt, sb)   # cap call at what Player 2 actually has
                    sb     -= actual           # deduct from Player 2's bank
                    pot    += actual           # add to pot
                    display(f'Player 2 calls ${actual}. Pot: ${pot}')

                elif s_act == 'raise':   # Player 2 re-raises — one re-raise allowed per street
                    sb  -= s_amt   # deduct re-raise from Player 2's bank
                    pot += s_amt   # add to pot
                    display(f'Player 2 re-raises ${s_amt}. Pot: ${pot}')
                    # Player 1 must now respond to the re-raise: call or fold
                    c_act2, _ = player_action(cb, current_bet=s_amt)
                    if c_act2 == 'fold':
                        sb += pot   # Player 2 wins the pot
                        display(f'Player 1 folds. Player 2 wins the pot of ${pot}!')
                        return pot, cb, sb, 'client'
                    else:   # Player 1 calls the re-raise
                        actual  = min(s_amt, cb)   # cap at what Player 1 has
                        cb     -= actual
                        pot    += actual
                        display(f'Player 1 calls ${actual}. Pot: ${pot}')

            # ── Player 1 checks ───────────────────────────────────────────────
            else:
                display(f'Player 1 checks.')
                # send BET with 0 so server knows there is no bet to match
                s.sendall(f'BET:0:{pot}:{sb}')
                resp  = s.recv()           # server replies with their action
                s_act = resp.split()[0]
                s_amt = int(resp.split()[1])

                if s_act == 'fold':
                    cb += pot   # Player 1 wins the pot when Player 2 folds
                    display(f'Player 2 folds. Player 1 wins the pot of ${pot}!')
                    return pot, cb, sb, 'server'

                elif s_act == 'check':
                    display(f'Player 2 checks.')   # both checked — move to next street

                elif s_act == 'raise':
                    sb  -= s_amt   # deduct raise from Player 2's bank
                    pot += s_amt   # add to pot
                    display(f'Player 2 raises ${s_amt}. Pot: ${pot}')
                    # Player 1 must now respond to Player 2's raise
                    c_act2, _ = player_action(cb, current_bet=s_amt)
                    if c_act2 == 'fold':
                        sb += pot   # Player 2 wins the pot
                        display(f'Player 1 folds. Player 2 wins the pot of ${pot}!')
                        return pot, cb, sb, 'client'
                    else:   # Player 1 calls the raise
                        actual  = min(s_amt, cb)   # cap at what Player 1 has
                        cb     -= actual
                        pot    += actual
                        display(f'Player 1 calls ${actual}. Pot: ${pot}')

            return pot, cb, sb, None   # nobody folded this street

        # ═════════════════════════════════════════════════════════════════════
        # GAME LOOP — one iteration = one full hand of poker
        # ═════════════════════════════════════════════════════════════════════
        while True:

            # check if either player is too broke to post their blind
            if client_bank < BIG_BLIND:
                display(f'Player 1 cannot cover the big blind. Player 2 wins!')
                s.sendall('GAME_OVER:Game over.')
                break   # end the game
            if server_bank < SMALL_BLIND:
                display(f'Player 2 cannot cover the small blind. Player 1 wins!')
                s.sendall('GAME_OVER:Game over.')
                break   # end the game

            # show both players a divider with current bank totals
            display(f'{"═"*46}')
            display(f'Player 1 bank: ${client_bank}  │  Player 2 bank: ${server_bank}')
            display(f'{"═"*46}')

            deck      = create_deck()    # build a fresh 52-card deck each hand
            random.shuffle(deck)         # shuffle the deck
            pot       = 0                # reset pot for this hand
            community = []               # community cards start empty each hand

            # ── Post blinds ──────────────────────────────────────────────────
            client_bank -= BIG_BLIND     # Player 1 posts the big blind
            server_bank -= SMALL_BLIND   # Player 2 posts the small blind
            pot          = BIG_BLIND + SMALL_BLIND   # pot starts with both blinds
            display(f'Blinds — Player 1: ${BIG_BLIND} (big)  |  Player 2: ${SMALL_BLIND} (small)  |  Pot: ${pot}')

            # ── Deal hole cards (private — each player only sees their own) ───
            server_hand = [deck.pop(), deck.pop()]   # deal 2 private cards to Player 2
            client_hand = [deck.pop(), deck.pop()]   # deal 2 private cards to Player 1
            # send Player 2 their hand via HAND tag (not displayed on client screen)
            s.sendall(f'HAND:Player 2 (You): {server_hand[0]},  {server_hand[1]}')
            s.recv()   # wait for OK
            # show Player 1 their own hand directly (not sent to server)
            print(f'  Player 1 (You): {client_hand[0]},  {client_hand[1]}')

            # ── Pre-Flop ─────────────────────────────────────────────────────
            # betting round before any community cards are revealed
            pot, client_bank, server_bank, folded = \
                betting_round(pot, client_bank, server_bank, 'Pre-Flop')
            if folded:   # someone folded — skip the rest of this hand
                display(f'Player 1 bank: ${client_bank}  │  Player 2 bank: ${server_bank}')
                again = input('\n  Play another round? (yes / no): ').strip().lower()
                if again != 'yes':
                    s.sendall('GAME_OVER:Opponent left. Thanks for playing!')
                    break
                s.sendall('CONTINUE')   # tell server a new hand is starting
                s.recv()                # wait for OK
                continue                # jump back to top of game loop

            # ── Flop ─────────────────────────────────────────────────────────
            flop = [deck.pop(), deck.pop(), deck.pop()]   # deal 3 community cards
            community.extend(flop)   # add flop to community card list
            display(f'[Flop]  {", ".join(flop)}')   # show flop to both players

            pot, client_bank, server_bank, folded = \
                betting_round(pot, client_bank, server_bank, 'Flop')
            if folded:
                display(f'Player 1 bank: ${client_bank}  │  Player 2 bank: ${server_bank}')
                again = input('\n  Play another round? (yes / no): ').strip().lower()
                if again != 'yes':
                    s.sendall('GAME_OVER:Opponent left. Thanks for playing!')
                    break
                s.sendall('CONTINUE')
                s.recv()
                continue

            # ── Turn ─────────────────────────────────────────────────────────
            turn = deck.pop()        # deal the 4th community card
            community.append(turn)   # add turn to community card list
            display(f'[Turn]  {turn}')   # show turn to both players

            pot, client_bank, server_bank, folded = \
                betting_round(pot, client_bank, server_bank, 'Turn')
            if folded:
                display(f'Player 1 bank: ${client_bank}  │  Player 2 bank: ${server_bank}')
                again = input('\n  Play another round? (yes / no): ').strip().lower()
                if again != 'yes':
                    s.sendall('GAME_OVER:Opponent left. Thanks for playing!')
                    break
                s.sendall('CONTINUE')
                s.recv()
                continue

            # ── River ────────────────────────────────────────────────────────
            river = deck.pop()        # deal the 5th and final community card
            community.append(river)   # add river to community card list
            display(f'[River]  {river}')   # show river to both players

            pot, client_bank, server_bank, folded = \
                betting_round(pot, client_bank, server_bank, 'River')
            if folded:
                display(f'Player 1 bank: ${client_bank}  │  Player 2 bank: ${server_bank}')
                again = input('\n  Play another round? (yes / no): ').strip().lower()
                if again != 'yes':
                    s.sendall('GAME_OVER:Opponent left. Thanks for playing!')
                    break
                s.sendall('CONTINUE')
                s.recv()
                continue

            # ── Showdown — evaluate both hands and award pot ──────────────────
            c_rank = best_hand_rank(client_hand, community)   # best 5-card rank for Player 1
            s_rank = best_hand_rank(server_hand, community)   # best 5-card rank for Player 2
            c_name = HAND_NAMES[c_rank[0]]   # human-readable name for Player 1's hand
            s_name = HAND_NAMES[s_rank[0]]   # human-readable name for Player 2's hand

            # reveal all cards and hand rankings to both players
            display(f'── SHOWDOWN ──')
            display(f'Community  : {", ".join(community)}')
            display(f'Player 1   : {client_hand[0]}, {client_hand[1]}  →  {c_name}')
            display(f'Player 2   : {server_hand[0]}, {server_hand[1]}  →  {s_name}')

            # determine winner and award pot
            if c_rank > s_rank:
                client_bank += pot   # Player 1 wins
                result = f'Player 1 wins the pot of ${pot}!  ({c_name} beats {s_name})'
            elif s_rank > c_rank:
                server_bank += pot   # Player 2 wins
                result = f'Player 2 wins the pot of ${pot}!  ({s_name} beats {c_name})'
            else:
                split        = pot // 2   # split the pot evenly on a tie
                client_bank += split
                server_bank += split
                result = f'Tie! Pot split — each player receives ${split}.'

            # show the result and updated banks to both players
            display(result)
            display(f'Player 1 bank: ${client_bank}  │  Player 2 bank: ${server_bank}')

            again = input('\n  Play another round? (yes / no): ').strip().lower()
            if again != 'yes':
                s.sendall('GAME_OVER:Opponent left. Thanks for playing!')
                break
            s.sendall('CONTINUE')   # tell server another round is starting
            s.recv()                # wait for OK

        print('\nThanks for playing!')   # shown when the game loop ends


if __name__ == '__main__':
    main()
