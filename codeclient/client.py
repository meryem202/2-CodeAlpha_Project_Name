import socket
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
import os 

# Server details
SERVER_IP = "192.168.1.17"  
SERVER_PORT = 12345


def connect_to_server():
    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Please enter the password!")
        return

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))

        
        client_socket.send(password.encode())

        
        response = client_socket.recv(1024).decode()
        if response == "ACCESS_DENIED":
            messagebox.showerror("Error", "Authentication failed! Wrong password.")
            client_socket.close()
            return
        else:
            messagebox.showinfo("Success", "Authentication successful!")

         
        with open("received_encrypted_file", "wb") as file:
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                file.write(chunk)

        messagebox.showinfo("Success", "Encrypted file received successfully!")
        decrypt_file("received_encrypted_file")

        client_socket.close()
    except Exception as e:
        messagebox.showerror("Connection Error", str(e))


def decrypt_file(encrypted_filename):
    try:
        if not os.path.exists("secret.key"):
            messagebox.showerror("Error", "Missing encryption key (secret.key).")
            return
        
        key = open("secret.key", "rb").read()  
        cipher = Fernet(key)

        with open(encrypted_filename, "rb") as file:
            encrypted_data = file.read()

        decrypted_data = cipher.decrypt(encrypted_data)

        decrypted_filename = "decrypted_received_file"
        with open(decrypted_filename, "wb") as file:
            file.write(decrypted_data)

        messagebox.showinfo("Success", f"File decrypted successfully! Saved as '{decrypted_filename}'")
    except Exception as e:
        messagebox.showerror("Decryption Error", str(e))

# GUI Setup
root = tk.Tk()
root.title("Secure File Transfer - Client")

frame = tk.Frame(root)
frame.pack(pady=20)

tk.Label(frame, text="Enter Password:").grid(row=0, column=0, padx=10)
password_entry = tk.Entry(frame, show="*", width=20)
password_entry.grid(row=0, column=1, padx=10)
tk.Button(frame, text="Connect & Receive", command=connect_to_server, fg="white", bg="blue").grid(row=0, column=2, padx=10)

root.mainloop()

