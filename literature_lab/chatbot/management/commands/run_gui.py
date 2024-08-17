from django.core.management.base import BaseCommand
import tkinter as tk
from chatbot.presenters import ChatbotPresenter

class Command(BaseCommand):
    help = 'Runs the Tkinter GUI'
    app_label = 'chatbot'

    def handle(self, *args, **kwargs):
        root = tk.Tk()
        app = ChatbotPresenter(root)
        root.protocol("WM_DELETE_WINDOW", app.close_application)
        root.mainloop()
