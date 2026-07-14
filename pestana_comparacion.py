import tkinter as tk
from tkinter import ttk


class PestanaComparacion:
    def __init__(self, app, tab):
        self.app = app
        self.tab = tab

        self.crear_interfaz()

    def crear_interfaz(self):
        frame_acciones = ttk.LabelFrame(
            self.tab,
            text=" Comparación TCT vs TRI ",
            padding=15
        )
        frame_acciones.pack(fill="x", padx=15, pady=10)

        ttk.Label(
            frame_acciones,
            text=(
                "Compara los reactivos con Flag K en ambos análisis "
                "y determina cuáles deben abonarse."
            ),
            font=("Arial", 10)
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=5,
            pady=(0, 10)
        )

        self.app.btn_comparar = ttk.Button(
            frame_acciones,
            text="Comparar resultados",
            command=self.app.comparar_resultados
        )
        self.app.btn_comparar.grid(
            row=1,
            column=0,
            padx=5,
            pady=5,
            sticky="ew"
        )

        self.app.btn_aplicar_abonos = ttk.Button(
            frame_acciones,
            text="Aplicar abonos",
            command=self.app.aplicar_abonos,
            state="disabled"
        )
        self.app.btn_aplicar_abonos.grid(
            row=1,
            column=1,
            padx=5,
            pady=5,
            sticky="ew"
        )

        ttk.Button(
            frame_acciones,
            text="Limpiar comparación",
            command=self.app.limpiar_comparacion
        ).grid(
            row=1,
            column=2,
            padx=5,
            pady=5,
            sticky="ew"
        )

        frame_acciones.columnconfigure((0, 1, 2), weight=1)

        frame_resumen = ttk.LabelFrame(
            self.tab,
            text=" Resumen ",
            padding=10
        )
        frame_resumen.pack(fill="x", padx=15, pady=5)

        self.app.var_comp_k_tct = tk.StringVar(value="-")
        self.app.var_comp_k_tri = tk.StringVar(value="-")
        self.app.var_comp_abonar = tk.StringVar(value="-")

        campos = [
            ("K en TCT", self.app.var_comp_k_tct),
            ("K en TRI", self.app.var_comp_k_tri),
            ("Reactivos a abonar", self.app.var_comp_abonar)
        ]

        for indice, (nombre, variable) in enumerate(campos):
            ttk.Label(
                frame_resumen,
                text=f"{nombre}:",
                font=("Arial", 9, "bold")
            ).grid(
                row=0,
                column=indice * 2,
                sticky="e",
                padx=(5, 2),
                pady=5
            )

            ttk.Label(
                frame_resumen,
                textvariable=variable
            ).grid(
                row=0,
                column=indice * 2 + 1,
                sticky="w",
                padx=(2, 20),
                pady=5
            )

        frame_tabla = ttk.LabelFrame(
            self.tab,
            text=" Resultado de la comparación ",
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
            "k_tct",
            "k_tri",
            "coincide",
            "abonar"
        )

        self.app.tabla_comparacion = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings"
        )

        encabezados = {
            "item": "Reactivo",
            "k_tct": "K TCT",
            "k_tri": "K TRI",
            "coincide": "Coincide",
            "abonar": "Abonar"
        }

        for columna in columnas:
            self.app.tabla_comparacion.heading(
                columna,
                text=encabezados[columna]
            )
            self.app.tabla_comparacion.column(
                columna,
                width=120,
                anchor="center"
            )

        self.app.tabla_comparacion.pack(
            fill="both",
            expand=True
        )

        self.app.tabla_comparacion.tag_configure(
            "abonar",
            background="#D9F2D9"
        )