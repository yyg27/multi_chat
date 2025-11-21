import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox, Listbox


DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 56458


BG_DARK = '#1a1a1a'
BG_MED = '#252525'
BG_LIGHT = '#2d2d2d'
BG_INPUT = '#333333'
ACCENT = '#e94560'
TEXT = '#ffffff'
TEXT_DIM = '#888888'
GREEN = '#00d26a'
PURPLE = '#bb86fc'
CYAN = '#03dac6'
BLUE = '#4cc9f0'

class client_gui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        #username prompt
        self.username = simpledialog.askstring("Login", "Username:", parent=self.root)
        if not self.username:
            self.root.destroy()
            return

        self.root.deiconify()
        self.root.title(f"Chat - {self.username}")
        self.root.geometry("950x600")
        self.root.configure(bg=BG_DARK)

        self.pm_windows = {}
        self.running = True

        self.build_gui()
        self.connect_to_server()

        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        self.root.mainloop()

    def build_gui(self):
        main = tk.Frame(self.root, bg=BG_DARK)
        main.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        #chat section
        left = tk.Frame(main, bg=BG_MED)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,3))

        #header
        header = tk.Frame(left, bg=BG_LIGHT)
        header.pack(fill=tk.X)

        tk.Label(header, text="CHATROOM", font=("Arial", 12, "bold"),
                bg=BG_LIGHT, fg=TEXT).pack(side=tk.LEFT, padx=15, pady=12)

        self.status_label = tk.Label(header, text="Connecting...", 
                                    font=("Arial", 9), bg=BG_LIGHT, fg=TEXT_DIM)
        self.status_label.pack(side=tk.RIGHT, padx=15, pady=12)

        #chat area
        self.chat_area = scrolledtext.ScrolledText(
            left, wrap=tk.WORD, state='disabled',
            bg=BG_DARK, fg=TEXT, font=("Consolas", 10), 
            relief='flat', padx=10, pady=10
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.chat_area.tag_config("me", foreground=BLUE)
        self.chat_area.tag_config("private", foreground=PURPLE)
        self.chat_area.tag_config("system", foreground=CYAN)
        self.chat_area.tag_config("general", foreground=TEXT)

        #input frame
        input_frame = tk.Frame(left, bg=BG_INPUT)
        input_frame.pack(fill=tk.X, padx=10, pady=(0,10))

        self.entry = tk.Entry(input_frame, font=("Arial", 11),
                             bg=BG_INPUT, fg=TEXT,
                             insertbackground='white', relief='flat')
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, ipady=10)
        self.entry.bind("<Return>", self.send)

        send_btn = tk.Button(input_frame, text="SEND", font=("Arial", 10, "bold"),
                            bg=ACCENT, fg='white', relief='flat',
                            cursor='hand2', command=self.send)
        send_btn.pack(side=tk.RIGHT, padx=5, pady=5, ipadx=15)

        #users section
        right = tk.Frame(main, bg=BG_MED, width=220)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        user_header = tk.Frame(right, bg=BG_LIGHT)
        user_header.pack(fill=tk.X)

        tk.Label(user_header, text="Users", font=("Arial", 11, "bold"),
                bg=BG_LIGHT, fg=TEXT).pack(side=tk.LEFT, padx=15, pady=12)

        self.user_count_label = tk.Label(user_header, text="0", 
                                        font=("Arial", 9, "bold"), 
                                        bg=ACCENT, fg='white', padx=6)
        self.user_count_label.pack(side=tk.RIGHT, padx=10, pady=12)

        self.user_list = Listbox(right, font=("Arial", 10),
                                bg=BG_DARK, fg=TEXT, relief='flat', 
                                selectbackground=ACCENT,
                                selectforeground='white',
                                highlightthickness=0)
        self.user_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.user_list.bind('<Double-1>', self.open_pm_click)

        tk.Label(right, text="Double click to user for PM",
                font=("Arial", 8), bg=BG_MED, fg=TEXT_DIM).pack(pady=5)

        #commands
        cmd = tk.Frame(right, bg=BG_LIGHT)
        cmd.pack(fill=tk.X, padx=10, pady=(0,10))
        tk.Label(cmd, text="/pm user msg\n/stats | /exit",
                font=("Consolas", 9), bg=BG_LIGHT, fg=TEXT_DIM).pack(padx=10, pady=8)

    def connect_to_server(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        try:
            self.client.connect((DEFAULT_HOST, DEFAULT_PORT));
            self.status_label.config(text="ONLINE", fg=GREEN);
            threading.Thread(target=self.receive, daemon=True).start();
        except Exception as e:
            self.status_label.config(text="OFFLINE", fg=ACCENT);
            messagebox.showerror("Error", f"Unable to connect the server!\n{e}");
            self.root.destroy();

    def receive(self):
        while self.running:
            try:
                data = self.client.recv(4096).decode('utf-8');
                if not data:
                    break
                
                for msg in data.split('\n'):
                    if not msg:
                        continue

                    if msg == "USERNAME":
                        self.client.send(self.username.encode('utf-8'));
                    
                    elif "Your username has been changed to" in msg:
                        try:
                            parts = msg.split("changed to");
                            new_name = parts[1].strip();
                            self.username = new_name;
                            self.root.title(f"Chat - {self.username}");
                            self.display(msg, "system");
                        except:
                            self.display(msg, "system");

                    elif msg.startswith("USERS:"):
                        self.update_user_list(msg);
                    elif "[*PRIVATE*]" in msg:
                        self.handle_incoming_pm(msg);
                    elif "[PM sended to" in msg:
                        self.display(msg, "private");
                    elif "[### CHAT SERVER ###]" in msg or "[SYSTEM REPORT]" in msg:
                        self.display(msg, "system");
                    else:
                        self.display(msg, "general");
            except:
                break
        
        self.stop();

    def update_user_list(self, msg):
        try:
            users = [u.strip() for u in msg.replace("USERS:", "").split(",") if u.strip()]
            self.user_list.delete(0, tk.END);
            for user in users:
                mark = ">> " if user == self.username else "   "
                self.user_list.insert(tk.END, mark + user);
            self.user_count_label.config(text=str(len(users)));
        except:
            pass

    def handle_incoming_pm(self, full_msg):
        try:
            parts = full_msg.split("[*PRIVATE*] ");
            content = parts[1];
            sender = content.split(":")[0].strip();
            text = content.split(":", 1)[1].strip();

            if sender in self.pm_windows:
                self.write_to_pm_window(sender, f"{sender}: {text}");
            else:
                self.display(f"[PM <- {sender}]: {text}", "private");
        except:
            self.display(full_msg, "private");

    def create_pm_window(self, target):
        target = target.replace(">> ", "").replace("   ", "").strip();
        
        if target in self.pm_windows:
            self.pm_windows[target]['window'].lift();
            return

        win = tk.Toplevel(self.root);
        win.title(f"PM: {target}");
        win.geometry("400x320");
        win.configure(bg=BG_MED);

        def on_close():
            self.pm_windows.pop(target, None)
            win.destroy();
        win.protocol("WM_DELETE_WINDOW", on_close);

        #pm header
        tk.Label(win, text=f"PM: {target}", font=("Arial", 10, "bold"),
                bg=BG_LIGHT, fg=TEXT).pack(fill=tk.X, ipady=10)

        #pm chat
        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, state='disabled',
                                       bg=BG_DARK, fg=TEXT,
                                       font=("Consolas", 10), relief='flat')
        txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        #pm input
        inp_frame = tk.Frame(win, bg=BG_INPUT)
        inp_frame.pack(fill=tk.X, padx=8, pady=(0,8))

        ent = tk.Entry(inp_frame, font=("Arial", 10), bg=BG_INPUT, fg=TEXT,
                      insertbackground='white', relief='flat')
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, ipady=8)
        ent.focus_set()

        def send_pm(e=None):
            m = ent.get();
            if m:
                self.client.send(f"/pm {target} {m}".encode('utf-8'));
                txt.configure(state='normal');
                txt.insert(tk.END, f"Ben: {m}\n");
                txt.configure(state='disabled');
                txt.see(tk.END);
                ent.delete(0, tk.END);

        ent.bind("<Return>", send_pm)
        tk.Button(inp_frame, text="Send", bg=ACCENT, fg='white',
                 relief='flat', command=send_pm).pack(side=tk.RIGHT, padx=5, pady=3)

        self.pm_windows[target] = {'window': win, 'text': txt}

    def write_to_pm_window(self, user, text):
        if user in self.pm_windows:
            txt = self.pm_windows[user]['text'];
            txt.configure(state='normal');
            txt.insert(tk.END, text + "\n");
            txt.configure(state='disabled');
            txt.see(tk.END);

    def open_pm_click(self, event):
        sel = self.user_list.curselection();
        if sel:
            target = self.user_list.get(sel[0]).replace(">> ", "").replace("   ", "").strip();
            if target and target != self.username:
                self.create_pm_window(target);

    def display(self, msg, tag="general"):
        self.chat_area.configure(state='normal');
        if f"] {self.username}:" in msg:
            self.chat_area.insert(tk.END, msg + "\n", "me");
        else:
            self.chat_area.insert(tk.END, msg + "\n", tag);
        self.chat_area.configure(state='disabled');
        self.chat_area.see(tk.END);

    def send(self, event=None):
        msg = self.entry.get();
        if msg:
            self.client.send(msg.encode('utf-8'));
            self.entry.delete(0, tk.END);
            if msg == "/exit":
                self.stop();

    def stop(self):
        self.running = False
        try:
            self.client.close();
        except:
            pass
        self.root.destroy();

if __name__ == "__main__":
    client_gui();