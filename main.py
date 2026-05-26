import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox


class AnalizadorPsicometria:

    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Exámenes - Psicometría")
        self.root.geometry("800x520")

        self.archivos_excel = []

        self.respuestas_correctas = None
        self.respuestas_alumnos = None
        self.cuentas = None

        self.crear_interfaz()

    def crear_interfaz(self):
        titulo = tk.Label(
            self.root,
            text="Analizador de Exámenes - Psicometría",
            font=("Arial", 18, "bold")
        )
        titulo.pack(pady=15)

        btn_cargar = tk.Button(
            self.root,
            text="Seleccionar archivo(s) Excel",
            font=("Arial", 12),
            command=self.seleccionar_archivos
        )
        btn_cargar.pack(pady=8)

        btn_procesar = tk.Button(
            self.root,
            text="Leer, separar y unir datos",
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

        self.texto_resultado = tk.Text(self.root, width=95, height=20)
        self.texto_resultado.pack(pady=15)

    def seleccionar_archivos(self):
        self.archivos_excel = filedialog.askopenfilenames(
            title="Seleccionar archivo(s) Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )

        if self.archivos_excel:
            archivos = "\n".join([
                os.path.basename(archivo)
                for archivo in self.archivos_excel
            ])

            messagebox.showinfo(
                "Archivos seleccionados",
                f"Se seleccionaron {len(self.archivos_excel)} archivo(s):\n\n{archivos}"
            )

    def limpiar_texto(self, serie_o_df):
        return (
            serie_o_df
            .fillna("0")
            .astype(str)
            .apply(lambda col: col.str.strip().str.upper().replace("", "0"))
            if isinstance(serie_o_df, pd.DataFrame)
            else serie_o_df.fillna("0").astype(str).str.strip().str.upper().replace("", "0")
        )

    def leer_archivo_individual(self, archivo):
        hoja = "calificaciones_opcion"

        fila_items = 7
        fila_respuestas_correctas = 8
        fila_inicio_alumnos = 9

        col_cuenta = 2
        col_inicio_preguntas = 12

        df = pd.read_excel(
            archivo,
            sheet_name=hoja,
            header=None,
            engine="openpyxl"
        )

        columnas_preguntas = []

        for col in range(col_inicio_preguntas, df.shape[1]):
            valor_item = df.iloc[fila_items, col]

            if pd.notna(valor_item) and str(valor_item).strip().isdigit():
                columnas_preguntas.append(col)
            else:
                break

        if len(columnas_preguntas) == 0:
            raise ValueError(
                f"No se detectaron preguntas en el archivo: {os.path.basename(archivo)}"
            )

        respuestas_correctas = df.iloc[
            fila_respuestas_correctas,
            columnas_preguntas
        ]

        datos_alumnos = df.iloc[fila_inicio_alumnos:].copy()
        datos_alumnos = datos_alumnos.dropna(how="all")

        cuentas = datos_alumnos.iloc[:, col_cuenta]

        respuestas_alumnos = datos_alumnos.iloc[
            :,
            columnas_preguntas
        ]

        cuentas = cuentas.fillna("0").astype(str).str.strip()

        respuestas_correctas = self.limpiar_texto(
            respuestas_correctas
        ).reset_index(drop=True)

        respuestas_alumnos = self.limpiar_texto(
            respuestas_alumnos
        ).reset_index(drop=True)

        respuestas_alumnos.insert(
            0,
            "CUENTA",
            cuentas.reset_index(drop=True)
        )

        return respuestas_correctas, respuestas_alumnos

    def leer_y_separar_datos(self):
        if not self.archivos_excel:
            messagebox.showwarning(
                "Aviso",
                "Primero selecciona uno o más archivos Excel."
            )
            return

        try:
            lista_correctas = []
            lista_alumnos = []
            resumen_archivos = []

            for archivo in self.archivos_excel:
                correctas, alumnos = self.leer_archivo_individual(archivo)

                lista_correctas.append(correctas)
                lista_alumnos.append(alumnos)

                resumen_archivos.append(
                    f"{os.path.basename(archivo)}: {len(correctas)} preguntas"
                )

            self.respuestas_correctas = pd.concat(
                lista_correctas,
                ignore_index=True
            )

            data_final = lista_alumnos[0]

            for siguiente in lista_alumnos[1:]:
                data_final = pd.merge(
                    data_final,
                    siguiente,
                    on="CUENTA",
                    how="outer"
                )

            data_final = data_final.fillna("0")

            self.cuentas = data_final["CUENTA"]

            self.respuestas_alumnos = data_final.drop(
                columns=["CUENTA"]
            )

            self.respuestas_alumnos.columns = [
                f"Item{str(i + 1).zfill(2)}"
                for i in range(len(self.respuestas_alumnos.columns))
            ]

            total_alumnos = len(self.cuentas)
            total_preguntas = len(self.respuestas_correctas)

            self.mostrar_resumen(
                total_alumnos,
                total_preguntas,
                resumen_archivos
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Ocurrió un error al unir los archivos:\n\n{e}"
            )

    def mostrar_resumen(self, total_alumnos, total_preguntas, resumen_archivos):
        self.texto_resultado.delete("1.0", tk.END)

        self.texto_resultado.insert(
            tk.END,
            "LECTURA REALIZADA CORRECTAMENTE\n"
        )
        self.texto_resultado.insert(tk.END, "-" * 65 + "\n\n")

        self.texto_resultado.insert(tk.END, "Archivos procesados:\n")
        for resumen in resumen_archivos:
            self.texto_resultado.insert(tk.END, f"- {resumen}\n")

        self.texto_resultado.insert(tk.END, "\n")
        self.texto_resultado.insert(tk.END, f"Total alumnos: {total_alumnos}\n")
        self.texto_resultado.insert(tk.END, f"Total preguntas unidas: {total_preguntas}\n\n")

        self.texto_resultado.insert(tk.END, "Primeras cuentas:\n")
        self.texto_resultado.insert(tk.END, str(self.cuentas.head()) + "\n\n")

        self.texto_resultado.insert(tk.END, "Primeras respuestas correctas:\n")
        self.texto_resultado.insert(tk.END, str(self.respuestas_correctas.head(10)))

    def generar_archivos_control_y_dat(self):
        if self.respuestas_correctas is None or self.respuestas_alumnos is None:
            messagebox.showwarning(
                "Aviso",
                "Primero debes leer y separar los datos."
            )
            return

        try:
            nombre_base = os.path.splitext(
                os.path.basename(self.archivos_excel[0])
            )[0]

            carpeta_salida = os.path.dirname(self.archivos_excel[0])

            respuestas_posibles = set()

            for respuesta in self.respuestas_correctas:
                if pd.notna(respuesta) and respuesta != "0":
                    respuestas_posibles.add(str(respuesta).strip().upper())

            total_respuestas = len(respuestas_posibles)

            control = pd.DataFrame({
                "ITEM": [
                    f"Item{str(i + 1).zfill(2)}"
                    for i in range(len(self.respuestas_correctas))
                ],
                "RESPUESTA_CORRECTA": self.respuestas_correctas.values,
                "TOTAL_RESPUESTAS": [total_respuestas] * len(self.respuestas_correctas)
            })

            dat = self.respuestas_alumnos.copy()
            dat.insert(0, "CUENTA", self.cuentas.reset_index(drop=True))

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

            messagebox.showinfo(
                "Éxito",
                f"Archivos generados correctamente:\n\n"
                f"{archivo_control_xlsx}\n"
                f"{archivo_control_txt}\n\n"
                f"{archivo_dat_xlsx}\n"
                f"{archivo_dat_txt}"
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudieron generar los archivos:\n\n{e}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = AnalizadorPsicometria(root)
    root.mainloop()