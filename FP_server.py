from socket32 import create_new_socket   # import our custom socket library
import FP_client as rlib                  # reuse player_action() from the client file

HOST = '127.0.0.1'   # IP address to bind the server to (localhost)
PORT = 65444          # port the server will listen on


def main():
    with create_new_socket() as s:   # open socket, auto-closes when done
        s.bind(HOST, PORT)           # bind socket to host and port
        s.listen()                   # start listening for incoming connections
        print('POKER server started. Listening on', (HOST, PORT))

        conn2client, addr = s.accept()   # wait for a client to connect
        print('Connected by', addr)
        print('## Welcome to POKER! ##\n')

        with conn2client:   # auto-close the client connection when done

            while True:   # message-processing loop — runs until game ends

                msg = conn2client.recv()   # wait for the next message from client

                # ── Dropped connection ────────────────────────────────────────
                if msg == '':
                    # empty string means the client disconnected unexpectedly
                    print('\n  Connection lost.')
                    break   # exit the loop

                # ── Game over ─────────────────────────────────────────────────
                elif msg.startswith('GAME_OVER:'):
                    # client signals the game is finished — print reason and exit
                    print(f'\n  {msg[10:]}')   # strip 'GAME_OVER:' tag and print
                    break   # exit the loop

                # ── New round starting ────────────────────────────────────────
                elif msg == 'CONTINUE':
                    # client wants to play another hand — just acknowledge
                    conn2client.sendall('OK')

                # ── Player 2's private hole cards ─────────────────────────────
                elif msg.startswith('HAND:'):
                    # client has dealt our hole cards — display them privately
                    print(f'\n  {msg[5:]}')    # strip 'HAND:' tag and print
                    conn2client.sendall('OK')   # acknowledge receipt

                # ── Mirrored game log message ─────────────────────────────────
                elif msg.startswith('DISPLAY:'):
                    # client sends these so both screens show the same game log
                    print(f'  {msg[8:]}')      # strip 'DISPLAY:' tag and print same text
                    conn2client.sendall('OK')   # acknowledge receipt

                # ── Betting prompt — server must make a decision ───────────────
                # Format: BET:<current_bet>:<pot>:<server_bank>
                elif msg.startswith('BET:'):
                    parts       = msg.split(':', 3)      # split into exactly 4 parts
                    current_bet = int(parts[1])           # amount Player 2 needs to match
                    pot         = int(parts[2])           # current pot size
                    server_bank = int(parts[3])           # Player 2's current bank balance
                    # show Player 2 the current game state before asking for their move
                    print(f'  Pot: ${pot} | Your bank: ${server_bank}')
                    # use the shared player_action() function to get Player 2's move
                    action, amount = rlib.player_action(server_bank, current_bet=current_bet)
                    # send the decision back to the client as '<action> <amount>'
                    conn2client.sendall(f'{action} {amount}')

                # ── Unknown / fallback ────────────────────────────────────────
                else:
                    # catch-all for any unrecognized message — print and acknowledge
                    print(msg)
                    conn2client.sendall('OK')

        print('\nDisconnected.')   # shown when the connection closes


if __name__ == '__main__':
    main()
