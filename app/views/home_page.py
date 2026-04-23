import tkinter as tk
from app.core.theme import Theme
from app.controllers.main_controller import MainController

class HomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SteamSalesPredictor")
        self.geometry("1200x800")
        
        self.controller = MainController(self)
        self.setup_ui()

    def setup_ui(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=Theme.SIDEBAR_BG, width=200)
        self.sidebar.pack(side="left", fill="y")
        
        tk.Label(self.sidebar, text="MENÚ", fg="white", bg=Theme.SIDEBAR_BG, font=("Segoe UI", 12, "bold")).pack(pady=20)
        
        for name in ["Inicio", "Informe de género","Impacto de WishList","Informe detallado","Visualización Dataset"]:
            tk.Button(
                self.sidebar, text=name, 
                command=lambda v=name: self.controller.show_view(v),
                bg=Theme.SIDEBAR_BG, fg="white", relief="flat", 
                font=Theme.FONT_UI, pady=10, cursor="hand2"
            ).pack(fill="x")

        # Contenedor Principal
        container = tk.Frame(self, bg=Theme.CONTENT_BG)
        container.pack(side="right", fill="both", expand=True)

        # Header con nombre dinámico
        header = tk.Frame(container, bg=Theme.HEADER_BG, height=70)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="SteamSalesPredictor", fg=Theme.TEXT_DARK, bg=Theme.HEADER_BG, font=Theme.FONT_TITLE).pack(side="left", padx=25)

        # Área donde se cargan las vistas de los archivos externos
        self.content_area = tk.Frame(container, bg=Theme.CONTENT_BG)
        self.content_area.pack(fill="both", expand=True)
        
        self.controller.show_view("Inicio")