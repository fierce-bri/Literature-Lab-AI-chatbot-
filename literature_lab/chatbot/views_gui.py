import tkinter as tk
from tkinter import messagebox

class ViewGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Literature Lab Chatbot")
        self.root.geometry("500x400")

        self.input_label = tk.Label(root, text="Enter your text:")
        self.input_label.pack(pady=10)

        self.input_text = tk.Text(root, height=10, width=50)
        self.input_text.pack()

        self.submit_button = tk.Button(root, text="Submit", width=10)
        self.submit_button.pack(pady=10)

        self.response_label = tk.Label(root, text="Response:")
        self.response_label.pack(pady=10)

        self.response_text = tk.Text(root, height=5, width=50, state='disabled')
        self.response_text.pack()
