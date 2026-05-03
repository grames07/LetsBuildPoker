# Run this file first, then launch poker_client.py in a second terminal.
from socket32 import create_new_socket
import poker_lib as plib
import random

HOST        = '0.0.0.0'
PORT        = 65444

# THESE VALUES CAN BE CHANGED, DEPENDING ON HOW YOU WANT TO STRUCTURE THE GAME
BIG_BLIND   = 0.50
SMALL_BLIND = 0.25
START_BANK  = 20.00

MSG_END      = "<<<END>>>"   # appended to every message we send — marks where it ends
_recv_buffer = ""            # holds leftover data between recv calls


# ─── helpers ──────────────────────────────────────────────────────────────────

def send(conn, text): # send a message with MSG_END appended to avoid merge issues on the client side
    conn.sendall(str(text) + MSG_END)


def recv_msg(conn): # keep reading into a buffer until we find MSG_END, then return everything before it
    global _recv_buffer
    while MSG_END not in _recv_buffer:        # keep reading until we have a full message
        _recv_buffer += conn.recv()
    msg, _, _recv_buffer = _recv_buffer.partition(MSG_END)   # split off the first complete message
    return msg


def mirror(conn, server_msg, client_msg): # allows us to use different messsages for server and client while keeping the same formatting
    print(server_msg)
    send(conn, client_msg)


def send_turn(conn, to_call, p2_bank, state_text): # tell client it's their turn, how much they need to call, and show them the current state of the hand
    conn.sendall(f"YOUR_TURN:{to_call:.2f}:{p2_bank:.2f}\n{state_text}" + MSG_END)


# ─── betting round ────────────────────────────────────────────────────────────

def run_betting_round(conn, p1_bank, p2_bank, pot, p1_in, p2_in, stage, community): # one complete betting round, which includes back/forth betting until both players have acted and the bets are equal (or one folds)
    p1_acted = False
    p2_acted = False
    comm_str  = ', '.join(community) if community else 'None' # format community cards for display, or show "None" if there are none yet

    while True: # our betting loop

        # ── Client's turn (Player 2) ──────────────────────────────────────────
        to_call_p2 = max(0.0, round(p1_in - p2_in, 2))

        # client sees their own bet as "Your bet" and P1's as "Opponent's bet"
        client_state = (f"\n  [{stage}]  Community: {comm_str}\n"
                        f"  Pot: {plib.format_money(pot)}  |  "
                        f"Your bet this round: {plib.format_money(p2_in)}  |  "
                        f"Opponent's bet this round: {plib.format_money(p1_in)}")
        send_turn(conn, to_call_p2, p2_bank, client_state)

        raw = recv_msg(conn)   # wait for the client's action — uses buffer to avoid merge issues

        if raw == 'fold':
            mirror(conn,"  Opponent folded.","  You folded.")
            return p1_bank, p2_bank, pot, 'player1'

        elif raw == 'check':
            mirror(conn,"  Opponent checked.","  You checked.")
            p2_acted = True

        elif raw == 'call':
            actual   = min(to_call_p2, p2_bank)
            p2_bank -= actual
            pot     += actual
            p2_in   += actual
            mirror(conn,f"  Opponent called {plib.format_money(actual)}.",f"  You called {plib.format_money(actual)}.")
            p2_acted = True

        elif raw.startswith('raise:'):
            raise_amt  = float(raw.split(':', 1)[1])
            call_first = max(0.0, p1_in - p2_in)
            total      = min(call_first + raise_amt, p2_bank)
            p2_bank   -= total
            pot       += total
            p2_in     += total
            mirror(conn,f"  Opponent raised — total this round: {plib.format_money(p2_in)}.",f"  You raised — total this round: {plib.format_money(p2_in)}.")
            p2_acted  = True
            p1_acted  = False   # server must respond to the raise

        if p1_acted and p2_acted and round(p1_in, 2) == round(p2_in, 2):
            break

        # ── Server's turn (Player 1) ──────────────────────────────────────────
        to_call_p1 = max(0.0, round(p2_in - p1_in, 2))

        # server sees their own bet as "Your bet" and P2's as "Opponent's bet"
        server_state = (f"\n  [{stage}]  Community: {comm_str}\n"
                        f"  Pot: {plib.format_money(pot)}  |  "
                        f"Your bet this round: {plib.format_money(p1_in)}  |  "
                        f"Opponent's bet this round: {plib.format_money(p2_in)}")
        print(server_state)

        action, amount = plib.player_action(p1_bank, to_call_p1)

        if action == 'fold':
            mirror(conn,
                   "  You folded.",
                   "  Opponent folded.")
            return p1_bank, p2_bank, pot, 'player2'

        elif action == 'check':
            mirror(conn,
                   "  You checked.",
                   "  Opponent checked.")
            p1_acted = True

        elif action == 'call':
            p1_bank -= amount
            pot     += amount
            p1_in   += amount
            mirror(conn,
                   f"  You called {plib.format_money(amount)}.",
                   f"  Opponent called {plib.format_money(amount)}.")
            p1_acted = True

        elif action == 'raise':
            call_first = max(0.0, p2_in - p1_in)
            total      = min(call_first + amount, p1_bank)
            p1_bank   -= total
            pot       += total
            p1_in     += total
            mirror(conn,
                   f"  You raised — total this round: {plib.format_money(p1_in)}.",
                   f"  Opponent raised — total this round: {plib.format_money(p1_in)}.")
            p1_acted  = True
            p2_acted  = False   # client must respond to the raise

        if p1_acted and p2_acted and round(p1_in, 2) == round(p2_in, 2):
            break

    return p1_bank, p2_bank, pot, None


# ─── hand helpers ─────────────────────────────────────────────────────────────

def end_hand(conn, p1_bank, p2_bank, pot, winner): # awarding the pot
    if winner == 'player1':
        p1_bank += pot
        mirror(conn, f"  You win the pot of {plib.format_money(pot)}!", f"  Opponent wins the pot of {plib.format_money(pot)}!")
    elif winner == 'player2':
        p2_bank += pot
        mirror(conn, f"  Opponent wins the pot of {plib.format_money(pot)}!", f"  You win the pot of {plib.format_money(pot)}!")
    else:
        split    = pot / 2
        p1_bank += split
        p2_bank += split
        tie_msg  = f"  Tie! Each player receives {plib.format_money(split)}."
        mirror(conn, tie_msg, tie_msg)   # same message for both on a tie

    # each player sees their own bank as "You" — same format, values swapped
    mirror(conn, f"  You: {plib.format_money(p1_bank)}  |  Opponent: {plib.format_money(p2_bank)}",f"  You: {plib.format_money(p2_bank)}  |  Opponent: {plib.format_money(p1_bank)}")

    return p1_bank, p2_bank


def play_hand(conn, p1_bank, p2_bank, hand_num):
    """Deal and play one complete hand of Texas Hold'em. Returns updated banks."""

    # ── decide who posts which blind this hand ─────────────────────────────────
    # odd hands:  P1 = big blind,   P2 = small blind
    # even hands: P1 = small blind, P2 = big blind
    if hand_num % 2 == 1:
        p1_blind      = BIG_BLIND
        p2_blind      = SMALL_BLIND
        p1_blind_name = "big"
        p2_blind_name = "small"
    else:
        p1_blind      = SMALL_BLIND
        p2_blind      = BIG_BLIND
        p1_blind_name = "small"
        p2_blind_name = "big"

    # ── Header — same format, banks swapped ────────────────────────────────────
    mirror(conn,
           f"\n{'─'*55}\n"
           f"  HAND {hand_num}   "
           f"You: {plib.format_money(p1_bank)}   "
           f"Opponent: {plib.format_money(p2_bank)}\n"
           f"{'─'*55}",
           f"\n{'─'*55}\n"
           f"  HAND {hand_num}   "
           f"You: {plib.format_money(p2_bank)}   "
           f"Opponent: {plib.format_money(p1_bank)}\n"
           f"{'─'*55}")

    # ── Deal ──────────────────────────────────────────────────────────────────
    deck = plib.create_deck()
    random.shuffle(deck)
    p1_hole   = [deck.pop(), deck.pop()]
    p2_hole   = [deck.pop(), deck.pop()]
    community = []

    # ── Blinds — same format, blind amounts and names swapped ──────────────────
    p1_bank -= p1_blind
    p2_bank -= p2_blind
    pot       = p1_blind + p2_blind
    p1_in     = p1_blind
    p2_in     = p2_blind

    mirror(conn,
           f"\n  Blinds — You: {plib.format_money(p1_blind)} ({p1_blind_name})  |  "
           f"Opponent: {plib.format_money(p2_blind)} ({p2_blind_name})  |  "
           f"Pot: {plib.format_money(pot)}",
           f"\n  Blinds — You: {plib.format_money(p2_blind)} ({p2_blind_name})  |  "
           f"Opponent: {plib.format_money(p1_blind)} ({p1_blind_name})  |  "
           f"Pot: {plib.format_money(pot)}")

    # each player only sees their own hole cards — same format, different cards
    mirror(conn,
           f"  Your hole cards: {p1_hole[0]}, {p1_hole[1]}",
           f"  Your hole cards: {p2_hole[0]}, {p2_hole[1]}")

    # ── Pre-Flop ──────────────────────────────────────────────────────────────
    pre_flop_msg = "\n  ── Pre-Flop ──"
    mirror(conn, pre_flop_msg, pre_flop_msg)
    p1_bank, p2_bank, pot, winner = run_betting_round(conn, p1_bank, p2_bank, pot, p1_in, p2_in, "Pre-Flop", community)
    if winner:
        return end_hand(conn, p1_bank, p2_bank, pot, winner)

    # ── Flop ──────────────────────────────────────────────────────────────────
    community += [deck.pop(), deck.pop(), deck.pop()]
    flop_msg   = f"\n  ── Flop: {', '.join(community)} ──"
    mirror(conn, flop_msg, flop_msg)
    p1_bank, p2_bank, pot, winner = run_betting_round(conn, p1_bank, p2_bank, pot, 0, 0, "Flop", community)
    if winner:
        return end_hand(conn, p1_bank, p2_bank, pot, winner)

    # ── Turn ──────────────────────────────────────────────────────────────────
    community.append(deck.pop())
    turn_msg = f"\n  ── Turn: {', '.join(community)} ──"
    mirror(conn, turn_msg, turn_msg)
    p1_bank, p2_bank, pot, winner = run_betting_round(conn, p1_bank, p2_bank, pot, 0, 0, "Turn", community)
    if winner:
        return end_hand(conn, p1_bank, p2_bank, pot, winner)

    # ── River ─────────────────────────────────────────────────────────────────
    community.append(deck.pop())
    river_msg = f"\n  ── River: {', '.join(community)} ──"
    mirror(conn, river_msg, river_msg)
    p1_bank, p2_bank, pot, winner = run_betting_round(conn, p1_bank, p2_bank, pot, 0, 0, "River", community)
    if winner:
        return end_hand(conn, p1_bank, p2_bank, pot, winner)

    # ── Showdown — same format, hole cards and hand names swapped ──────────────
    p1_best = plib.best_hand_rank(p1_hole, community)
    p2_best = plib.best_hand_rank(p2_hole, community)
    result  = plib.compare_hands(p1_best, p2_best)

    mirror(conn,
           f"\n  ── Showdown ──\n"
           f"  You: {p1_hole[0]}, {p1_hole[1]}  →  {plib.possible_hands[p1_best[0]]}\n"
           f"  Opponent: {p2_hole[0]}, {p2_hole[1]}  →  {plib.possible_hands[p2_best[0]]}",f"\n  ── Showdown ──\n"
           f"  You: {p2_hole[0]}, {p2_hole[1]}  →  {plib.possible_hands[p2_best[0]]}\n"
           f"  Opponent: {p1_hole[0]}, {p1_hole[1]}  →  {plib.possible_hands[p1_best[0]]}")

    winner = 'player1' if result == 1 else ('player2' if result == -1 else 'tie')
    return end_hand(conn, p1_bank, p2_bank, pot, winner)


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    print("## Texas Hold'em — Server (Player 1) ##\n")

    with create_new_socket() as s:
        s.bind(HOST, PORT)
        s.listen()
        print(f"Waiting for opponent on {HOST}:{PORT} ...")

        conn, addr = s.accept()
        print(f"Opponent connected from {addr}\n")

        with conn:
            p1_bank  = START_BANK
            p2_bank  = START_BANK
            hand_num = 1

            while True:
                p1_bank, p2_bank = play_hand(conn, p1_bank, p2_bank, hand_num)
                hand_num += 1

                # ── check if the game is over ──────────────────────────────────
                if p1_bank <= 0:
                    send(conn, "GAME_OVER\nYou win — opponent is out of chips!")
                    print("Opponent wins the game!")
                    recv_msg(conn)   # wait for client's empty acknowledgement before closing
                    break
                if p2_bank <= 0:
                    send(conn, "GAME_OVER\nOpponent wins — you are out of chips!")
                    print("You win the game!")
                    recv_msg(conn)   # wait for client's empty acknowledgement before closing
                    break

                # ── ask server player if they want another hand ────────────────
                again = input("\n  Play another hand? (yes / no): ").strip().lower()
                if again != 'yes':
                    send(conn, "GAME_OVER\nThanks for playing!")
                    recv_msg(conn)   # wait for client's empty acknowledgement before closing
                    break
                send(conn, "NEXT_HAND")

            print("\n  Session ended.")


if __name__ == '__main__':
    main()
