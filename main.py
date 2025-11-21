import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import webbrowser


HTTP_PORT = 8080

BG_COLOR = "#252A34"
BTN_COLOR_SERVER = "#30475E"
BTN_COLOR_RELAY = "#162447"
BTN_COLOR_WEB = "#FFD369"
BTN_COLOR_GUI = "#27ae60"
BTN_COLOR_CLI = "#00909E"
TEXT_COLOR = "white"

class ProjectLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chat System Launcher")
        self.root.geometry("400x500")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        
        lbl_title = tk.Label(self.root, text="Chat System Control Panel", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 16, "bold"))
        lbl_title.pack(pady=20)

        #buttons
        btn_server = tk.Button(self.root, text="Start Main Server (56458)", 
                               command=self.run_server, 
                               bg=BTN_COLOR_SERVER, fg="white", font=("Arial", 12, "bold"), 
                               width=30, height=2, cursor="hand2")
        btn_server.pack(pady=5)

        
        btn_relay = tk.Button(self.root, text="Start Relay Server (56459)", 
                               command=self.run_relay, 
                               bg=BTN_COLOR_RELAY, fg="white", font=("Arial", 10), 
                               width=30, height=1, cursor="hand2")
        btn_relay.pack(pady=5)

        
        btn_web_log = tk.Button(self.root, text=f"View Web Logs (HTTP:{HTTP_PORT})", 
                               command=self.view_web_logs, 
                               bg=BTN_COLOR_WEB, fg="black", font=("Arial", 10), 
                               width=30, height=1, cursor="hand2")
        btn_web_log.pack(pady=10)

        
        btn_gui_client = tk.Button(self.root, text="Start Client (GUI Mode)", 
                                   command=self.run_gui_client, 
                                   bg=BTN_COLOR_GUI, fg="white", font=("Arial", 12, "bold"), 
                                   width=30, height=2, cursor="hand2")
        btn_gui_client.pack(pady=15)


        btn_cli_client = tk.Button(self.root, text="Start Client (CLI Mode)", 
                                   command=self.run_cli_client, 
                                   bg=BTN_COLOR_CLI, fg="white", font=("Arial", 10), 
                                   width=30, height=1, cursor="hand2")
        btn_cli_client.pack(pady=5)


        self.root.mainloop()

    def run_process(self, script_name):
        if not os.path.exists(script_name):
            messagebox.showerror("Error", f"'{script_name}' file not found \nPlease check");
            return

        try:
            if os.name == 'nt': #windows
                subprocess.Popen([sys.executable, script_name], creationflags=subprocess.CREATE_NEW_CONSOLE);
            else:
                subprocess.Popen([sys.executable, script_name]);
                
        except Exception as e:
            messagebox.showerror("Error", f"Run-time error: {e}");

    def run_server(self):
        self.run_process("chat_server.py");

    def run_relay(self):
        self.run_process("chat_relay.py");

    def view_web_logs(self):
        webbrowser.open_new_tab(f"http://localhost:{HTTP_PORT}");
        messagebox.showinfo("Browser Launch", f"Attempting to open http://localhost:{HTTP_PORT}\n(Server must be running the HTTP feature)");

    def run_gui_client(self):
        self.run_process("chat_client_gui.py");

    def run_cli_client(self):
        self.run_process("chat_client.py");

if __name__ == "__main__":
    try:
        import webbrowser;
        ProjectLauncher();
    except Exception as e:
        print(f"Failed to launch: {e}");