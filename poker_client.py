# Launch this after poker_server.py is already running.
from socket32 import create_new_socket
import poker_lib as plib

HOST = '127.0.0.1'
PORT = 65444

MSG_END      = "<<<END>>>"   # every message from the server ends with this marker
_recv_buffer = ""            # holds leftover data between recv calls


def recv_msg(s):
    """Receive one complete message.
    Because TCP can merge multiple sends into one recv, we keep reading
    into a buffer until we find MSG_END, then return everything before it.
    Any data after MSG_END is kept in the buffer for the next call."""
    global _recv_buffer
    while MSG_END not in _recv_buffer:        # keep reading until we have a full message
        _recv_buffer += s.recv()
    msg, _, _recv_buffer = _recv_buffer.partition(MSG_END)   # split off the first complete message
    return msg


def get_action(to_call, bank):
    """
    Show the player their options and return their choice as a string
    the server can parse: 'fold', 'check', 'call', or 'raise:<amount>'
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
    print("## Texas Hold'em — Client (Player 2) ##\n")

    with create_new_socket() as s:
        s.connect(HOST, PORT)
        print("Connected to server!\n")

        p2_bank = 20.00   # kept in sync via YOUR_TURN messages

        while True:
            msg = recv_msg(s)   # always use recv_msg so merged messages are handled correctly

            # ── Server is asking us to act ────────────────────────────────────
            if msg.startswith('YOUR_TURN:'):
                # first line: "YOUR_TURN:<to_call>:<p2_bank>"
                # everything after the first newline is the state display
                first_line, _, state_text = msg.partition('\n')
                parts   = first_line.split(':')
                to_call = float(parts[1])
                p2_bank = float(parts[2])   # keep our bank in sync with the server

                print(state_text)
                action = get_action(to_call, p2_bank)
                s.sendall(action + MSG_END)   # attach MSG_END so the server's recv_msg works too

            # ── Game is ending ────────────────────────────────────────────────
            elif msg.startswith('GAME_OVER'):
                _, _, ending = msg.partition('\n')
                print(ending if ending else 'Game over.')
                s.sendall(MSG_END)   # send empty acknowledgement — mirrors RPS end-of-game pattern
                break

            # ── Another hand is coming — nothing to do ────────────────────────
            elif msg == 'NEXT_HAND':
                pass

            # ── Everything else is a display message — just print it ──────────
            else:
                print(msg)


if __name__ == '__main__':
    main()
