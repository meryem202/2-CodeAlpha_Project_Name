import socket
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from cryptography.fernet import Fernet
import os

# Define the authentication password
SERVER_PASSWORD = "meryem"

# Generate or load encryption key
def get_encryption_key():
    if os.path.exists("secret.key"):
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    print(f"[SERVER] Encryption Key: {key.decode()}")  # Display key in terminal
    return key

# Encrypt file
def encrypt_file(filename, key):
    cipher = Fernet(key)
    with open(filename, "rb") as file:
        file_data = file.read()
    
    encrypted_data = cipher.encrypt(file_data)
    encrypted_filename = f"encrypted_{os.path.basename(filename)}"
    
    with open(encrypted_filename, "wb") as enc_file:
        enc_file.write(encrypted_data)
    
    return encrypted_filename

# Function to start the server
def start_server():
    host = "0.0.0.0"
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    log_message(f"Server listening on {host}:{port}...")
    
    key = get_encryption_key()  # Generate or load encryption key
    
    while True:
        client_socket, client_address = server_socket.accept()
        log_message(f"Connection from {client_address}")

        # Receive password from client
        client_password = client_socket.recv(1024).decode()
        if client_password != SERVER_PASSWORD:
            client_socket.send(b"ACCESS_DENIED")
            log_message("Client authentication failed!")
            client_socket.close()
            continue
        
        client_socket.send(b"ACCESS_GRANTED")
        log_message("Client authenticated successfully!")

        # Send encrypted file
        if selected_file:
            encrypted_filename = encrypt_file(selected_file, key)
            
            with open(encrypted_filename, "rb") as file:
                file_data = file.read()
                client_socket.sendall(file_data)
            
            log_message(f"Sent encrypted file: {encrypted_filename}")

        client_socket.close()

# Function to log messages in GUI
def log_message(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)

# Function to select a file
def select_file():
    global selected_file
    selected_file = filedialog.askopenfilename()
    if selected_file:
        file_label.config(text=f"Selected: {selected_file}")

# Function to run server in a thread
def run_server():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

# GUI setup
root = tk.Tk()
root.title("Secure File Transfer - Server")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Select a file to send:").grid(row=0, column=0, padx=10)
file_label = tk.Label(frame, text="No file selected", fg="gray")
file_label.grid(row=0, column=1, padx=10)
tk.Button(frame, text="Browse", command=select_file).grid(row=0, column=2, padx=10)

tk.Button(root, text="Start Server", command=run_server, fg="white", bg="green").pack(pady=10)

log_text = tk.Text(root, height=10, width=50)
log_text.pack(pady=10)

root.mainloop()

