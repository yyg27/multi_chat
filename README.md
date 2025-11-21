
# Multi-User Chat System

This project is a multi-threaded chat application built with Python. It features a central TCP server, a GUI-based or CLI based client for you to choose and a real-time web monitoring panel using WebSockets.

##  Project Features

-   **Multi-User Support:** Multiple clients can connect simultaneously via TCP sockets.
    
-   **Real-Time Communication:** Instant messaging with zero delay.
    
-   **Private Messaging (PM):** Secure direct messaging between users (`/pm username message`).
    
-   **Spam Protection:** Rate limiting prevents users from flooding the chat.
    
-   **Web Monitor (WebSocket):** Admins can view live server logs and statistics via a web interface in real-time.
    
-   **GUI Client:** A graphical interface built with Tkinter.
-  **CLI Client:** For 
    

## Prerequisites

-   **Python 3.x** installed on your system.
 - `tkinter` library for GUI
-   **`websockets` library** is required for the Web Monitor feature.
    

### Installation

1.  Clone or download this repository.
    
2.  Install the required library:
    
    ```
    pip install websockets
    ```

##  How to Run

The project includes a launcher (`main.py`) to manage all components.

### 1. Start the Launcher

Run the main script to open the Control Panel:

```
python main.py
```

### 2. Start the Server

-   Click **"Start Main Server"** on the launcher.
    
-   This starts the TCP server on port `56458` and the WebSocket log server on port `8080`.
    

### 3. Open Web Monitor (Optional)

-   Click **"View Web Logs"** on the launcher.
    
-   This opens the `index.html` file in your browser, connecting to the server via WebSockets to stream live logs.
    

### 4. Connect Clients

-   Click **"Start Client (GUI Mode)"** to launch a new chat window.
    
-   Enter a unique username.
    
-   Start chatting!
    

## Commands

-   **`/pm <username> <message>`**: Send a private message to a specific user.
    
-   **`/stats`**: View current server statistics (active users, total messages).
    
-   **`/exit`**: Disconnect from the server.
    

##  File Structure

-   `chat_server.py`: The core server logic (TCP + WebSocket).
    
-   `chat_client_gui.py`: The graphical user interface for clients.
    
-   `chat_client.py`: A basic command-line interface client.
    
-   `chat_relay.py`: Optional relay server for proxying connections.
    
-   `main.py`: The central launcher dashboard.
    
-   `index.html`: The web interface for real-time log monitoring.
    

##  Troubleshooting

-   **Address already in use:** If you get this error, the server wasn't closed properly. Run this command in terminal to kill the zombie process:
    
    ```
    fuser -k 56458/tcp
    ```
    
    _(Or simply use the Task Manager to kill python processes in Windows)_
    
