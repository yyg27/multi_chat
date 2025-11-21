import socket
import threading
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
);

HOST="localhost" ;
PORT=56458;

##TCP chat client##
def chat_client(host=HOST, port=PORT):
    username = input("Enter your username: ").strip();
    if not username:
        print("Please enter a username!");
        return
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    
    try:
        client.connect((host, port));
    except Exception as e:
        logging.error(f"Connection error: {e}");
        return
    
    logging.info(f"Connected to server at {host}:{port}");
    
    def receive_msg():
        while True:
            try:
                data = client.recv(1024).decode('utf-8', errors='ignore');
                if not data:
                    raise Exception("Server closed connection");
                
                messages = data.split('\n')
                for message in messages:
                    if not message:
                        continue

                    if message == "USERNAME":
                        client.send(username.encode('utf-8'));
                    else:
                        print(message);

            except Exception as e:
                print(f"\nDisconnected from server: {e}");
                client.close();
                break
    
    ##function to send messages
    def write():
        while True:
            try:
                message_text = input('');
                #to exit chat
                if message_text.lower() == ("/exit"):
                    logging.info("Leaving chat...");
                    client.close();
                    break

                if message_text.strip():
                    client.send(message_text.encode('utf-8'));
            except Exception as e:
                print(f"Error sending message: {e}");
                client.close();
                break
            except OSError:
                break
    
    ##threading
    receive_thread = threading.Thread(target=receive_msg, daemon=True);
    receive_thread.start();
    
    write_thread = threading.Thread(target=write, daemon=True);
    write_thread.start();
    
    #keeping the main thread alive
    try:
        receive_thread.join();
    except KeyboardInterrupt:
        print("\nDisconnecting...");
        client.close();
        sys.exit();

if __name__ == "__main__":
    chat_client();