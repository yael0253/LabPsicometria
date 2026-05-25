import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

class AnalizadorPsicometria:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Exámenes - Psicometría")
        self.root.geometry("700x450")

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
            text="Analizador de Exámenes",
            font=("Arial", 18, "bold")
        )
        titulo.pack(pady=15)

        btn_cargar = tk.Button(
            self.root,
            text="Seleccionar archivo Excel",
            font=("Arial", 12),
            command=self.seleccionar_archivo
        )
        btn_cargar.pack(pady=10)

        btn_procesar = tk.Button(
            self.root,
            text="Leer y separar datos",
            font=("Arial", 12),
            command=self.leer_y_separar_datos
        )
        btn_procesar.pack(pady=10)

        self.texto_resultado = tk.Text(self.root, width=80, height=18)
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
                header=None
            )

            # Respuestas correctas
            self.respuestas_correctas = self.df.iloc[
                fila_respuestas_correctas,
                col_inicio_preguntas:
            ]

            # Datos de alumnos
            self.datos_alumnos = self.df.iloc[fila_inicio_alumnos:].copy()

            # Número de cuenta
            self.cuentas = self.datos_alumnos.iloc[:, col_cuenta]

            # Respuestas de alumnos
            self.respuestas_alumnos = self.datos_alumnos.iloc[
                :,
                col_inicio_preguntas:
            ]

            # Limpiar columnas vacías
            self.respuestas_correctas = self.respuestas_correctas.dropna()
            total_preguntas = len(self.respuestas_correctas)

            self.respuestas_alumnos = self.respuestas_alumnos.iloc[:, :total_preguntas]

            total_alumnos = len(self.datos_alumnos)

            self.mostrar_resumen(total_alumnos, total_preguntas)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al leer el archivo:\n{e}")

    def mostrar_resumen(self, total_alumnos, total_preguntas):
        self.texto_resultado.delete("1.0", tk.END)

        self.texto_resultado.insert(tk.END, "LECTURA REALIZADA CORRECTAMENTE\n")
        self.texto_resultado.insert(tk.END, "-" * 50 + "\n\n")

        self.texto_resultado.insert(tk.END, f"Total de alumnos detectados: {total_alumnos}\n")
        self.texto_resultado.insert(tk.END, f"Total de preguntas detectadas: {total_preguntas}\n\n")

        self.texto_resultado.insert(tk.END, "Primeras cuentas detectadas:\n")
        self.texto_resultado.insert(tk.END, str(self.cuentas.head()) + "\n\n")

        self.texto_resultado.insert(tk.END, "Primeras respuestas correctas:\n")
        self.texto_resultado.insert(tk.END, str(self.respuestas_correctas.head(10)) + "\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = AnalizadorPsicometria(root)
    root.mainloop()