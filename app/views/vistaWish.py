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

        # --- 1. CONFIGURACIÓN DEL SISTEMA DE SCROLL ---
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        # Función para ajustar el ancho del contenido y el texto de las notas
        def configurar_ancho_frame(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
            # Ajuste dinámico de texto en todas las notas existentes
            for card in self.info_panel.winfo_children():
                for widget in card.winfo_children():
                    if isinstance(widget, tk.Label) and widget.cget("font").startswith("Consolas"):
                        widget.config(wraplength=event.width - 100)

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

        # --- 2. LÓGICA DE NEGOCIO Y VARIABLES ---
        self.logica = ControladorWish(self.controller.obtener_datos_crudos(), self.controller.almacen_exito)
        self.v_w = tk.StringVar(value="5000")
        self.v_s = tk.StringVar(value="500")
        self.v_p = tk.StringVar(value="14.99")

        self.setup_ui()
        self.actualizar_dashboard()

    def bind_mouse_wheel(self):
        """Soporte para scroll con rueda de ratón."""
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def setup_ui(self):
        """Construcción de la interfaz visual."""
        # Header Principal
        header = tk.Frame(self.scrollable_frame, bg="#2980b9", pady=15)
        header.pack(fill="x")
        tk.Label(header, text="IA PREDICTORA: ANÁLISIS ESTRATÉGICO DE LANZAMIENTO", 
                 font=("Helvetica", 12, "bold"), fg="white", bg="#2980b9").pack()

        # Barra de Entradas (Inputs)
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

        # Contenedor de Gráficos (Matplotlib)
        self.plot_container = tk.Frame(self.scrollable_frame, bg="white")
        self.plot_container.pack(fill="x", padx=10, pady=10)

        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(1, 3, figsize=(10, 3.8), dpi=90)
        self.fig.patch.set_facecolor('white')
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.plot_container)
        self.canvas_plot.get_tk_widget().pack(fill="x")

        # Panel de Notas (Información Diagnóstica)
        self.info_panel = tk.Frame(self.scrollable_frame, bg="white", padx=40, pady=20)
        self.info_panel.pack(fill="x")

    def interpretar_pesos(self, pesos):
        """Genera la narrativa técnica sobre la influencia de las variables."""
        w, s, p = pesos['wishlists'], pesos['seguidores'], pesos['precio']
        
        def get_status(val, inv=False):
            if inv: return "✅ FAVORABLE" if val < 0 else "⚠️ CRÍTICO"
            return "✅ ALTO" if val > 0 else "⚠️ BAJO"

        txt = (
            f"📈 WISHLISTS: {get_status(w)}\n"
            f"   Impacto: {w:.2f} - {'Volumen principal de conversión.' if w > 0 else 'Baja correlación histórica.'}\n\n"
            f"👥 SEGUIDORES: {get_status(s)}\n"
            f"   Impacto: {s:.2f} - {'Comunidad fidelizada detectada.' if s > 0 else 'Tracción social insuficiente.'}\n\n"
            f"💰 PRECIO: {get_status(p, True)}\n"
            f"   Impacto: {p:.2f} - {'Rango óptimo para el mercado.' if p < 0 else 'Precio actúa como resistencia.'}"
        )
        return txt

    def actualizar_dashboard(self):
        """Ejecuta la predicción IA y refresca todos los componentes visuales."""
        try:
            # 1. Obtención de datos e IA
            w = float(self.v_w.get())
            s = float(self.v_s.get())
            p = float(self.v_p.get())

            pred_sem = self.logica.pedir_prediccion_ia(w, s, p) 
            pred_dia = int(pred_sem * 0.35) 
            pesos = self.logica.ia.obtener_pesos()
            
            # --- 2. RENDERIZADO DE GRÁFICOS (OPTIMIZADO) ---
            self.ax1.clear()
            self.ax2.clear()
            self.ax3.clear()

            # --- GRÁFICO 1: COMPARATIVA DE LANZAMIENTO (BARRAS) ---
            # Usamos un degradado visual para diferenciar el impacto inicial del acumulado
            bars = self.ax1.bar(['Día 1', 'Semana 1'], [pred_dia, pred_sem], 
                                color=["#3498db", "#2980b9"], edgecolor="#2c3e50", linewidth=0.5)
            self.ax1.set_title("PROYECCIÓN DE VENTAS", fontsize=9, fontweight='bold', pad=10)
            self.ax1.set_ylabel("Unidades", fontsize=8)
            self.ax1.tick_params(axis='both', labelsize=8)
            self.ax1.grid(axis='y', linestyle='--', alpha=0.3) # Rejilla sutil para lectura

            # Etiquetas de datos automáticas
            for bar in bars:
                height = bar.get_height()
                self.ax1.text(bar.get_x() + bar.get_width()/2., height + (height*0.01),
                             f"{int(height):,}", ha='center', va='bottom', 
                             fontsize=8, fontweight='bold', color="#2c3e50")

            # --- GRÁFICO 2: BENCHMARK ESTRATÉGICO (SCATTER) ---
            if self.logica.ia.entrenado:
                df_h = self.logica.df.select(["Wishlists", "Ventas Sem. 1", "Ventas Día 1"]).drop_nulls()
                
                # Capas de Mercado (Fondo): Mostramos la "nube" histórica de otros juegos
                self.ax2.scatter(df_h["Wishlists"], df_h["Ventas Sem. 1"], 
                                 alpha=0.05, color="#2c3e50", s=10, label="Mercado Sem. 1")
                self.ax2.scatter(df_h["Wishlists"], df_h["Ventas Día 1"], 
                                 alpha=0.1, color="#3498db", s=8, label="Mercado Día 1")
                
                # Capas de Predicción (Frente): Tu posición estimada
                self.ax2.scatter([w], [pred_sem], color="#e74c3c", s=80, 
                                 edgecolors="white", linewidth=1.5, label="TU SEMANA 1", zorder=5)
                self.ax2.scatter([w], [pred_dia], color="#f1c40f", s=80, 
                                 edgecolors="#2c3e50", linewidth=1.5, label="TU DÍA 1", zorder=5)
                
                self.ax2.set_title("BENCHMARK VS MERCADO", fontsize=9, fontweight='bold', pad=10)
                self.ax2.set_xlabel("Wishlists", fontsize=8)
                self.ax2.legend(fontsize=7, loc="upper left", frameon=True, shadow=True)
                self.ax2.tick_params(labelsize=8)

            # --- GRÁFICO 3: EMBUDO DE CONVERSIÓN (DONUT) ---
            ventas_dia1 = pred_dia
            ventas_resto = max(0, pred_sem - pred_dia)
            no_compra = max(0, w - pred_sem)
            
            sizes = [ventas_dia1, ventas_resto, no_compra]
            labels = ['Día 1', 'Resto Sem.', 'Sin Conv.']
            colores = ['#3498db', '#2980b9', '#ecf0f1']
            
            # Dibujo de la torta con porcentajes descriptivos
            wedges, texts, autotexts = self.ax3.pie(
                sizes, 
                autopct='%1.1f%%', 
                startangle=140, 
                colors=colores, 
                pctdistance=0.75,
                textprops={'fontsize': 7, 'fontweight': 'bold'}
            )
            
            # Estilo Donut (Círculo blanco central)
            self.ax3.add_artist(plt.Circle((0,0), 0.60, fc='white'))
            self.ax3.set_title("EFICIENCIA DE WL", fontsize=9, fontweight='bold', pad=10)
            
            # Leyenda personalizada inferior
            self.ax3.legend(wedges, labels, title="Segmentos", loc="lower center", 
                            bbox_to_anchor=(0.5, -0.15), fontsize=7, frameon=False)

            self.fig.tight_layout()
            self.canvas_plot.draw()


            # 3. Construcción de Notas Estilizadas
            for widget in self.info_panel.winfo_children():
                widget.destroy()

            prob_dia1 = (pred_dia / w) * 100 if w > 0 else 0
            prob_sem1 = (pred_sem / w) * 100 if w > 0 else 0

            notas_data = [
                {
                    "t": f"MÉTRICAS CLAVE (Confianza R²: {self.logica.ia.r2:.4f})",
                    "c": f"• Conversión Semanal: {prob_sem1:.1f}% de la audiencia.\n• Eficacia Día 1: {((pred_dia/pred_sem)*100):.1f}% del lanzamiento.",
                    "bg": "#f8f9f9"
                },
                {
                    "t": "RESUMEN EJECUTIVO",
                    "c": f"• Proyección Día 1: {pred_dia:,} ventas.\n• Cierre Semana 1: {pred_sem:,} unidades.\n• Remanente: {int(max(0, w-pred_sem)):,} usuarios a futuro.",
                    "bg": "#ebf5fb"
                },
                {
                    "t": "ANÁLISIS DE ATRIBUTOS",
                    "c": self.interpretar_pesos(pesos),
                    "bg": "#fef9e7"
                }
            ]

            for nota in notas_data:
                card = tk.Frame(self.info_panel, bg=nota["bg"], padx=15, pady=10, 
                                highlightbackground="#d5dbdb", highlightthickness=1)
                card.pack(fill="x", pady=5)
                
                tk.Label(card, text=nota["t"], font=("Arial", 9, "bold"), 
                         bg=nota["bg"], fg="#2c3e50", anchor="w").pack(fill="x")
                
                tk.Label(card, text=nota["c"], font=("Consolas", 9), 
                         bg=nota["bg"], fg="#566573", justify="left", anchor="w",
                         wraplength=700).pack(fill="x", pady=(5,0))

        except Exception as e:
            # Gestión de errores visual
            error_card = tk.Frame(self.info_panel, bg="#fdedec", padx=15, pady=10)
            error_card.pack(fill="x")
            tk.Label(error_card, text=f"❌ Error en Simulación: {e}", bg="#fdedec", fg="#cb4335").pack()