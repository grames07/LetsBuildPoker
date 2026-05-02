# Launch this after poker_server.py is already running.
from socket32 import create_new_socket
import poker_lib as plib

HOST = '127.0.0.1'
PORT = 65444


def get_action(to_call, bank):
    """
    Show the player their options and return their choice as a string
    the server can parse: 'fold', 'check', 'call', or 'raise:<amount>'
    Mirrors player_action() from poker_lib but sends over the socket instead
    of returning locally.
    """
    if to_call == 0:
        options = ['fold', 'check', 'raise']
        prompt  = '  Your move (fold / check / raise): '
    else:
        options = ['fold', 'call', 'raise']
        prompt  = f'  Your move (fold / call {plib.format_money(to_call)} / raise): '

    while True:
        move = input(prompt).strip().lower()

        if move not in options:
            print(f'  Invalid. Please choose: {" / ".join(options)}')
            continue

        if move == 'raise':
            while True:
                try:
                    amt = float(input('  Raise amount: $'))
                    if amt <= 0:
                        print('  Amount must be more than zero.')
                    elif amt > bank:
                        print(f'  You only have {plib.format_money(bank)}.')
                    else:
                        return f'raise:{amt}'
                except ValueError:
                    print('  Please type a number.')

        return move   # 'fold', 'check', or 'call'


def main():
    print("## Texas Hold'em — Client  (Player 2 / Small Blind) ##\n")

    with create_new_socket() as s:
        s.connect(HOST, PORT)
        print("Connected to server!\n")

        p2_bank = 20.00   # starting bank — re-synced each turn via YOUR_TURN messages

        while True:
            msg = s.recv()

            # ── Server is asking us to act ────────────────────────────────────
            if msg.startswith('YOUR_TURN:'):
                # first line format: "YOUR_TURN:<to_call>:<p2_bank>"
                # everything after the first newline is the state display text
                first_line, _, state_text = msg.partition('\n')
                parts   = first_line.split(':')   # ['YOUR_TURN', to_call, p2_bank]
                to_call = float(parts[1])
                p2_bank = float(parts[2])         # keep our bank in sync with the server

                print(state_text)
                action = get_action(to_call, p2_bank)
                s.sendall(action)                 # send choice back to server

            # ── Game is ending ────────────────────────────────────────────────
            elif msg.startswith('GAME_OVER'):
                _, _, ending = msg.partition('\n')
                print(ending if ending else 'Game over.')
                break

            # ── Server confirmed another hand is coming ───────────────────────
            elif msg == 'NEXT_HAND':
                pass   # nothing to do — the hand header will arrive momentarily

            # ── Everything else is a display message ──────────────────────────
            else:
                print(msg)


if __name__ == '__main__':
    main()
