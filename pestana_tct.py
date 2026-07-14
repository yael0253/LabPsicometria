import tkinter as tk
from tkinter import ttk


class PestanaTCT:
    def __init__(self, app, tab, titulo_modulo):
        self.app = app
        self.tab = tab
        self.titulo_modulo = titulo_modulo

        self.crear_interfaz()

    def crear_interfaz(self):
        frame_encabezado = ttk.LabelFrame(
            self.tab,
            text=" Análisis de Teoría Clásica (TCT) ",
            padding=15
        )
        frame_encabezado.pack(fill="x", padx=15, pady=10)

        ttk.Label(
            frame_encabezado,
            text=self.titulo_modulo,
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
                "Calcula dificultad, discriminación, fiabilidad "
                "y reactivos con Flag K."
            ),
            font=("Arial", 10)
        ).grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="w",
            padx=5,
            pady=(0, 10)
        )

        self.app.btn_ejecutar_tct = ttk.Button(
            frame_encabezado,
            text="Ejecutar análisis TCT",
            command=self.app.analizar_tct
        )
        self.app.btn_ejecutar_tct.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=5,
            pady=5
        )

        self.app.btn_exportar_tct = ttk.Button(
            frame_encabezado,
            text="Exportar resultados TCT",
            command=self.app.exportar_resultados_tct,
            state="disabled"
        )
        self.app.btn_exportar_tct.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=5,
            pady=5
        )

        self.app.btn_limpiar_tct = ttk.Button(
            frame_encabezado,
            text="Limpiar resultados TCT",
            command=self.app.limpiar_resultados_tct
        )
        self.app.btn_limpiar_tct.grid(
            row=2,
            column=2,
            sticky="ew",
            padx=5,
            pady=5
        )

        frame_encabezado.columnconfigure((0, 1, 2), weight=1)

        # Resumen
        frame_resumen = ttk.LabelFrame(
            self.tab,
            text=" Resumen general ",
            padding=10
        )
        frame_resumen.pack(fill="x", padx=15, pady=5)

        self.app.var_tct_alumnos = tk.StringVar(value="-")
        self.app.var_tct_reactivos = tk.StringVar(value="-")
        self.app.var_tct_media = tk.StringVar(value="-")
        self.app.var_alpha = tk.StringVar(value="-")
        self.app.var_tct_p = tk.StringVar(value="-")
        self.app.var_tct_rpbis = tk.StringVar(value="-")
        self.app.var_tct_k = tk.StringVar(value="-")

        campos = [
            ("Alumnos", self.app.var_tct_alumnos),
            ("Reactivos", self.app.var_tct_reactivos),
            ("Media de aciertos", self.app.var_tct_media),
            ("Alfa de Cronbach", self.app.var_alpha),
            ("Media (P)", self.app.var_tct_p),
            ("Media (Rpbis)", self.app.var_tct_rpbis),
            ("Reactivos con Flag K", self.app.var_tct_k)
        ]

        for indice, (nombre, variable) in enumerate(campos):
            fila = indice // 4
            columna = (indice % 4) * 2

            ttk.Label(
                frame_resumen,
                text=f"{nombre}:",
                font=("Arial", 9, "bold")
            ).grid(
                row=fila,
                column=columna,
                sticky="e",
                padx=(5, 2),
                pady=5
            )

            ttk.Label(
                frame_resumen,
                textvariable=variable
            ).grid(
                row=fila,
                column=columna + 1,
                sticky="w",
                padx=(2, 15),
                pady=5
            )

        # Tabla
        frame_tabla = ttk.LabelFrame(
            self.tab,
            text=" Resultados por reactivo ",
            padding=10
        )
        frame_tabla.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        columnas = (
            "item",
            "correcta",
            "n",
            "p",
            "rpbis",
            "alpha_sin",
            "flag"
        )

        self.app.tabla_tct = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            height=14
        )

        encabezados = {
            "item": "Reactivo",
            "correcta": "Correcta",
            "n": "N",
            "p": "P",
            "rpbis": "Rpbis",
            "alpha_sin": "Alpha sin ítem",
            "flag": "Flag"
        }

        anchos = {
            "item": 90,
            "correcta": 75,
            "n": 70,
            "p": 80,
            "rpbis": 90,
            "alpha_sin": 110,
            "flag": 70
        }

        for columna in columnas:
            self.app.tabla_tct.heading(
                columna,
                text=encabezados[columna]
            )
            self.app.tabla_tct.column(
                columna,
                width=anchos[columna],
                anchor="center"
            )

        scroll_vertical = ttk.Scrollbar(
            frame_tabla,
            orient="vertical",
            command=self.app.tabla_tct.yview
        )

        scroll_horizontal = ttk.Scrollbar(
            frame_tabla,
            orient="horizontal",
            command=self.app.tabla_tct.xview
        )

        self.app.tabla_tct.configure(
            yscrollcommand=scroll_vertical.set,
            xscrollcommand=scroll_horizontal.set
        )

        self.app.tabla_tct.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scroll_vertical.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        scroll_horizontal.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        frame_tabla.rowconfigure(0, weight=1)
        frame_tabla.columnconfigure(0, weight=1)

        self.app.tabla_tct.tag_configure(
            "flag_k",
            background="#FFDADA"
        )