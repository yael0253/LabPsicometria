import tkinter as tk
from tkinter import ttk


class PestanaETL:
    def __init__(self, app, tab):
        self.app = app
        self.tab = tab

        self.crear_interfaz()

    def crear_interfaz(self):
        frame_acciones = ttk.LabelFrame(
            self.tab,
            text=" Acciones de Carga e Integración ",
            padding=15
        )
        frame_acciones.pack(fill="x", padx=15, pady=10)

        img_excel = self.app.referencias_imagenes.get("excel", "")
        img_pdf = self.app.referencias_imagenes.get("pdf", "")

        ttk.Button(
            frame_acciones,
            text=" Seleccionar archivo(s) Excel",
            image=img_excel,
            compound="left",
            command=self.app.seleccionar_archivos
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=5,
            sticky="ew"
        )

        ttk.Button(
            frame_acciones,
            text=" Seleccionar PDF de análisis",
            image=img_pdf,
            compound="left",
            command=self.app.seleccionar_pdf
        ).grid(
            row=0,
            column=1,
            padx=10,
            pady=5,
            sticky="ew"
        )

        ttk.Button(
            frame_acciones,
            text="⚙ Leer, separar y unir datos",
            command=self.app.leer_y_separar_datos
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=5,
            sticky="ew"
        )

        ttk.Button(
            frame_acciones,
            text="💾 Generar CONTROL y DAT",
            command=self.app.generar_archivos_control_y_dat
        ).grid(
            row=0,
            column=3,
            padx=10,
            pady=5,
            sticky="ew"
        )

        frame_acciones.columnconfigure((0, 1, 2, 3), weight=1)

        # Archivos cargados
        frame_archivos = ttk.LabelFrame(
            self.tab,
            text=" Archivos cargados ",
            padding=15
        )
        frame_archivos.pack(fill="x", padx=15, pady=10)

        self.app.lista_archivos = tk.Listbox(
            frame_archivos,
            height=6,
            font=("Consolas", 10)
        )
        self.app.lista_archivos.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=10,
            pady=5
        )

        scroll_archivos = ttk.Scrollbar(
            frame_archivos,
            orient="vertical",
            command=self.app.lista_archivos.yview
        )
        scroll_archivos.grid(
            row=0,
            column=4,
            sticky="ns",
            pady=5
        )

        self.app.lista_archivos.configure(
            yscrollcommand=scroll_archivos.set
        )

        ttk.Button(
            frame_archivos,
            text="🗑 Eliminar seleccionado",
            command=self.app.eliminar_archivo_seleccionado
        ).grid(
            row=1,
            column=2,
            padx=10,
            pady=5,
            sticky="ew"
        )

        ttk.Button(
            frame_archivos,
            text="🧹 Limpiar lista",
            command=self.app.limpiar_archivos
        ).grid(
            row=1,
            column=3,
            padx=10,
            pady=5,
            sticky="ew"
        )

        frame_archivos.columnconfigure((0, 1, 2, 3), weight=1)

        # Consola
        frame_consola = ttk.LabelFrame(
            self.tab,
            text=" Consola de Resultados y Diagnóstico ",
            padding=10
        )
        frame_consola.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        scroll_consola = ttk.Scrollbar(frame_consola)
        scroll_consola.pack(side="right", fill="y")

        self.app.texto_resultado = tk.Text(
            frame_consola,
            font=("Consolas", 10),
            yscrollcommand=scroll_consola.set
        )
        self.app.texto_resultado.pack(
            fill="both",
            expand=True
        )

        scroll_consola.configure(
            command=self.app.texto_resultado.yview
        )