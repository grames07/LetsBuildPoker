from socket32 import create_new_socket   # import our custom socket library
import random                             # used to shuffle the deck
from itertools import combinations        # used to find best 5-card hand from 7 cards
from collections import Counter           # used to count card values for hand evaluation

HOST = '127.0.0.1'   # the server's IP address (localhost)
PORT = 65444          # the port the server is listening on

# ─────────────────────────────────────────────────────────────────────────────
# CARD AND DECK HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def create_deck():
    """Build and return a fresh 52-card deck as a list of strings."""
    suits   = ["Hearts", "Diamonds", "Clubs", "Spades"]    # the four suits
    numbers = ["2", "3", "4", "5", "6", "7", "8", "9",    # card face values
               "10", "Jack", "Queen", "King", "Ace"]
    # combine every number with every suit to make 52 unique cards
    return [f"{n} of {s}" for s in suits for n in numbers]


def get_card_value(card):
    """Return the numeric value (2–14) of a card string like '10 of Hearts'."""
    number = card.split(" of ")[0]    # grab the face value from the card string
    vals   = {                        # map face values to integers
        "2":2,  "3":3,  "4":4,  "5":5,  "6":6,  "7":7,  "8":8,
        "9":9,  "10":10, "Jack":11, "Queen":12, "King":13, "Ace":14
    }
    return vals[number]   # return the numeric value


def get_card_suit(card):
    """Return the suit string from a card like '10 of Hearts' → 'Hearts'."""
    return card.split(" of ")[1]   # everything after ' of ' is the suit


# ─────────────────────────────────────────────────────────────────────────────
# HAND EVALUATION
# ─────────────────────────────────────────────────────────────────────────────

# dictionary mapping hand rank integers to human-readable names
HAND_NAMES = {
    0: "High Card",        1: "One Pair",
    2: "Two Pair",         3: "Three of a Kind",
    4: "Straight",         5: "Flush",
    6: "Full House",       7: "Four of a Kind",
    8: "Straight Flush"
}


def evaluate_five_card_hand(cards):
    """Evaluate a 5-card poker hand.
    Returns (rank_int, tiebreaker_list) — higher tuple means better hand."""

    # get numeric values of all 5 cards, sorted highest to lowest
    vals  = sorted([get_card_value(c) for c in cards], reverse=True)
    # get the suit of each card
    suits = [get_card_suit(c) for c in cards]

    # a flush is when all 5 cards share the same suit
    is_flush    = len(set(suits)) == 1
    # a straight is 5 consecutive values with no duplicates
    is_straight = (len(set(vals)) == 5) and (vals[0] - vals[4] == 4)

    # special case: A-2-3-4-5 "wheel" straight (ace plays low)
    if set(vals) == {14, 2, 3, 4, 5}:
        is_straight = True
        vals        = [5, 4, 3, 2, 1]   # re-order so ace is treated as 1

    vc     = Counter(vals)                              # count how many of each value we have
    counts = sorted(vc.values(), reverse=True)          # e.g. [3,2] = full house, [4,1] = quads
    # sort cards by how often they appear first, then by card value (for tiebreakers)
    groups = sorted(vc.keys(), key=lambda x: (vc[x], x), reverse=True)

    # return (rank, tiebreaker) — tuples compare element by element in Python
    if   is_straight and is_flush: return (8, vals)   # straight flush
    elif counts[0] == 4:           return (7, groups) # four of a kind
    elif counts == [3, 2]:         return (6, groups) # full house
    elif is_flush:                 return (5, vals)   # flush
    elif is_straight:              return (4, vals)   # straight
    elif counts[0] == 3:           return (3, groups) # three of a kind
    elif counts[:2] == [2, 2]:     return (2, groups) # two pair
    elif counts[0] == 2:           return (1, groups) # one pair
    else:                          return (0, vals)   # high card


def best_hand_rank(hole_cards, community_cards):
    """Find the best 5-card hand rank from all 7 available cards
    (2 hole cards + 5 community cards).
    Tries every possible 5-card combination and returns the highest rank."""
    all_cards = list(hole_cards) + list(community_cards)   # combine hole and community cards
    # evaluate all possible 5-card combos and return the best one
    return max(evaluate_five_card_hand(list(combo))
               for combo in combinations(all_cards, 5))


# ─────────────────────────────────────────────────────────────────────────────
# PLAYER INPUT  —  also imported by the server as  rlib.player_action()
# ─────────────────────────────────────────────────────────────────────────────

def player_action(bank, current_bet=0):
    """Ask the current player for a betting decision.
    Returns (action_str, amount_int).
    action_str is one of: 'fold', 'check', 'call', 'raise'
    current_bet > 0 means the player must call or raise to stay in.
    """
    if current_bet == 0:
        # no bet to match — player can check instead of calling
        options = ['fold', 'check', 'raise']
        prompt  = '  Your move (fold / check / raise): '
    else:
        # there is a bet on the table — player must call or raise to stay in
        options = ['fold', 'call', 'raise']
        prompt  = f'  Your move (fold / call ${current_bet} / raise): '

    while True:   # keep asking until we get a valid move
        move = input(prompt).strip().lower()   # read input, remove whitespace, lowercase
        if move not in options:
            print(f'  Invalid move. Choose: {" / ".join(options)}')   # prompt again
            continue
        if move == 'raise':
            while True:   # keep asking until we get a valid raise amount
                try:
                    amt = int(input('  Raise amount: $'))   # read raise amount
                    if amt <= 0:
                        print('  Amount must be positive.')        # must be at least $1
                    elif amt > bank:
                        print(f'  You only have ${bank}. Try again.')   # can't bet more than you have
                    else:
                        return 'raise', amt   # valid raise — return action and amount
                except ValueError:
                    print('  Please enter a valid number.')   # non-integer input
        elif move == 'call':
            return 'call', min(current_bet, bank)   # can't call more than you have (all-in cap)
        else:
            return move, 0   # 'fold' or 'check' — no money involved


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    client_bank = 1000   # client starts with $1000
    server_bank = 1000   # server starts with $1000
    SMALL_BLIND = 25     # small blind amount posted by the server each round
    BIG_BLIND   = 50     # big blind amount posted by the client each round

    print('## Welcome to POKER! ##')

    with create_new_socket() as s:    # open a socket, auto-close when done
        s.connect(HOST, PORT)         # connect to the server

        # ── Protocol reference ───────────────────────────────────────────────
        # Every message sent from client to server starts with a tag so the
        # server knows what to do with it:
        #
        #   INFO:<msg>                       server prints msg,      replies OK
        #   HAND:<msg>                       server prints hand,     replies OK
        #   COMMUNITY:<msg>                  server prints cards,    replies OK
        #   SHOWDOWN:<msg>                   server prints reveal,   replies OK
        #   RESULT:<msg>                     server prints result,   replies OK
        #   BET:<bet>:<pot>:<sbank>:<msg>    server makes a decision,
        #                                    replies '<action> <amount>'
        #   CONTINUE                         start next round,       replies OK
        #   GAME_OVER:<msg>                  server prints and exits
        # ────────────────────────────────────────────────────────────────────

        def betting_round(pot, cb, sb, street):
            """Run one full betting street (Pre-Flop, Flop, Turn, or River).
            The client always acts first.
            Returns (new_pot, new_client_bank, new_server_bank, who_folded).
            who_folded is 'client', 'server', or None if nobody folded.
            """
            print(f'\n  ── {street} Betting  (Pot: ${pot}) ──')

            # tell the server what street we're on and show their current bank
            s.sendall(f'INFO:{street} betting begins | Pot: ${pot} | Your bank: ${sb}')
            s.recv()   # wait for server to acknowledge with 'OK'

            # show the client their current situation
            print(f'  Pot: ${pot} | Your bank: ${cb}')
            c_act, c_amt = player_action(cb)   # ask the client for their move

            # ── Client folds ─────────────────────────────────────────────────
            if c_act == 'fold':
                sb += pot   # server wins the pot when client folds
                print(f'  You folded. Opponent wins the pot of ${pot}.')
                # tell the server they won
                s.sendall(f'RESULT:Opponent folded. You win the pot of ${pot}!')
                s.recv()   # wait for OK
                return pot, cb, sb, 'client'   # return with folded='client'

            # ── Client raises ─────────────────────────────────────────────────
            if c_act == 'raise':
                cb  -= c_amt    # deduct raise from client's bank
                pot += c_amt    # add raise to the pot
                print(f'  You raised ${c_amt}. Pot: ${pot}')
                # send a BET message so the server knows how much to match
                s.sendall(f'BET:{c_amt}:{pot}:{sb}:Opponent raised ${c_amt}. Pot: ${pot}')
                resp  = s.recv()           # server replies with '<action> <amount>'
                s_act = resp.split()[0]    # e.g. 'fold', 'call', or 'raise'
                s_amt = int(resp.split()[1])   # the dollar amount (0 for fold/check)

                if s_act == 'fold':
                    cb += pot   # client wins the pot when server folds
                    print(f'  Opponent folded! You win the pot of ${pot}.')
                    s.sendall(f'RESULT:You folded. Opponent wins the pot of ${pot}.')
                    s.recv()   # wait for OK
                    return pot, cb, sb, 'server'   # return with folded='server'

                elif s_act == 'call':
                    actual  = min(s_amt, sb)   # cap at what the server actually has
                    sb     -= actual           # deduct call from server's bank
                    pot    += actual           # add call to the pot
                    print(f'  Opponent called ${actual}. Pot: ${pot}')
                    s.sendall(f'INFO:You called ${actual}. Pot: ${pot}')
                    s.recv()   # wait for OK

                elif s_act == 'raise':   # server re-raises — one re-raise allowed per street
                    sb  -= s_amt    # deduct re-raise from server's bank
                    pot += s_amt    # add re-raise to the pot
                    print(f'  Opponent re-raised ${s_amt}. Pot: ${pot}')
                    s.sendall(f'INFO:You re-raised ${s_amt}. Pot: ${pot}')
                    s.recv()   # wait for OK
                    # now the client must respond to the re-raise: call or fold
                    print(f'  Pot: ${pot} | Your bank: ${cb}')
                    c_act2, _ = player_action(cb, current_bet=s_amt)   # ask client again
                    if c_act2 == 'fold':
                        sb += pot   # server wins the pot
                        print(f'  You folded. Opponent wins the pot of ${pot}.')
                        s.sendall(f'RESULT:Opponent folded. You win the pot of ${pot}!')
                        s.recv()   # wait for OK
                        return pot, cb, sb, 'client'
                    else:   # client calls the re-raise
                        actual  = min(s_amt, cb)   # cap at what client has
                        cb     -= actual            # deduct call from client's bank
                        pot    += actual            # add to pot
                        print(f'  You called ${actual}. Pot: ${pot}')
                        s.sendall(f'INFO:Opponent called ${actual}. Pot: ${pot}')
                        s.recv()   # wait for OK

            # ── Client checks ─────────────────────────────────────────────────
            else:
                print('  You checked.')
                # send BET with amount 0 so server knows client checked
                s.sendall(f'BET:0:{pot}:{sb}:Opponent checked. Pot: ${pot}')
                resp  = s.recv()           # server replies with their action
                s_act = resp.split()[0]
                s_amt = int(resp.split()[1])

                if s_act == 'fold':
                    cb += pot   # client wins the pot
                    print(f'  Opponent folded! You win the pot of ${pot}.')
                    s.sendall(f'RESULT:You folded. Opponent wins the pot of ${pot}.')
                    s.recv()   # wait for OK
                    return pot, cb, sb, 'server'

                elif s_act == 'check':
                    print('  Opponent checked.')   # both checked — move to next street
                    s.sendall(f'INFO:Both players checked. Pot: ${pot}')
                    s.recv()   # wait for OK

                elif s_act == 'raise':
                    sb  -= s_amt    # deduct raise from server's bank
                    pot += s_amt    # add raise to pot
                    print(f'  Opponent raised ${s_amt}. Pot: ${pot}')
                    s.sendall(f'INFO:You raised ${s_amt}. Pot: ${pot}')
                    s.recv()   # wait for OK
                    # client must now respond to the server's raise
                    print(f'  Pot: ${pot} | Your bank: ${cb}')
                    c_act2, _ = player_action(cb, current_bet=s_amt)   # ask client again
                    if c_act2 == 'fold':
                        sb += pot   # server wins the pot
                        print(f'  You folded. Opponent wins the pot of ${pot}.')
                        s.sendall(f'RESULT:Opponent folded. You win the pot of ${pot}!')
                        s.recv()   # wait for OK
                        return pot, cb, sb, 'client'
                    else:   # client calls the raise
                        actual  = min(s_amt, cb)   # cap at what client has
                        cb     -= actual            # deduct from client's bank
                        pot    += actual            # add to pot
                        print(f'  You called ${actual}. Pot: ${pot}')
                        s.sendall(f'INFO:Opponent called ${actual}. Pot: ${pot}')
                        s.recv()   # wait for OK

            return pot, cb, sb, None   # no one folded — return None for folded

        # ═════════════════════════════════════════════════════════════════════
        #  GAME LOOP  —  one iteration = one full hand of poker
        # ═════════════════════════════════════════════════════════════════════
        while True:

            # ── Game-over checks ─────────────────────────────────────────────
            # check if either player is too broke to post their blind
            if client_bank < BIG_BLIND:
                print('\n  You cannot cover the big blind — game over!')
                s.sendall('GAME_OVER:You win! Opponent cannot cover the blind.')
                break   # end the game loop
            if server_bank < SMALL_BLIND:
                print('\n  Opponent cannot cover the small blind — you win the game!')
                s.sendall('GAME_OVER:You lose! You cannot cover the blind.')
                break   # end the game loop

            # print a divider showing both players' current bank amounts
            print(f'\n{"═"*50}')
            print(f'  Your bank: ${client_bank}   │   Opponent: ${server_bank}')
            print(f'{"═"*50}')

            deck      = create_deck()    # build a fresh 52-card deck
            random.shuffle(deck)         # shuffle the deck randomly
            pot       = 0                # reset the pot for this hand
            community = []               # community cards start empty each hand

            # ── Post blinds ──────────────────────────────────────────────────
            client_bank -= BIG_BLIND     # client posts the big blind
            server_bank -= SMALL_BLIND   # server posts the small blind
            pot          = BIG_BLIND + SMALL_BLIND   # pot starts with both blinds
            print(f'  Blinds — You: ${BIG_BLIND} (big)   Opponent: ${SMALL_BLIND} (small)   Pot: ${pot}')
            # inform the server of the blind amounts and their updated bank
            s.sendall(f'INFO:Blinds — You: ${SMALL_BLIND} (small) | Opponent: ${BIG_BLIND} (big) | Pot: ${pot} | Bank: ${server_bank}')
            s.recv()   # wait for OK

            # ── Deal hole cards ───────────────────────────────────────────────
            server_hand = [deck.pop(), deck.pop()]   # deal 2 cards to the server
            client_hand = [deck.pop(), deck.pop()]   # deal 2 cards to the client
            # send the server their hole cards to display
            s.sendall(f'HAND:Your hand: {server_hand[0]},  {server_hand[1]}')
            s.recv()   # wait for OK
            # show the client their own hole cards
            print(f'  Your hand: {client_hand[0]},  {client_hand[1]}')

            # ── Pre-Flop ─────────────────────────────────────────────────────
            # run the pre-flop betting round before any community cards are shown
            pot, client_bank, server_bank, folded = \
                betting_round(pot, client_bank, server_bank, 'Pre-Flop')
            if folded:   # if someone folded, skip the rest of the hand
                print(f'\n  Your bank: ${client_bank}   │   Opponent: ${server_bank}')
                again = input('\n  Play another round? (yes / no): ').strip().lower()
                if again != 'yes':
                    s.sendall('GAME_OVER:Opponent left the game.')   # tell server we're done
                    break
                s.sendall('CONTINUE')   # tell server to start a new hand
                s.recv()                # wait for OK
                continue                # jump back to top of while loop

            # ── Flop ─────────────────────────────────────────────────────────
            flop = [deck.pop(), deck.pop(), deck.pop()]   # deal 3 community cards
            community.extend(flop)   # add flop cards to community card list
            print(f'\n  [Flop]  {", ".join(flop)}')
            # send the flop to the server to display
            s.sendall(f'COMMUNITY:Flop → {", ".join(flop)}')
            s.recv()   # wait for OK

            pot, client_bank, server_bank, folded = \
                betting_round(pot, client_bank, server_bank, 'Flop')
            if folded:   # someone folded on the flop
                print(f'\n  Your bank: ${client_bank}   │   Opponent: ${server_bank}')
                again = input('\n  Play another round? (yes / no): ').strip().lower()
                if again != 'yes':
                    s.sendall('GAME_OVER:Opponent left the game.')
                    break
                s.sendall('CONTINUE')
                s.recv()
                continue

            # ── Turn ─────────────────────────────────────────────────────────
            turn = deck.pop()        # deal one more community card (the turn)
            community.append(turn)   # add turn card to community list
            print(f'\n  [Turn]  {turn}')
            s.sendall(f'COMMUNITY:Turn → {turn}')   # send turn card to server
            s.recv()   # wait for OK

            pot, client_bank, server_bank, folded = \
                betting_round(pot, client_bank, server_bank, 'Turn')
            if folded:   # someone folded on the turn
                print(f'\n  Your bank: ${client_bank}   │   Opponent: ${server_bank}')
                again = input('\n  Play another round? (yes / no): ').strip().lower()
                if again != 'yes':
                    s.sendall('GAME_OVER:Opponent left the game.')
                    break
                s.sendall('CONTINUE')
                s.recv()
                continue

            # ── River ────────────────────────────────────────────────────────
            river = deck.pop()        # deal the final community card (the river)
            community.append(river)   # add river card to community list
            print(f'\n  [River]  {river}')
            s.sendall(f'COMMUNITY:River → {river}')   # send river card to server
            s.recv()   # wait for OK

            pot, client_bank, server_bank, folded = \
                betting_round(pot, client_bank, server_bank, 'River')
            if folded:   # someone folded on the river
                print(f'\n  Your bank: ${client_bank}   │   Opponent: ${server_bank}')
                again = input('\n  Play another round? (yes / no): ').strip().lower()
                if again != 'yes':
                    s.sendall('GAME_OVER:Opponent left the game.')
                    break
                s.sendall('CONTINUE')
                s.recv()
                continue

            # ── Showdown ─────────────────────────────────────────────────────
            # evaluate both hands using the best 5 cards from 7 available
            c_rank = best_hand_rank(client_hand, community)
            s_rank = best_hand_rank(server_hand, community)
            c_name = HAND_NAMES[c_rank[0]]   # get human-readable name for client's hand
            s_name = HAND_NAMES[s_rank[0]]   # get human-readable name for server's hand

            print(f'\n  ── SHOWDOWN ──')
            print(f'  Community  : {", ".join(community)}')
            print(f'  Your hand  : {client_hand[0]}, {client_hand[1]}  →  {c_name}')
            print(f'  Opponent   : {server_hand[0]}, {server_hand[1]}  →  {s_name}')

            # send the showdown info to the server so they can see both hands
            s.sendall(f'SHOWDOWN:Community: {", ".join(community)} | '
                      f'Your hand: {server_hand[0]}, {server_hand[1]} ({s_name}) | '
                      f'Opponent: {client_hand[0]}, {client_hand[1]} ({c_name})')
            s.recv()   # wait for OK

            # ── Determine winner and award pot ────────────────────────────────
            if c_rank > s_rank:
                client_bank += pot   # client wins the pot
                result_cli  = f'You win the pot of ${pot}!  ({c_name} beats {s_name})'
                result_srv  = f'RESULT:You lose. Opponent wins ${pot}.  ({c_name} beats {s_name})'
            elif s_rank > c_rank:
                server_bank += pot   # server wins the pot
                result_cli  = f'Opponent wins the pot of ${pot}.  ({s_name} beats {c_name})'
                result_srv  = f'RESULT:You win the pot of ${pot}!  ({s_name} beats {c_name})'
            else:
                split        = pot // 2          # split the pot evenly on a tie
                client_bank += split             # give each player half
                server_bank += split
                result_cli  = f"Tie! Pot split — each player receives ${split}."
                result_srv  = f"RESULT:Tie! Pot split — each player receives ${split}."

            print(f'\n  {result_cli}')   # show result to client
            s.sendall(result_srv)         # send result to server
            s.recv()                      # wait for OK

            # show updated bank totals after the hand
            print(f'  Your bank: ${client_bank}   │   Opponent: ${server_bank}')
            again = input('\n  Play another round? (yes / no): ').strip().lower()
            if again != 'yes':
                s.sendall('GAME_OVER:Opponent left the game.')   # notify server
                break
            s.sendall('CONTINUE')   # tell server another round is starting
            s.recv()                # wait for OK

        print('\nThanks for playing!')   # shown when the game loop ends


if __name__ == '__main__':
    main()
