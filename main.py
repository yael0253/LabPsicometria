import os
import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader


class AnalizadorPsicometria:

    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Exámenes - Psicometría")
        self.root.geometry("850x560")

        self.archivos_excel = []
        self.archivo_pdf = None

        self.respuestas_correctas = None
        self.respuestas_alumnos = None
        self.cuentas = None

        self.opciones_pdf = []
        self.alumnos_eliminados = 0

        self.crear_interfaz()

    def crear_interfaz(self):
        titulo = tk.Label(
            self.root,
            text="Analizador de Exámenes - Psicometría",
            font=("Arial", 18, "bold")
        )
        titulo.pack(pady=15)

        tk.Button(
            self.root,
            text="Seleccionar archivo(s) Excel",
            font=("Arial", 12),
            command=self.seleccionar_archivos
        ).pack(pady=6)

        tk.Button(
            self.root,
            text="Seleccionar PDF de análisis",
            font=("Arial", 12),
            command=self.seleccionar_pdf
        ).pack(pady=6)
        
        tk.Button(
            self.root,
            text="Leer, separar y unir datos",
            font=("Arial", 12),
            command=self.leer_y_separar_datos
        ).pack(pady=6)

        tk.Button(
            self.root,
            text="Generar CONTROL y DAT",
            font=("Arial", 12),
            command=self.generar_archivos_control_y_dat
        ).pack(pady=6)

        self.texto_resultado = tk.Text(self.root, width=100, height=20)
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

    def seleccionar_pdf(self):
        self.archivo_pdf = filedialog.askopenfilename(
            title="Seleccionar PDF de análisis",
            filetypes=[("PDF", "*.pdf")]
        )

        if self.archivo_pdf:
            messagebox.showinfo(
                "PDF seleccionado",
                os.path.basename(self.archivo_pdf)
            )

    def limpiar_texto(self, serie_o_df):
        if isinstance(serie_o_df, pd.DataFrame):
            return (
                serie_o_df
                .fillna("0")
                .astype(str)
                .apply(lambda col: col.str.strip().str.upper().replace("", "0"))
            )

        return (
            serie_o_df
            .fillna("0")
            .astype(str)
            .str.strip()
            .str.upper()
            .replace("", "0")
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

        cuentas = (
            cuentas
            .fillna("")
            .astype(str)
            .str.strip()
            .reset_index(drop=True)
        )

        respuestas_correctas = self.limpiar_texto(
            respuestas_correctas
        ).reset_index(drop=True)

        respuestas_alumnos = self.limpiar_texto(
            respuestas_alumnos
        ).reset_index(drop=True)

        respuestas_temp = respuestas_alumnos.replace(
            ["", "NAN", "nan", "NaN"],
            "0"
        )

        filas_validas = respuestas_temp.ne("0").any(axis=1)

        alumnos_eliminados = (~filas_validas).sum()
        self.alumnos_eliminados += int(alumnos_eliminados)

        filas_validas = filas_validas.tolist()

        cuentas = cuentas[filas_validas].reset_index(drop=True)
        respuestas_alumnos = respuestas_alumnos[filas_validas].reset_index(drop=True)

        respuestas_alumnos.insert(
            0,
            "CUENTA",
            cuentas
        )

        return respuestas_correctas, respuestas_alumnos

    def leer_pdf_opciones(self):
        if not self.archivo_pdf:
            return []

        reader = PdfReader(self.archivo_pdf)
        opciones_por_item = []

        for num_pagina, pagina in enumerate(reader.pages, start=1):
            try:
                texto = pagina.extract_text()

                if not texto:
                    continue

                # Buscar opciones tipo:
                # A [79]
                # B [30]
                # C [151]
                opciones = re.findall(
                    r'([A-E])\s*\[\s*\d+\s*\]',
                    texto,
                    re.MULTILINE
                )

                # Solo contar páginas que parezcan reactivos
                if len(opciones) >= 2:
                    opciones_unicas = []

                    for opcion in opciones:
                        if opcion not in opciones_unicas:
                            opciones_unicas.append(opcion)

                    opciones_por_item.append(len(opciones_unicas))

                    print(
                        f"Página {num_pagina}: opciones detectadas {opciones_unicas}"
                    )

            except Exception as e:
                    print(f"Error en página {num_pagina}: {e}")
        return opciones_por_item
    
    def leer_pdf_temas(self, total_preguntas_esperadas=None):

            if not self.archivo_pdf:
                return []

            reader = PdfReader(self.archivo_pdf)

            temas_detectados = []

            for num_pagina, pagina in enumerate(reader.pages, start=1):

                try:
                    texto = pagina.extract_text()

                    if not texto:
                        continue

                    if "Tema" not in texto and "Reactivos" not in texto and "Promedio" not in texto:
                        continue

                    texto = texto.replace("\n", " ")
                    texto = " ".join(texto.split())

                    if "rpbis Promedio" in texto:
                        texto = texto.split("rpbis Promedio", 1)[1]

                    if "Facultad de Medicina" in texto:
                        texto = texto.split("Facultad de Medicina", 1)[0]

                    resultados = re.findall(
                        r"([A-ZÁÉÍÓÚÑÜ ,]+?)(\d{1,2})(0?\.\d+|\.\d+)(0?\.\d+|\.\d+)",
                        texto
                    )

                    for tema, cantidad_texto, p_promedio, rpbis in resultados:

                        tema = tema.strip().upper()

                        tema = re.sub(
                            r"[^A-ZÁÉÍÓÚÑÜ ,]",
                            "",
                            tema
                        ).strip()

                        palabras_invalidas = [
                            "RESUMEN",
                            "REACTIVOS",
                            "PROMEDIO",
                            "ASISTENTES",
                            "CALIFICACIÓN",
                            "FIABILIDAD",
                            "DIFICULTAD",
                            "DISCRIMINACIÓN",
                            "TEMA"
                        ]

                        if any(palabra in tema for palabra in palabras_invalidas):
                            continue

                        if len(tema) < 3:
                            continue

                        posibles_cantidades = []

                        cantidad_normal = int(cantidad_texto)
                        posibles_cantidades.append(cantidad_normal)

                        # Caso ambiguo:
                        # 30.460 puede ser 3 + 0.460
                        # pero 200.579 puede ser 20 + 0.579
                        if len(cantidad_texto) == 2 and cantidad_texto.endswith("0"):
                            posibles_cantidades.append(int(cantidad_texto[0]))

                        posibles_cantidades = list(set(posibles_cantidades))

                        temas_detectados.append({
                            "tema": tema,
                            "cantidades": posibles_cantidades,
                            "capturado": cantidad_texto,
                            "pagina": num_pagina
                        })

                except Exception as e:
                    print("Error leyendo temas:", e)

            temas_expandido = []

            for item in temas_detectados:

                tema = item["tema"]
                cantidades = item["cantidades"]

                # Correcciones especiales conocidas
                if "IMÁGENES" in tema:
                    cantidad = 20

                else:
                    # Si hay ambigüedad como 30, usar 3
                    cantidad = min(cantidades)

                print(
                    f"Página {item['pagina']} | {tema} -> {cantidad} "
                    f"(capturado: {item['capturado']})"
                )

                for _ in range(cantidad):
                    temas_expandido.append(tema)

            if total_preguntas_esperadas is not None:
                if len(temas_expandido) > total_preguntas_esperadas:
                    temas_expandido = temas_expandido[:total_preguntas_esperadas]

            print("TOTAL TEMAS EXPANDIDOS:", len(temas_expandido))

            return temas_expandido
       
    def leer_y_separar_datos(self):
        if not self.archivos_excel:
            messagebox.showwarning(
                "Aviso",
                "Primero selecciona uno o más archivos Excel."
            )
            return

        try:
            self.alumnos_eliminados = 0

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

            if self.archivo_pdf:
                self.opciones_pdf = self.leer_pdf_opciones()
                self.temas_pdf = self.leer_pdf_temas(
                     total_preguntas_esperadas=len(self.respuestas_correctas)
                )
            else:
                self.opciones_pdf = []
                self.temas_pdf = []

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
        self.texto_resultado.insert(tk.END, "-" * 70 + "\n\n")

        self.texto_resultado.insert(tk.END, "Archivos Excel procesados:\n")
        for resumen in resumen_archivos:
            self.texto_resultado.insert(tk.END, f"- {resumen}\n")

        self.texto_resultado.insert(tk.END, "\n")
        self.texto_resultado.insert(tk.END, f"Total alumnos válidos: {total_alumnos}\n")
        self.texto_resultado.insert(tk.END, f"Alumnos eliminados sin respuestas: {self.alumnos_eliminados}\n")
        self.texto_resultado.insert(tk.END, f"Total preguntas unidas: {total_preguntas}\n\n")
        self.texto_resultado.insert(tk.END, f"Temas detectados PDF: {len(self.temas_pdf)}\n"
)

        if self.archivo_pdf:
            self.texto_resultado.insert(
                tk.END,
                f"PDF cargado: {os.path.basename(self.archivo_pdf)}\n"
            )
            self.texto_resultado.insert(
                tk.END,
                f"Reactivos detectados en PDF: {len(self.opciones_pdf)}\n\n"
            )
        else:
            self.texto_resultado.insert(
                tk.END,
                "PDF no seleccionado. El CONTROL usará el cálculo anterior.\n\n"
            )

        self.texto_resultado.insert(tk.END, "Primeras cuentas:\n")
        self.texto_resultado.insert(tk.END, str(self.cuentas.head()) + "\n\n")

        self.texto_resultado.insert(tk.END, "Primeras respuestas correctas:\n")
        self.texto_resultado.insert(tk.END, str(self.respuestas_correctas.head(10)) + "\n\n")

        if self.opciones_pdf:
            self.texto_resultado.insert(tk.END, "Primeros totales de opciones desde PDF:\n")
            self.texto_resultado.insert(tk.END, str(self.opciones_pdf[:10]))

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

            total_preguntas = len(self.respuestas_correctas)

            if self.opciones_pdf and len(self.opciones_pdf) >= total_preguntas:
                total_respuestas_lista = self.opciones_pdf[:total_preguntas]
            else:
                respuestas_posibles = set()

                for respuesta in self.respuestas_correctas:
                    if pd.notna(respuesta) and respuesta != "0":
                        respuestas_posibles.add(str(respuesta).strip().upper())

                total_respuestas = len(respuestas_posibles)
                total_respuestas_lista = [total_respuestas] * total_preguntas
            
            # ==========================================
            # PREPARAR TEMAS PARA CONTROL
            # ==========================================

            temas_control = list(self.temas_pdf)

            if len(temas_control) < total_preguntas:
                faltantes = total_preguntas - len(temas_control)
                temas_control.extend(["PRELIMINAR"] * faltantes)

            elif len(temas_control) > total_preguntas:
                temas_control = temas_control[:total_preguntas]

            control = pd.DataFrame({
                "ITEM": [
                    f"Item{str(i + 1).zfill(2)}"
                    for i in range(total_preguntas)
                ],
                "RESPUESTA_CORRECTA": self.respuestas_correctas.values,
                "TOTAL_RESPUESTAS": total_respuestas_lista,
                "TEMA": temas_control,
                "Y": ["Y"] * total_preguntas,
                "M": ["M"] * total_preguntas
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