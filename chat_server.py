import socket
import threading
import logging
import random
import time
from datetime import datetime


#logging config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chat_server.log"), #save chat server logs
        logging.StreamHandler() #write to console
    ]
);

host = "0.0.0.0";
tcp_port = 56458;

#for storing clients address and usernames
clients = [];
usernames = [];

#for storing offline messages
delayed_messages = {};

server_stats = {
    "total_messages":0,
    "total_pms":0,
    "active_users":0
};

#to keep last message times for clients
last_message_time = {};
muted_users = {}

def is_spam(client):
    current_time = time.time();
    spam_timer = 3
    cooldown = 10

    #check if user is in already cooldown
    if client in muted_users:
        cooldown_time = muted_users[client];
        if current_time < cooldown_time:
            cooldown = int(cooldown_time - current_time); ##new cooldown value
            return True,cooldown;
        else:
            del muted_users[client];

    #check if is spam
    if client in last_message_time:
        last_time = last_message_time[client]; 

        if current_time - last_time < spam_timer:
            muted_users[client] = current_time + cooldown
            return True,cooldown #spam

    last_message_time[client] = current_time;
    return False,0;

def show_stats():
    stats = f"[SYSTEM REPORT] Active Users: {len(clients)} | Total Messages: {server_stats['total_messages']} | Total PMs: {server_stats['total_pms']}";
    logging.info(stats);

#for showing stats every other minute
def show_stats_period():
    while True:
        time.sleep(120);
        show_stats();



##function to receive connections
def receive(server):
    while True:
        try:
            client, address = server.accept();
            logging.info(f"User connected from {address}");
                
            client.send("USERNAME".encode("utf-8"));
            username = client.recv(1024).decode("utf-8", errors="ignore").strip();
                
            ##username rules
            if username.startswith('*'):
                client.send("[### CHAT SERVER ###] - Invalid username! Username cannot start with *".encode('utf-8'));
                client.close();
                continue

            if username in usernames:
                existing_username = username
                while username in usernames:
                    suffix = random.randint(0,999);
                    username = f"{existing_username}{suffix}";
                client.send(f"[### CHAT SERVER ###] - Username is already in use.. Your username has been changed to {username}".encode('utf-8'));    
                
            if not username:
                username = f"User_{address[1]}";
                
            #append to server list
            clients.append(client);
            usernames.append(username);

            server_stats["active_users"] = len(clients);

            if username in delayed_messages:
                pending_message = delayed_messages[username];
                client.send(f"There are {len(pending_message)} messages for you".encode('utf-8'));

                for message in pending_message:
                    client.send(message.encode('utf-8'));

                del delayed_messages[username];    

                
            print(f"Your username is : {username}")
            broadcast(f"[### CHAT SERVER ###] - {username} has joined the chat");
            client.send("[### CHAT SERVER ###] - Connected to the server".encode("utf-8"));
            logging.info(f"{username} has joined the chat from {address}");
                
            #threading
            thread = threading.Thread(target=handle, args=(client,), daemon=True);
            ##daemon=True prevents crashes
            thread.start();
        except Exception as e:
            logging.error(f"Error accepting connection: {e}");
            break
    
##function to handle client messages
def handle(client):
    while True:
        try:
            message = client.recv(1024).decode("utf-8", errors="ignore");
            if not message:
                #if client disconnected
                raise Exception("Client disconnected");
            
            #check spam
            spam,cooldown = is_spam(client);

            if spam:
                client.send(f"SPAM DETECTED ! You are muted for {cooldown} seconds...".encode('utf-8'));
                continue;
    
            #find username of the sender
            index = clients.index(client);
            username = usernames[index];
                
            #find out if it is a broadcast or private message
            if message.startswith("/pm"):
                server_stats["total_pms"] += 1;
                send_pm(client,username,message);
            #show stats with /stats command on demand
            elif message.strip() == "/stats":
                show_stats();
                client.send(f"[SYSTEM REPORT] Active Users: {len(clients)} | Total Messages: {server_stats['total_messages']} | Total PMs: {server_stats['total_pms']}".encode('utf-8'));
            else:
                #add username to message
                message_to_broadcast = f"{username}: {message}";
                server_stats["total_messages"] += 1;
                broadcast(message_to_broadcast);

        except:
            #remove client
            if client in clients:
                index = clients.index(client);
                clients.remove(client);
                client.close();

                server_stats["active_users"] = len(clients);

                username = usernames[index];
                broadcast(f"{username} has left the chat");
                usernames.remove(username);
                logging.info(f"{username} disconnected");
            break
    

##function to broadcast messages to all clients
def broadcast(message):
    #add timestamps
    timestamp = datetime.now().strftime('%H:%M:%S');
        
    #turn message to utf-8 format
    if isinstance(message, bytes):
        message = message.decode('utf-8');
            
    formatted_message = f"[{timestamp}] {message}";
        
    logging.info(f"[BROADCAST]: {formatted_message}");

    for client in clients:
        try:
          client.send(formatted_message.encode('utf-8'));
        except Exception as e:
            logging.error(f"Error broadcasting to client: {e}");


##function to send private messages
def send_pm(sender_client,sender_username,message):
    try:
        ##message format is /pm username hello world blablabla
        components = message.split(" ",2);

        if len(components) < 3:
            sender_client.send("[### CHAT SERVER ###] - Invalid /pm command use this format: /pm <username> <message>".encode('utf-8'));
            return

        target_name = components[1];
        private_message = components[2];

        #for saving messages for offline users
        if target_name not in usernames:
            sender_client.send(f"[### CHAT SERVER ###] - User {target_name} is not found".encode('utf-8'));
            sender_client.send("Saving your message to database to send when user is online".encode('utf-8'));
            timestamp = datetime.now().strftime('%H:%M:%S');
            saved_message = f"[{timestamp}] [DELAYED MESSAGE] {sender_username}: {private_message}";

            if target_name not in delayed_messages:
                delayed_messages[target_name] = [];
        
            delayed_messages[target_name].append(saved_message);

            return;

        timestamp = datetime.now().strftime('%H:%M:%S');

        target_index = usernames.index(target_name);
        target_client = clients[target_index];

        #send pm
        target_client.send(f"[{timestamp}] [*PRIVATE*] {sender_username}: {private_message}".encode('utf-8'));
        #to notify the sender
        sender_client.send(f"[{timestamp}] [PM sended to {target_name}]: {private_message}".encode('utf-8'))
        #logging
        logging.info(f"[**PRIVATE MESSAGE**] {sender_username} to {target_name} : {private_message}");

    except Exception as e:
        logging.error(f"PM Error: {e}");
        sender_client.send("[### CHAT SERVER ###] - Error sending private message.".encode('utf-8'));


##TCP chat server##
def tcp_chat_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
    
    logging.info("[### CHAT SERVER ###] - Server starting up...");
    
    try:
        server.bind((host, tcp_port));
        logging.info(f"[### CHAT SERVER ###] - Server is bound to port {tcp_port}");
        server.listen();
        logging.info(f"[### CHAT SERVER ###] - Server listening on port {tcp_port}..;.");

        threading.Thread(target=show_stats_period, daemon=True).start();
        
        receive(server);

    except Exception as e:
        logging.error(f"[### CHAT SERVER ###] - Failed to start server: {e}");
        return
    

if __name__ == "__main__":  
    try:
        tcp_chat_server();
    except KeyboardInterrupt:
        logging.info("Server shutting down...");
        for client in clients:
            try:
                client.close();
            except:
                pass

        logging.info("Server is closed");