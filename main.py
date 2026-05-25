import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox


class AnalizadorPsicometria:

    def __init__(self, root):

        self.root = root
        self.root.title("Analizador de Exámenes - Psicometría")
        self.root.geometry("750x500")

        self.archivo_excel = None

        self.df = None
        self.respuestas_correctas = None
        self.datos_alumnos = None
        self.respuestas_alumnos = None
        self.cuentas = None

        self.crear_interfaz()

    # =========================================================
    # INTERFAZ
    # =========================================================

    def crear_interfaz(self):

        titulo = tk.Label(
            self.root,
            text="Analizador de Exámenes - Psicometría",
            font=("Arial", 18, "bold")
        )

        titulo.pack(pady=15)

        btn_cargar = tk.Button(
            self.root,
            text="Seleccionar archivo Excel",
            font=("Arial", 12),
            command=self.seleccionar_archivo
        )

        btn_cargar.pack(pady=8)

        btn_procesar = tk.Button(
            self.root,
            text="Leer y separar datos",
            font=("Arial", 12),
            command=self.leer_y_separar_datos
        )

        btn_procesar.pack(pady=8)

        btn_generar = tk.Button(
            self.root,
            text="Generar CONTROL y DAT",
            font=("Arial", 12),
            command=self.generar_archivos_control_y_dat
        )

        btn_generar.pack(pady=8)

        self.texto_resultado = tk.Text(
            self.root,
            width=90,
            height=20
        )

        self.texto_resultado.pack(pady=15)

    # =========================================================
    # SELECCIONAR ARCHIVO
    # =========================================================

    def seleccionar_archivo(self):

        self.archivo_excel = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )

        if self.archivo_excel:

            messagebox.showinfo(
                "Archivo seleccionado",
                self.archivo_excel
            )

    # =========================================================
    # LEER Y SEPARAR DATOS
    # =========================================================

    def leer_y_separar_datos(self):

        if not self.archivo_excel:

            messagebox.showwarning(
                "Aviso",
                "Primero selecciona un archivo Excel."
            )

            return

        try:

            hoja = "calificaciones_opcion"

            # =================================================
            # CONFIGURACIÓN DEL EXCEL
            # =================================================

            fila_items = 7                  # fila 8 Excel
            fila_respuestas_correctas = 8  # fila 9 Excel
            fila_inicio_alumnos = 9        # fila 10 Excel

            col_cuenta = 2                 # columna C
            col_inicio_preguntas = 12      # columna M

            # =================================================
            # LEER EXCEL
            # =================================================

            self.df = pd.read_excel(
                self.archivo_excel,
                sheet_name=hoja,
                header=None,
                engine="openpyxl"
            )

            # =================================================
            # DETECTAR COLUMNAS DE PREGUNTAS
            # =================================================

            columnas_preguntas = []

            for col in range(col_inicio_preguntas, self.df.shape[1]):

                valor_item = self.df.iloc[fila_items, col]

                if (
                    pd.notna(valor_item)
                    and str(valor_item).strip().isdigit()
                ):

                    columnas_preguntas.append(col)

                else:
                    break

            total_preguntas = len(columnas_preguntas)

            if total_preguntas == 0:

                messagebox.showerror(
                    "Error",
                    "No se detectaron preguntas."
                )

                return

            # =================================================
            # RESPUESTAS CORRECTAS
            # =================================================

            self.respuestas_correctas = self.df.iloc[
                fila_respuestas_correctas,
                columnas_preguntas
            ]

            # =================================================
            # DATOS DE ALUMNOS
            # =================================================

            self.datos_alumnos = self.df.iloc[
                fila_inicio_alumnos:
            ].copy()

            self.datos_alumnos = self.datos_alumnos.dropna(how="all")

            # =================================================
            # CUENTAS
            # =================================================

            self.cuentas = self.datos_alumnos.iloc[:, col_cuenta]

            self.cuentas = (
                self.cuentas
                .fillna("0")
                .astype(str)
                .str.strip()
            )

            # =================================================
            # RESPUESTAS ALUMNOS
            # =================================================

            self.respuestas_alumnos = self.datos_alumnos.iloc[
                :,
                columnas_preguntas
            ]

            # =================================================
            # LIMPIEZA RESPUESTAS CORRECTAS
            # =================================================

            self.respuestas_correctas = (
                self.respuestas_correctas
                .fillna("0")
                .astype(str)
                .str.strip()
                .str.upper()
                .replace("", "0")
            )

            # =================================================
            # LIMPIEZA RESPUESTAS ALUMNOS
            # =================================================

            self.respuestas_alumnos = (
                self.respuestas_alumnos
                .fillna("0")
                .astype(str)
                .apply(
                    lambda col:
                    col.str.strip()
                    .str.upper()
                    .replace("", "0")
                )
            )

            total_alumnos = len(self.datos_alumnos)

            self.mostrar_resumen(
                total_alumnos,
                total_preguntas
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Ocurrió un error:\n\n{e}"
            )

    # =========================================================
    # MOSTRAR RESUMEN
    # =========================================================

    def mostrar_resumen(
        self,
        total_alumnos,
        total_preguntas
    ):

        self.texto_resultado.delete("1.0", tk.END)

        self.texto_resultado.insert(
            tk.END,
            "LECTURA REALIZADA CORRECTAMENTE\n"
        )

        self.texto_resultado.insert(
            tk.END,
            "-" * 60 + "\n\n"
        )

        self.texto_resultado.insert(
            tk.END,
            f"Archivo:\n{self.archivo_excel}\n\n"
        )

        self.texto_resultado.insert(
            tk.END,
            f"Total alumnos: {total_alumnos}\n"
        )

        self.texto_resultado.insert(
            tk.END,
            f"Total preguntas: {total_preguntas}\n\n"
        )

        self.texto_resultado.insert(
            tk.END,
            "Primeras cuentas:\n"
        )

        self.texto_resultado.insert(
            tk.END,
            str(self.cuentas.head())
        )

        self.texto_resultado.insert(
            tk.END,
            "\n\n"
        )

        self.texto_resultado.insert(
            tk.END,
            "Primeras respuestas correctas:\n"
        )

        self.texto_resultado.insert(
            tk.END,
            str(self.respuestas_correctas.head(10))
        )

    # =========================================================
    # GENERAR ARCHIVOS
    # =========================================================

    def generar_archivos_control_y_dat(self):

        if (
            self.respuestas_correctas is None
            or self.respuestas_alumnos is None
        ):

            messagebox.showwarning(
                "Aviso",
                "Primero debes leer los datos."
            )

            return

        try:

            # =================================================
            # NOMBRE BASE
            # =================================================

            nombre_base = os.path.splitext(
                os.path.basename(self.archivo_excel)
            )[0]

            carpeta_salida = os.path.dirname(
                self.archivo_excel
            )

            # =================================================
            # TOTAL RESPUESTAS POSIBLES
            # =================================================

            respuestas_posibles = set()

            for respuesta in self.respuestas_correctas:

                if (
                    pd.notna(respuesta)
                    and respuesta != "0"
                ):

                    respuestas_posibles.add(
                        str(respuesta).strip().upper()
                    )

            total_respuestas = len(respuestas_posibles)

            # =================================================
            # ARCHIVO CONTROL
            # =================================================

            control = pd.DataFrame({

                "ITEM": [

                    f"Item{str(i + 1).zfill(2)}"

                    for i in range(
                        len(self.respuestas_correctas)
                    )
                ],

                "RESPUESTA_CORRECTA":
                    self.respuestas_correctas.values,

                "TOTAL_RESPUESTAS":
                    [total_respuestas]
                    * len(self.respuestas_correctas)

            })

            # =================================================
            # ARCHIVO DAT
            # =================================================

            dat = self.respuestas_alumnos.copy()

            dat = dat.reset_index(drop=True)

            dat.columns = [

                f"Item{str(i + 1).zfill(2)}"

                for i in range(
                    len(dat.columns)
                )
            ]

            cuentas = self.cuentas.reset_index(drop=True)

            dat.insert(
                0,
                "CUENTA",
                cuentas
            )

            # =================================================
            # NOMBRES ARCHIVOS
            # =================================================

            archivo_control_xlsx = os.path.join(
                carpeta_salida,
                f"{nombre_base}_control.xlsx"
            )

            archivo_control_txt = os.path.join(
                carpeta_salida,
                f"{nombre_base}_control.txt"
            )

            archivo_dat_xlsx = os.path.join(
                carpeta_salida,
                f"{nombre_base}_DAT.xlsx"
            )

            archivo_dat_txt = os.path.join(
                carpeta_salida,
                f"{nombre_base}_DAT.txt"
            )

            # =================================================
            # GUARDAR XLSX
            # =================================================

            control.to_excel(
                archivo_control_xlsx,
                index=False,
                engine="openpyxl"
            )

            dat.to_excel(
                archivo_dat_xlsx,
                index=False,
                engine="openpyxl"
            )

            # =================================================
            # GUARDAR TXT
            # =================================================

            control.to_csv(
                archivo_control_txt,
                sep="\t",
                index=False,
                header=False,
                encoding="utf-8"
            )

            dat.to_csv(
                archivo_dat_txt,
                sep="\t",
                index=False,
                header=False,
                encoding="utf-8"
            )

            # =================================================
            # MENSAJE
            # =================================================

            messagebox.showinfo(
                "Éxito",
                "Archivos generados correctamente."
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudieron generar:\n\n{e}"
            )


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = AnalizadorPsicometria(root)

    root.mainloop()