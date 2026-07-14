import tkinter as tk
from tkinter import ttk


class PestanaTRI:
    def __init__(self, app, tab, titulo_modulo):
        self.app = app
        self.tab = tab
        self.titulo_modulo = titulo_modulo

        self.crear_interfaz()

    def crear_interfaz(self):
        frame_encabezado = ttk.LabelFrame(
            self.tab,
            text=" Teoría de Respuesta al Ítem (TRI) ",
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
                "Estimación de dificultad, discriminación, adivinación "
                "y detección de reactivos con Flag K."
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

        self.app.btn_ejecutar_tri = ttk.Button(
            frame_encabezado,
            text="Ejecutar análisis TRI",
            command=self.app.analizar_tri
        )
        self.app.btn_ejecutar_tri.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=5,
            pady=5
        )

        self.app.btn_exportar_tri = ttk.Button(
            frame_encabezado,
            text="Exportar resultados TRI",
            command=self.app.exportar_resultados_tri,
            state="disabled"
        )
        self.app.btn_exportar_tri.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=5,
            pady=5
        )

        self.app.btn_limpiar_tri = ttk.Button(
            frame_encabezado,
            text="Limpiar resultados TRI",
            command=self.app.limpiar_resultados_tri
        )
        self.app.btn_limpiar_tri.grid(
            row=2,
            column=2,
            sticky="ew",
            padx=5,
            pady=5
        )

        frame_encabezado.columnconfigure((0, 1, 2), weight=1)

        # Resumen TRI
        frame_resumen = ttk.LabelFrame(
            self.tab,
            text=" Resumen general ",
            padding=10
        )
        frame_resumen.pack(fill="x", padx=15, pady=5)

        self.app.var_tri_alumnos = tk.StringVar(value="-")
        self.app.var_tri_reactivos = tk.StringVar(value="-")
        self.app.var_tri_media_a = tk.StringVar(value="-")
        self.app.var_tri_media_b = tk.StringVar(value="-")
        self.app.var_tri_media_c = tk.StringVar(value="-")
        self.app.var_tri_k = tk.StringVar(value="-")

        campos = [
            ("Alumnos", self.app.var_tri_alumnos),
            ("Reactivos", self.app.var_tri_reactivos),
            ("Media a", self.app.var_tri_media_a),
            ("Media b", self.app.var_tri_media_b),
            ("Media c", self.app.var_tri_media_c),
            ("Reactivos con Flag K", self.app.var_tri_k)
        ]

        for indice, (nombre, variable) in enumerate(campos):
            fila = indice // 3
            columna = (indice % 3) * 2

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
                padx=(2, 20),
                pady=5
            )

        # Tabla TRI
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
            "p",
            "r",
            "a",
            "b",
            "c",
            "flag"
        )

        self.app.tabla_tri = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            height=14
        )

        encabezados = {
            "item": "Reactivo",
            "correcta": "Correcta",
            "p": "P",
            "r": "R",
            "a": "a",
            "b": "b",
            "c": "c",
            "flag": "Flag"
        }

        anchos = {
            "item": 90,
            "correcta": 75,
            "p": 75,
            "r": 75,
            "a": 75,
            "b": 75,
            "c": 75,
            "flag": 100
        }

        for columna in columnas:
            self.app.tabla_tri.heading(
                columna,
                text=encabezados[columna]
            )
            self.app.tabla_tri.column(
                columna,
                width=anchos[columna],
                anchor="center"
            )

        scroll_y = ttk.Scrollbar(
            frame_tabla,
            orient="vertical",
            command=self.app.tabla_tri.yview
        )

        scroll_x = ttk.Scrollbar(
            frame_tabla,
            orient="horizontal",
            command=self.app.tabla_tri.xview
        )

        self.app.tabla_tri.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        self.app.tabla_tri.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        frame_tabla.rowconfigure(0, weight=1)
        frame_tabla.columnconfigure(0, weight=1)

        self.app.tabla_tri.tag_configure(
            "flag_k",
            background="#FFDADA"
        )