import tkinter as tk
from tkinter import ttk


class PestanaReporte:
    def __init__(self, app, tab):
        self.app = app
        self.tab = tab

        self.crear_interfaz()

    def crear_interfaz(self):
        frame_encabezado = ttk.LabelFrame(
            self.tab,
            text=" Dictamen Post Aplicación ",
            padding=15
        )
        frame_encabezado.pack(fill="x", padx=15, pady=10)

        ttk.Label(
            frame_encabezado,
            text="Generación del reporte y dictamen final",
            font=("Arial", 14, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=5,
            pady=(0, 5)
        )

        ttk.Label(
            frame_encabezado,
            text=(
                "Integra estadísticas generales, reactivos identificados, "
                "porcentaje de aprobación y resultados posteriores al abono."
            )
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="w",
            padx=5,
            pady=(0, 10)
        )

        ttk.Button(
            frame_encabezado,
            text="Vista previa del dictamen",
            command=self.app.mostrar_vista_previa_reporte
        ).grid(
            row=2,
            column=0,
            padx=5,
            pady=5,
            sticky="ew"
        )

        self.app.btn_generar_reporte = ttk.Button(
            frame_encabezado,
            text="Generar dictamen Word",
            command=self.app.generar_reporte,
            state="disabled"
        )
        self.app.btn_generar_reporte.grid(
            row=2,
            column=1,
            padx=5,
            pady=5,
            sticky="ew"
        )

        ttk.Button(
            frame_encabezado,
            text="Limpiar vista previa",
            command=self.app.limpiar_vista_previa_reporte
        ).grid(
            row=2,
            column=2,
            padx=5,
            pady=5,
            sticky="ew"
        )

        frame_encabezado.columnconfigure((0, 1, 2), weight=1)

        frame_vista = ttk.LabelFrame(
            self.tab,
            text=" Vista previa ",
            padding=10
        )
        frame_vista.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        scroll = ttk.Scrollbar(frame_vista)
        scroll.pack(side="right", fill="y")

        self.app.texto_reporte = tk.Text(
            frame_vista,
            font=("Consolas", 10),
            wrap="word",
            yscrollcommand=scroll.set
        )
        self.app.texto_reporte.pack(
            fill="both",
            expand=True
        )

        scroll.configure(
            command=self.app.texto_reporte.yview
        )