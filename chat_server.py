import socket
import threading
import logging
import random
from datetime import datetime

#logging config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/chat_server.log"), #save chat server logs
        logging.StreamHandler() #write to console
    ]
);

##TCP chat server##
def chat_server(host="0.0.0.0", port=56458):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
    
    logging.info("### CHAT SERVER ### - Server starting up...");
    
    try:
        server.bind((host, port));
        logging.info(f"### CHAT SERVER ### - Server is bound to port {port}");
        server.listen();
        logging.info(f"### CHAT SERVER ### - Server listening on port {port}..;.");
    except Exception as e:
        logging.error(f"### CHAT SERVER ### - Failed to start server: {e}");
        return
    
    #for storing clients address and usernames
    clients = [];
    usernames = [];
    
    ##function to broadcast messages to all clients
    def broadcast(message):
        #add timestamps
        timestamp = datetime.now().strftime('%H:%M:%S');
        
        #turn message to utf-8 format
        if isinstance(message, bytes):
            message = message.decode('utf-8');
            
        formatted_message = f"[{timestamp}] {message}";
        
        logging.info(f"BROADCAST: {formatted_message}");

        for client in clients:
            try:
              client.send(formatted_message.encode('utf-8'));
            except Exception as e:
                logging.error(f"Error broadcasting to client: {e}");

    ##function to handle client messages
    def handle(client):
        while True:
            try:
                message = client.recv(1024).decode("utf-8", errors="ignore");
                if not message:
                    #if client disconnected
                    raise Exception("Client disconnected");
                
                #find username of the sender
                index = clients.index(client);
                username = usernames[index];

                #add username to message
                message_to_send = f"{username}: {message}";
                broadcast(message_to_send);

            except:
                #remove client
                if client in clients:
                    index = clients.index(client);
                    clients.remove(client);
                    client.close();
                    username = usernames[index];
                    broadcast(f"### CHAT SERVER ### - {username} has left the chat");
                    usernames.remove(username);
                    logging.info(f"{username} disconnected");
                break
    
    ##function to receive connections
    def receive():
        while True:
            try:
                client, address = server.accept();
                logging.info(f"User connected from {address}");
                
                client.send("USERNAME".encode("utf-8"));
                username = client.recv(1024).decode("utf-8", errors="ignore").strip();
                
                ##username rules
                if username.startswith('*'):
                    client.send("Invalid username!!! Username cannot start with *".encode('utf-8'));
                    client.close();
                    continue

                if username in usernames:
                    existing_username = username
                    while username in usernames:
                        suffix = random.randint(0,999);
                        username = f"{existing_username}{suffix}";
                    client.send("Username is already in use! Your username has been changed to {username}".encode('utf-8'));    
                
                if not username:
                    username = f"User_{address[1]}";
                
                #append to server list
                clients.append(client);
                usernames.append(username);
                
                print(f"Your username is : {username}")
                broadcast(f"### CHAT SERVER ### - {username} has joined the chat");
                client.send("### CHAT SERVER ### - Connected to the server".encode("utf-8"));
                logging.info(f"{username} has joined the chat from {address}");
                
                #threading
                thread = threading.Thread(target=handle, args=(client,), daemon=True);
                ##daemon=True prevents crashes
                thread.start();
            except Exception as e:
                logging.error(f"Error accepting connection: {e}");
                break
    
    try:
        receive();
    except KeyboardInterrupt:
        logging.info("Server shutting down...");
        for client in clients:
            try:
                client.close();
            except:
                pass
        server.close();

if __name__ == "__main__":
    chat_server();