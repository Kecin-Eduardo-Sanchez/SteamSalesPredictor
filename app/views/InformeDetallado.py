import tkinter as tk
from tkinter import ttk, messagebox
import polars as pl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
# Importamos la lógica directamente para evitar el AttributeError
from app.controllers.ActualidadWish import ControladorWish

class InformeDetallado(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f4f7f6")

        # 1. INSTANCIAMOS LA LÓGICA DE FORMA INDEPENDIENTE
        # Esto evita el error 'MainController' object has no attribute 'vista_wish'
        self.df_completo = self.controller.obtener_datos_crudos()
        self.logica_ia = ControladorWish(self.df_completo, self.controller.almacen_exito)

        # 2. VARIABLES PARA LOS INPUTS
        self.v_w = tk.StringVar(value="5000")
        self.v_s = tk.StringVar(value="500")
        self.v_p = tk.StringVar(value="14.99")
        self.v_inv = tk.StringVar(value="5000")
        
        # Obtener lista de géneros del dataset para el combobox
        try:
            self.lista_generos = self.df_completo.select(pl.col("Género (Tag)")).unique().sort("Género (Tag)").to_series().to_list()
        except:
            self.lista_generos = ["Indie", "Action", "Adventure", "RPG", "Strategy"]
        
        self.v_gen = tk.StringVar(value=self.lista_generos[0] if self.lista_generos else "")

        self.setup_ui()
        self.actualizar_analisis_total()

    def setup_ui(self):
        # --- HEADER ---
        header = tk.Frame(self, bg="#2c3e50", pady=15)
        header.pack(fill="x")
        tk.Label(header, text="SIMULADOR DE RENTABILIDAD Y ESTRATEGIA", 
                 font=("Helvetica", 14, "bold"), fg="#ecf0f1", bg="#2c3e50").pack()

        # --- PANEL DE INPUTS (La "Consola") ---
        input_panel = tk.Frame(self, bg="#dfe6e9", pady=15, padx=20)
        input_panel.pack(fill="x")
        
        lbl_style = {"font": ("Arial", 8, "bold"), "bg": "#dfe6e9", "fg": "#2d3436"}
        
        # Columna 1: Mercado
        tk.Label(input_panel, text="GÉNERO:", **lbl_style).grid(row=0, column=0, sticky="e", padx=5)
        self.combo_gen = ttk.Combobox(input_panel, textvariable=self.v_gen, values=self.lista_generos, state="readonly", width=15)
        self.combo_gen.grid(row=0, column=1, padx=5)

        tk.Label(input_panel, text="WISHLISTS:", **lbl_style).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(input_panel, textvariable=self.v_w, width=18).grid(row=1, column=1)

        # Columna 2: Producto
        tk.Label(input_panel, text="PRECIO ($):", **lbl_style).grid(row=0, column=2, sticky="e", padx=5)
        tk.Entry(input_panel, textvariable=self.v_p, width=15).grid(row=0, column=3)

        tk.Label(input_panel, text="SEGUIDORES:", **lbl_style).grid(row=1, column=2, sticky="e", padx=5)
        tk.Entry(input_panel, textvariable=self.v_s, width=15).grid(row=1, column=3)

        # Columna 3: Inversión
        tk.Label(input_panel, text="INVERSIÓN TOTAL ($):", **lbl_style).grid(row=0, column=4, sticky="e", padx=5)
        tk.Entry(input_panel, textvariable=self.v_inv, width=15).grid(row=0, column=5)

        # Botones
        btn_f = tk.Frame(input_panel, bg="#dfe6e9")
        btn_f.grid(row=0, column=6, rowspan=2, padx=20)
        
        tk.Button(btn_f, text="RECALCULAR", command=self.actualizar_analisis_total, 
                  bg="#16a085", fg="white", font=("Arial", 9, "bold"), width=15, pady=5).pack(pady=2)
        tk.Button(btn_f, text="GENERAR PDF", command=self.exportar_pdf, 
                  bg="#2c3e50", fg="white", font=("Arial", 9, "bold"), width=15, pady=5).pack(pady=2)

        # --- ÁREA DE NOTAS (SCROLL) ---
        self.canvas = tk.Canvas(self, bg="#f4f7f6", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.root_frame = tk.Frame(self.canvas, bg="#f4f7f6")
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.root_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.root_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=20)
        self.scrollbar.pack(side="right", fill="y")

    def actualizar_analisis_total(self):
        """Mezcla la lógica de VistaWish (IA) y Vista2 (Género)."""
        for widget in self.root_frame.winfo_children(): widget.destroy()

        try:
            # 1. Obtener valores de los inputs
            w = float(self.v_w.get())
            s = float(self.v_s.get())
            p = float(self.v_p.get())
            inv = float(self.v_inv.get())
            gen_sel = self.v_gen.get()

            # 2. Lógica de Género (Ajustado a tus columnas reales)
            df_gen = self.df_completo.filter(pl.col("Género (Tag)") == gen_sel)
            
            # NOTA: Cambiamos "Semana 1" por "Ventas Sem. 1" que es tu columna real
            punto_dulce_data = df_gen.group_by("Precio (USD)").agg(
                pl.col("Ventas Sem. 1").sum().alias("S")
            ).sort("S", descending=True)
            
            punto_dulce = float(punto_dulce_data[0, "Precio (USD)"]) if not punto_dulce_data.is_empty() else 0.0

            # 3. Lógica de Predicción (IA)
            ventas_est = self.logica_ia.pedir_prediccion_ia(w, s, p)
            
            # 4. Cálculos Financieros
            ingreso_bruto = ventas_est * p
            # Cálculo de recuperación: Steam (30%) + Impuestos/Fees aproximados (10%) = ~40% menos
            # Vamos a ser conservadores y usar el 60% neto para el desarrollador
            ingreso_neto = ingreso_bruto * 0.60 
            balance = ingreso_neto - inv
            recuperado_pct = (ingreso_neto / inv * 100) if inv > 0 else 0

            # --- RENDERIZADO DE NOTAS ---
            
            # Nota 1: Análisis de Mercado
            diff_p = p - punto_dulce
            status_p = "OPTIMO" if abs(diff_p) < 2 else "DESVIADO"
            txt_gen = (f"Género: {gen_sel} | Punto Dulce: ${punto_dulce:.2f}\n"
                       f"Tu precio: ${p:.2f} ({status_p})\n"
                       f"Diferencia: {diff_p:+.2f} USD respecto al líder de ventas.")
            self.agregar_nota("ESTRATEGIA DE PRECIOS", txt_gen, "#f39c12")

            # Nota 2: Predicción IA
            txt_ia = (f"Ventas estimadas (Semana 1): {int(ventas_est):,} unidades.\n"
                      f"Ingreso Bruto: ${ingreso_bruto:,.2f} USD.\n"
                      f"Ingreso Neto Estimado (Post-Steam/Tax): ${ingreso_neto:,.2f} USD.")
            self.agregar_nota("PROYECCIÓN DE VENTAS", txt_ia, "#2980b9")

            # Nota 3: Rentabilidad (La clave que pediste)
            color_roi = "#27ae60" if balance > 0 else "#e74c3c"
            status_fin = "INVERSIÓN RECUPERADA ✅" if balance > 0 else "INVERSIÓN NO RECUPERADA ⚠️"
            txt_roi = (f"Resultado: {status_fin}\n"
                       f"Balance Neto: {balance:,.2f} USD.\n"
                       f"Porcentaje de recuperación: {recuperado_pct:.1f}% en 7 días.")
            self.agregar_nota("CÁLCULO DE RETORNO (ROI)", txt_roi, color_roi)

        except Exception as e:
            self.agregar_nota("ERROR DE DATOS", f"Detalle técnico: {e}", "#c0392b")

    def agregar_nota(self, titulo, contenido, color):
        container = tk.Frame(self.root_frame, bg="white", padx=20, pady=15, highlightthickness=1, highlightbackground="#dcdde1")
        container.pack(fill="x", pady=8, padx=20)
        tk.Frame(container, bg=color, width=5).pack(side="left", fill="y")
        f = tk.Frame(container, bg="white", padx=15)
        f.pack(side="left", fill="both")
        tk.Label(f, text=titulo, font=("Arial", 10, "bold"), fg=color, bg="white").pack(anchor="w")
        tk.Label(f, text=contenido, font=("Segoe UI", 9), justify="left", bg="white").pack(anchor="w", pady=5)

    def exportar_pdf(self):
        """Genera un informe detallado con todas las métricas de mercado, IA y finanzas."""
        fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        filename = f"Informe_Estrategico_{self.v_gen.get()}_{datetime.now().strftime('%H%M%S')}.pdf"
        
        try:
            # 1. Obtención de datos actuales para el reporte
            w = float(self.v_w.get())
            s = float(self.v_s.get())
            p = float(self.v_p.get())
            inv = float(self.v_inv.get())
            gen_sel = self.v_gen.get()
            
            # Re-calculamos para asegurar que el PDF tenga lo último visible
            ventas_est = self.logica_ia.pedir_prediccion_ia(w, s, p)
            bruto = ventas_est * p
            neto = bruto * 0.60 # Tu lógica de margen neto
            balance = neto - inv
            roi = (neto / inv * 100) if inv > 0 else 0
            
            # Obtener punto dulce para el PDF
            df_gen = self.df_completo.filter(pl.col("Género (Tag)") == gen_sel)
            punto_dulce_data = df_gen.group_by("Precio (USD)").agg(pl.col("Ventas Sem. 1").sum().alias("S")).sort("S", descending=True)
            punto_dulce = float(punto_dulce_data[0, "Precio (USD)"]) if not punto_dulce_data.is_empty() else 0.0

            # 2. Configuración del documento ReportLab
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            
            # --- ENCABEZADO ---
            c.setFillColorRGB(0.17, 0.24, 0.31) # Color azul oscuro
            c.rect(0, height - 80, width, 80, fill=1)
            c.setFillColorRGB(1, 1, 1)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 45, "INFORME ESTRATÉGICO DE LANZAMIENTO")
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 60, f"Simulación generada por IA el {fecha_str}")

            # --- SECCIÓN 1: CONFIGURACIÓN INICIAL ---
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, height - 110, "1. PARÁMETROS DEL PROYECTO")
            c.setFont("Helvetica", 10)
            c.drawString(70, height - 130, f"• Género Principal: {gen_sel}")
            c.drawString(70, height - 145, f"• Tracción Acumulada: {int(w):,} Wishlists / {int(s):,} Seguidores")
            c.drawString(70, height - 160, f"• Precio de Venta: ${p:.2f} USD")
            c.drawString(70, height - 175, f"• Inversión de Desarrollo: ${inv:,.2f} USD")

            # --- SECCIÓN 2: ANÁLISIS DE MERCADO ---
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, height - 210, "2. COMPETITIVIDAD Y POSICIONAMIENTO")
            c.setFont("Helvetica", 10)
            c.drawString(70, height - 230, f"• Punto Dulce del Género: ${punto_dulce:.2f} USD")
            diff = p - punto_dulce
            txt_p = f"Posicionado ${abs(diff):.2f} " + ("por encima" if diff > 0 else "por debajo") + " del óptimo."
            c.drawString(70, height - 245, f"• Análisis de Precio: {txt_p}")

            # --- SECCIÓN 3: PREDICCIÓN DE IA ---
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, height - 280, "3. PROYECCIÓN DE VENTAS (SEMANA 1)")
            c.setFont("Helvetica", 10)
            c.drawString(70, height - 300, f"• Estimación de Ventas: {int(ventas_est):,} unidades")
            c.drawString(70, height - 315, f"• Tasa de Conversión: {(ventas_est/w*100):.1f}% de las Wishlists")
            c.drawString(70, height - 330, f"• Ingreso Bruto Estimado: ${bruto:,.2f} USD")

            # --- SECCIÓN 4: RESULTADOS FINANCIEROS (ROI) ---
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, height - 370, "4. VIABILIDAD ECONÓMICA")
            c.setFont("Helvetica", 10)
            c.drawString(70, height - 390, f"• Ingreso Neto Real (Estimado 60%): ${neto:,.2f} USD")
            c.drawString(70, height - 405, f"• Balance Neto (Semana 1): ${balance:,.2f} USD")
            
            # Barra de progreso visual para el ROI
            c.drawString(70, height - 420, f"• Recuperación de Inversión: {roi:.1f}%")
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.rect(70, height - 440, 200, 15)
            progress = min(roi * 2, 200) # Máximo 200px para el 100%
            if balance > 0: c.setFillColorRGB(0.15, 0.68, 0.37) 
            else: c.setFillColorRGB(0.75, 0.22, 0.16)
            c.rect(70, height - 440, progress, 15, fill=1)

            # --- SECCIÓN 5: VEREDICTO ---
            c.setFillColorRGB(0.17, 0.24, 0.31)
            c.rect(50, height - 520, 500, 50, fill=0)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(60, height - 485, "VEREDICTO ESTRATÉGICO:")
            c.setFont("Helvetica-Oblique", 10)
            
            if balance > 0:
                veredicto = "EL PROYECTO ES ALTAMENTE VIABLE. Se espera recuperar la inversión en la primera semana."
            elif roi > 75:
                veredicto = "VIABILIDAD MODERADA. Cerca del punto de equilibrio; optimizar marketing para cerrar la brecha."
            else:
                veredicto = "RIESGO FINANCIERO DETECTADO. Se recomienda revisar el precio o aumentar la base de Wishlists."
            
            c.drawString(60, height - 505, veredicto)

            # Pie de página
            c.setFillColorRGB(0.5, 0.5, 0.5)
            c.setFont("Helvetica", 8)
            c.drawCentredString(width/2, 30, "Este informe es una proyección basada en datos históricos y algoritmos de IA. Los resultados reales pueden variar.")

            c.save()
            messagebox.showinfo("PDF Generado", f"Informe guardado como: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error al exportar", f"No se pudo generar el PDF: {e}")