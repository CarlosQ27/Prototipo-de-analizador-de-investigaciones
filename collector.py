import tkinter as tk
from tkinter import ttk
import json
import threading
import time

class CollectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú")

        self.data = None

        # Título del artículo
        self.title_label = ttk.Label(root, text="Título del artículo:")
        self.title_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.title_entry = ttk.Entry(root, width=50)
        self.title_entry.grid(row=0, column=1, padx=10, pady=10)

        # Tipo de publicación
        self.type_label = ttk.Label(root, text="Tipo de publicación:")
        self.type_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.type_var = tk.StringVar()
        self.type_conference = ttk.Radiobutton(root, text="Conferencia", variable=self.type_var, value="Conferencia", command=self.toggle_type)
        self.type_conference.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        self.type_journal = ttk.Radiobutton(root, text="Revista", variable=self.type_var, value="Revista", command=self.toggle_type)
        self.type_journal.grid(row=1, column=1, padx=110, pady=10, sticky=tk.W)

        # Nombre de la conferencia
        self.conference_label = ttk.Label(root, text="Nombre de la conferencia:")
        self.conference_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.conference_entry = ttk.Entry(root, width=50)
        self.conference_entry.grid(row=2, column=1, padx=10, pady=10)
        self.conference_label.grid_remove()
        self.conference_entry.grid_remove()

        # Link de la página principal de la revista
        self.journal_link_label = ttk.Label(root, text="Link de la página principal de la revista:")
        self.journal_link_label.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.journal_link_entry = ttk.Entry(root, width=50)
        self.journal_link_entry.grid(row=3, column=1, padx=10, pady=10)
        self.journal_link_label.grid_remove()
        self.journal_link_entry.grid_remove()

        # Link de la investigación
        self.research_link_label = ttk.Label(root, text="Link de la investigación:")
        self.research_link_label.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        self.research_link_entry = ttk.Entry(root, width=50)
        self.research_link_entry.grid(row=4, column=1, padx=10, pady=10)

        # Botón de envío
        self.submit_button = ttk.Button(root, text="Enviar", command=self.submit)
        self.submit_button.grid(row=5, column=0, columnspan=2, pady=20)

        # Label para animación de procesamiento
        self.processing_label = ttk.Label(root, text="", foreground="red")
        self.processing_label.grid(row=6, column=0, columnspan=2, pady=10)

    def toggle_type(self):
        if self.type_var.get() == "Conferencia":
            self.conference_label.grid()
            self.conference_entry.grid()
            self.journal_link_label.grid_remove()
            self.journal_link_entry.grid_remove()
        else:
            self.conference_label.grid_remove()
            self.conference_entry.grid_remove()
            self.journal_link_label.grid()
            self.journal_link_entry.grid()

    def submit(self):
        self.data = {
            "title": self.title_entry.get(),
            "type": self.type_var.get(),
            "conference_name": self.conference_entry.get() if self.type_var.get() == "Conferencia" else "",
            "journal_link": self.journal_link_entry.get() if self.type_var.get() == "Revista" else "",
            "research_link": self.research_link_entry.get()
        }
        self.processing_label.config(text="Procesando los datos obtenidos.")
        threading.Thread(target=self.process_data).start()
        self.animate_processing()

    def process_data(self):
        # Simula algún procesamiento pesado
        time.sleep(5)
        self.root.quit()

    def animate_processing(self):
        current_text = self.processing_label.cget("text")
        if current_text.endswith("..."):
            self.processing_label.config(text="Procesando los datos obtenidos.")
        else:
            self.processing_label.config(text=current_text + ".")
        self.root.after(500, self.animate_processing)

    def get_data(self):
        return self.data

if __name__ == "__main__":
    root = tk.Tk()
    app = CollectorApp(root)
    root.mainloop()
    if app.get_data():
        print(json.dumps(app.get_data()))
