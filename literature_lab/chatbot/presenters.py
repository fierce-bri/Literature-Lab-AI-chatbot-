from .models import UserQuery
from .views_gui import ViewGUI
import tkinter as tk
from tkinter import messagebox

class ChatbotPresenter:
    def __init__(self, root):
        self.view = ViewGUI(root)
        self.view.submit_button.config(command=self.process_input)

    def process_input(self):
        input_text = self.view.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("Input Error", "Please enter some text.")
            return
        response_text = self.generate_response(input_text)
        self.view.response_text.config(state='normal')
        self.view.response_text.delete("1.0", tk.END)
        self.view.response_text.insert(tk.END, response_text)
        self.view.response_text.config(state='disabled')

    def generate_response(self, input_text):
        # Placeholder for generating a response
        return f"You wrote: {input_text}"

    def close_application(self):
        self.view.root.destroy()

