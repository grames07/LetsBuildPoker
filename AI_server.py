from socket32 import create_new_socket   # import our custom socket library
import FP_client as rlib                  # reuse player_action() from the client file

HOST = '127.0.0.1'   # the IP address to bind the server to (localhost)
PORT = 65444          # the port the server will listen on


def main():
    with create_new_socket() as s:    # open a socket, auto-close when done
        s.bind(HOST, PORT)            # bind the socket to our host and port
        s.listen()                    # start listening for incoming connections
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
                    break   # exit the message loop

                # ── Game over ─────────────────────────────────────────────────
                elif msg.startswith('GAME_OVER:'):
                    # client has signaled the game is finished
                    print(f'\n  {msg[10:]}')   # print the reason (everything after 'GAME_OVER:')
                    break   # exit the message loop

                # ── Continue to next round ────────────────────────────────────
                elif msg == 'CONTINUE':
                    # client wants to play another hand — acknowledge and loop
                    conn2client.sendall('OK')

                # ── Server's hole cards ───────────────────────────────────────
                elif msg.startswith('HAND:'):
                    # client has dealt our hole cards — display them
                    print(f'\n  {msg[5:]}')    # strip 'HAND:' tag and print
                    conn2client.sendall('OK')   # acknowledge receipt

                # ── Community cards (flop / turn / river) ─────────────────────
                elif msg.startswith('COMMUNITY:'):
                    # client is revealing a community card or the flop
                    print(f'\n  {msg[10:]}')   # strip 'COMMUNITY:' tag and print
                    conn2client.sendall('OK')   # acknowledge receipt

                # ── Showdown reveal ───────────────────────────────────────────
                elif msg.startswith('SHOWDOWN:'):
                    # client is revealing both hands at the end of the round
                    print('\n  ── SHOWDOWN ──')
                    for part in msg[9:].split(' | '):   # split by ' | ' to print each part on its own line
                        print(f'  {part}')
                    conn2client.sendall('OK')   # acknowledge receipt

                # ── Round result ──────────────────────────────────────────────
                elif msg.startswith('RESULT:'):
                    # client is telling us the outcome of the round
                    print(f'\n  {msg[7:]}')    # strip 'RESULT:' tag and print
                    conn2client.sendall('OK')   # acknowledge receipt

                # ── General info (no action required) ────────────────────────
                elif msg.startswith('INFO:'):
                    # client is sending a status update — just display it
                    print(f'  {msg[5:]}')      # strip 'INFO:' tag and print
                    conn2client.sendall('OK')   # acknowledge receipt

                # ── Betting prompt (server must choose an action) ─────────────
                # Message format:  BET:<current_bet>:<pot>:<server_bank>:<display_message>
                elif msg.startswith('BET:'):
                    parts       = msg.split(':', 4)    # split into exactly 5 parts
                    current_bet = int(parts[1])         # the amount we need to match
                    pot         = int(parts[2])         # the current pot size
                    server_bank = int(parts[3])         # our current bank balance
                    display     = parts[4]              # the message to show the player
                    print(f'\n  {display}')             # show the betting situation
                    print(f'  Pot: ${pot} | Your bank: ${server_bank}')
                    # use the shared player_action function to get the server player's move
                    action, amount = rlib.player_action(server_bank,
                                                        current_bet=current_bet)
                    # send the action and amount back to the client as '<action> <amount>'
                    conn2client.sendall(f'{action} {amount}')

                # ── Unknown / fallback ────────────────────────────────────────
                else:
                    # catch-all for any unrecognized message — print and acknowledge
                    print(msg)
                    conn2client.sendall('OK')

        print('\nDisconnected.')   # shown when the connection closes


if __name__ == '__main__':
    main()
