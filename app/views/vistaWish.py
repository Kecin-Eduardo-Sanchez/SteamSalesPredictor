import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from app.controllers.ActualidadWish import ControladorWish

class VistaWish(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="white")

        # --- 1. SISTEMA DE SCROLL RESPONSIVO ---
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        # Ajuste dinámico de ancho y salto de línea (wraplength)
        def configurar_ancho_frame(event):
            # El frame interno ocupa todo el ancho del canvas
            self.canvas.itemconfig(self.canvas_window, width=event.width)
            # El texto se ajusta al nuevo ancho menos márgenes
            if hasattr(self, 'txt_info'):
                self.txt_info.config(wraplength=event.width - 70)

        self.canvas.bind('<Configure>', configurar_ancho_frame)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.bind_mouse_wheel()

        # Lógica y variables
        self.logica = ControladorWish(self.controller.obtener_datos_crudos(), self.controller.almacen_exito)
        self.v_w = tk.StringVar(value="5000")
        self.v_s = tk.StringVar(value="500")
        self.v_p = tk.StringVar(value="14.99")

        self.setup_ui()
        self.actualizar_dashboard()

    def bind_mouse_wheel(self):
        # Soporte universal para scroll con ratón
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def setup_ui(self):
        # 1. Header
        header = tk.Frame(self.scrollable_frame, bg="#2980b9", pady=15)
        header.pack(fill="x")
        tk.Label(header, text="IA PREDICTORA: ANÁLISIS ESTRATÉGICO DE LANZAMIENTO", 
                 font=("Helvetica", 12, "bold"), fg="white", bg="#2980b9").pack()

        # 2. Barra de Herramientas (Inputs)
        input_bar = tk.Frame(self.scrollable_frame, bg="#ebf5fb", pady=15)
        input_bar.pack(fill="x")
        container = tk.Frame(input_bar, bg="#ebf5fb")
        container.pack()

        fields = [("Wishlists", self.v_w), ("Seguidores", self.v_s), ("Precio $", self.v_p)]
        for i, (txt, var) in enumerate(fields):
            tk.Label(container, text=txt, font=("Arial", 8, "bold"), bg="#ebf5fb", fg="#2c3e50").grid(row=0, column=i*2, padx=5)
            tk.Entry(container, textvariable=var, width=8).grid(row=0, column=i*2+1, padx=5)

        tk.Button(container, text="SIMULAR", command=self.actualizar_dashboard, 
                  bg="#2c3e50", fg="white", font=("Arial", 8, "bold"), padx=15).grid(row=0, column=6, padx=20)

        # 3. Contenedor de Gráficos
        self.plot_container = tk.Frame(self.scrollable_frame, bg="white")
        self.plot_container.pack(fill="x", padx=10, pady=10)

        # 3 Subplots: Barras, Scatter (Benchmark) y Pie (Donut)
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(1, 3, figsize=(10, 3.8), dpi=90)
        self.fig.patch.set_facecolor('white')
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.plot_container)
        self.canvas_plot.get_tk_widget().pack(fill="x")

        # 4. Panel de Información (Diagnóstico)
        self.info_panel = tk.Frame(self.scrollable_frame, bg="white", padx=40, pady=20)
        self.info_panel.pack(fill="x")

        self.txt_info = tk.Label(
            self.info_panel, 
            text="", 
            font=("Consolas", 10), 
            bg="white", 
            fg="#34495e", 
            justify="left", 
            anchor="nw",
            wraplength=700 
        )
        self.txt_info.pack(fill="x")

    def interpretar_pesos(self, pesos):
        w, s, p = pesos['wishlists'], pesos['seguidores'], pesos['precio']
        txt = f"• Wishlists ({w:.2f}): " + ("Aportan volumen crítico al lanzamiento." if w > 0 else "Impacto inusual en este set de datos.")
        txt += f"\n• Seguidores ({s:.2f}): " + ("Refuerzan la conversión del Día 1." if s > 0 else "Baja correlación con ventas directas.")
        txt += f"\n• Precio ({p:.2f}): " + ("Actúa como barrera (a mayor precio, menos ventas)." if p < 0 else "El mercado tolera este rango de precio.")
        return txt

    def actualizar_dashboard(self):
        try:
            # Captura de datos
            w = float(self.v_w.get())
            s = float(self.v_s.get())
            p = float(self.v_p.get())

            # Predicciones
            pred_sem = self.logica.pedir_prediccion_ia(w, s, p) 
            pred_dia = int(pred_sem * 0.35) # Estimación del impacto inicial
            pesos = self.logica.ia.obtener_pesos()
            
            # Limpiar gráficos previos
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()

            # --- GRÁFICO 1: BARRAS ---
            self.ax1.bar(['Día 1', 'Semana 1'], [pred_dia, pred_sem], color=["#0799fa", "#2980b9"])
            self.ax1.set_title("Ventas Predichas", fontsize=10, fontweight='bold')
            self.ax1.set_ylabel("Unidades", fontsize=8)
            for i, v in enumerate([pred_dia, pred_sem]):
                self.ax1.text(i, v + (v*0.02), f"{int(v):,}", ha='center', fontsize=8, fontweight='bold')

            # --- GRÁFICO 2: BENCHMARK ---
            if self.logica.ia.entrenado:
                df_h = self.logica.df.select(["Wishlists", "Ventas Sem. 1", "Ventas Día 1"]).drop_nulls()
                self.ax2.scatter(df_h["Wishlists"], df_h["Ventas Sem. 1"], alpha=0.1, color="gray", s=5)
                self.ax2.scatter(df_h["Wishlists"], df_h["Ventas Día 1"], alpha=0.2, color="#3498db", s=5)
                self.ax2.scatter([w], [pred_sem], color="#8A0000", s=60, edgecolors="white", label="Tu Sem. 1")
                self.ax2.scatter([w], [pred_dia], color="#0799fa", s=60, edgecolors="white", label="Tu Día 1")
                self.ax2.set_title("Benchmark vs Mercado", fontsize=10, fontweight='bold')
                self.ax2.set_xlabel("Wishlists", fontsize=8)
                self.ax2.legend(fontsize=6, loc="upper left")

            # --- GRÁFICO 3: DONUT (EMBUDO) ---
            ventas_dia1 = pred_dia
            ventas_resto_semana = max(0, pred_sem - pred_dia)
            no_convertidos = max(0, w - pred_sem)
            
            sizes = [ventas_dia1, ventas_resto_semana, no_convertidos]
            colores = ['#0799fa', '#2980b9', '#ecf0f1']
            
            self.ax3.pie(sizes, autopct='%1.1f%%', startangle=140, colors=colores, pctdistance=0.80, textprops={'fontsize': 7})
            self.ax3.set_title("Conversión de WL", fontsize=10, fontweight='bold')
            self.ax3.add_artist(plt.Circle((0,0),0.65,fc='white')) 
            self.ax3.legend(['Día 1', 'Semana', 'Resto'], loc="lower center", bbox_to_anchor=(0.5, -0.15), fontsize=6)

            self.fig.tight_layout()
            self.canvas_plot.draw()

            # --- TEXTO DIAGNÓSTICO ---
            prob_dia1 = (pred_dia / w) * 100 if w > 0 else 0
            prob_sem1 = (pred_sem / w) * 100 if w > 0 else 0
            
            res_txt = (
                f"📊 DIAGNÓSTICO ESTRATÉGICO (Confianza R²: {self.logica.ia.r2:.4f})\n"
                f"• Ratio de conversión semanal esperado: {prob_sem1:.1f}%\n"
                f"• Concentración de ventas en el Día 1: {((pred_dia/pred_sem)*100):.1f}% del total semanal.\n\n"
                f"📝 RESUMEN DE EXPECTATIVAS:\n"
                f"De las {w:,} wishlists actuales, el modelo predice una probabilidad del {prob_dia1:.1f}% "
                f"de conversión inmediata el Día 1, lo que equivale a {pred_dia:,} ventas. "
                f"Hacia el cierre de la primera semana, el volumen total ascendería a {pred_sem:,} unidades "
                f"(conversión del {prob_sem1:.1f}%). Esto implica que {int(max(0, w-pred_sem)):,} usuarios "
                f"({max(0, 100-prob_sem1):.1f}%) no comprarán inicialmente, quedando como remanente para futuras ofertas.\n\n"
                f"🔍 ANÁLISIS DE VARIABLES:\n"
                f"{self.interpretar_pesos(pesos)}"
            )
            self.txt_info.config(text=res_txt)

        except Exception as e:
            if hasattr(self, 'txt_info'): 
                self.txt_info.config(text=f"❌ Error en la simulación: {e}", fg="red")