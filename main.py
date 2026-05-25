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

        self.texto_resultado = tk.Text(self.root, width=90, height=18)
        self.texto_resultado.pack(pady=15)

    def seleccionar_archivo(self):
        self.archivo_excel = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )

        if self.archivo_excel:
            messagebox.showinfo("Archivo seleccionado", self.archivo_excel)

    def leer_y_separar_datos(self):
        if not self.archivo_excel:
            messagebox.showwarning("Aviso", "Primero selecciona un archivo Excel.")
            return

        try:
            hoja = "calificaciones_opcion"

            # Configuración según el formato del Excel
            fila_respuestas_correctas = 8   # fila 9 en Excel
            fila_inicio_alumnos = 9         # fila 10 en Excel
            col_cuenta = 2                  # columna C
            col_inicio_preguntas = 12       # columna M

            self.df = pd.read_excel(
                self.archivo_excel,
                sheet_name=hoja,
                header=None,
                engine="openpyxl"
            )

            # Respuestas correctas
            self.respuestas_correctas = self.df.iloc[
                fila_respuestas_correctas,
                col_inicio_preguntas:
            ]

            # Quitar columnas vacías de respuestas correctas
            self.respuestas_correctas = self.respuestas_correctas.dropna()
            total_preguntas = len(self.respuestas_correctas)

            # Datos de alumnos
            self.datos_alumnos = self.df.iloc[fila_inicio_alumnos:].copy()

            # Eliminar filas completamente vacías
            self.datos_alumnos = self.datos_alumnos.dropna(how="all")

            # Número de cuenta
            self.cuentas = self.datos_alumnos.iloc[:, col_cuenta]

            # Respuestas de alumnos
            self.respuestas_alumnos = self.datos_alumnos.iloc[
                :,
                col_inicio_preguntas:col_inicio_preguntas + total_preguntas
            ]

            # Limpieza básica
            self.cuentas = self.cuentas.astype(str).str.strip()

            self.respuestas_correctas = (
                self.respuestas_correctas
                .astype(str)
                .str.strip()
                .str.upper()
            )

            self.respuestas_alumnos = (
                self.respuestas_alumnos
                .astype(str)
                .apply(lambda col: col.str.strip().str.upper())
            )

            total_alumnos = len(self.datos_alumnos)

            self.mostrar_resumen(total_alumnos, total_preguntas)

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Ocurrió un error al leer el archivo:\n\n{e}"
            )

    def mostrar_resumen(self, total_alumnos, total_preguntas):
        self.texto_resultado.delete("1.0", tk.END)

        self.texto_resultado.insert(tk.END, "LECTURA REALIZADA CORRECTAMENTE\n")
        self.texto_resultado.insert(tk.END, "-" * 60 + "\n\n")

        self.texto_resultado.insert(
            tk.END,
            f"Archivo cargado:\n{self.archivo_excel}\n\n"
        )

        self.texto_resultado.insert(
            tk.END,
            f"Total de alumnos detectados: {total_alumnos}\n"
        )

        self.texto_resultado.insert(
            tk.END,
            f"Total de preguntas detectadas: {total_preguntas}\n\n"
        )

        self.texto_resultado.insert(tk.END, "Primeras cuentas detectadas:\n")
        self.texto_resultado.insert(tk.END, str(self.cuentas.head()) + "\n\n")

        self.texto_resultado.insert(tk.END, "Primeras respuestas correctas:\n")
        self.texto_resultado.insert(
            tk.END,
            str(self.respuestas_correctas.head(10)) + "\n"
        )

    def generar_archivos_control_y_dat(self):
        if self.respuestas_correctas is None or self.respuestas_alumnos is None:
            messagebox.showwarning(
                "Aviso",
                "Primero debes leer y separar los datos."
            )
            return

        try:
            # Nombre base del archivo original
            nombre_base = os.path.splitext(
                os.path.basename(self.archivo_excel)
            )[0]

            # Carpeta donde se guardarán los archivos
            carpeta_salida = os.path.dirname(self.archivo_excel)

            # Respuestas correctas limpias
            respuestas_correctas = self.respuestas_correctas.reset_index(drop=True)

            # Detectar respuestas posibles usadas en todo el examen
            respuestas_posibles = set()

            for respuesta in respuestas_correctas:
                if pd.notna(respuesta) and respuesta != "NAN":
                    respuestas_posibles.add(str(respuesta).strip().upper())

            total_respuestas = len(respuestas_posibles)

            # =========================
            # ARCHIVO CONTROL
            # =========================

            control = pd.DataFrame({
                "ITEM": [
                    f"Item{str(i + 1).zfill(2)}"
                    for i in range(len(respuestas_correctas))
                ],
                "RESPUESTA_CORRECTA": respuestas_correctas.values,
                "TOTAL_RESPUESTAS": [total_respuestas] * len(respuestas_correctas)
            })

            # =========================
            # ARCHIVO DAT
            # =========================

            dat = self.respuestas_alumnos.copy()
            dat = dat.reset_index(drop=True)

            dat.columns = [
                f"Item{str(i + 1).zfill(2)}"
                for i in range(len(dat.columns))
            ]

            cuentas = self.cuentas.reset_index(drop=True)
            dat.insert(0, "CUENTA", cuentas)

            # =========================
            # NOMBRES DE SALIDA
            # =========================

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

            # =========================
            # GUARDAR XLSX
            # =========================

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

            # =========================
            # GUARDAR TXT
            # =========================

            control.to_csv(
                archivo_control_txt,
                sep="\t",
                index=False,
                encoding="utf-8"
            )

            dat.to_csv(
                archivo_dat_txt,
                sep="\t",
                index=False,
                encoding="utf-8"
            )

            messagebox.showinfo(
                "Archivos generados",
                f"Se generaron correctamente:\n\n"
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