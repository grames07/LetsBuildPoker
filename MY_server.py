#import socket32, which allows us to connect servers and clients
from socket32 import create_new_socket
import MY_client as rlib

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65444        # The port used by the server



def main():
    with create_new_socket() as s:
        # Bind socket to address and publish contact info
        s.bind(HOST, PORT)
        s.listen()
        print("POKER server started. Listening on", (HOST, PORT))

        # Answer incoming connection
        conn2client, addr = s.accept()
        print('Connected by', addr)


        with conn2client:
            # Create a secret for this connection


            while True:   # message processing loop
                server_hand_message = conn2client.recv()
                print(server_hand_message)




                conn2client.sendall(server_move)

                server_message = conn2client.recv()
                print(server_message)
                if server_message[-2:]== 'h!':
                    break




            print('Disconnected')

if __name__ == '__main__':
    main()

