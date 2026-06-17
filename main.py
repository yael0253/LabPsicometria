import os
import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader
from PIL import Image, ImageTk  # Librería para manejar imágenes PNG/JPG


class AnalizadorPsicometria:

    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de Exámenes - Psicometría")
        self.root.geometry("900x700")
        
        # Configurar un estilo moderno para las pestañas y componentes
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Un tema más limpio que el nativo clásico

        self.archivos_excel = []
        self.archivo_pdf = None

        self.respuestas_correctas = None
        self.respuestas_alumnos = None
        self.cuentas = None

        self.opciones_pdf = []
        self.temas_pdf = []
        self.alumnos_eliminados = 0

        self.crear_interfaz()

    def crear_interfaz(self):
        # ==========================================
        # 1. BANNER SUPERIOR (LOGO DE LA FACULTAD)
        # ==========================================
        self.frame_banner = tk.Frame(self.root, bg="#002B49", height=100) 
        self.frame_banner.pack(fill="x", side="top")
        self.frame_banner.pack_propagate(False)

        try:
            # Cargar y redimensionar el logo de la facultad
            img_logo = Image.open("logo_facultad.png") #PENDIENTE DE PONER EL LOGO REAL DE LA FACULTAD
            img_logo = img_logo.resize((300, 80), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(img_logo)
            
            lbl_logo = tk.Label(self.frame_banner, image=self.logo_photo, bg="#002B49")
            lbl_logo.pack(pady=10, padx=20, side="left")
        except Exception:
            # Si no encuentra la imagen, pone un texto elegante por seguridad
            lbl_texto_backup = tk.Label(
                self.frame_banner, 
                text="LABORATORIO DE PSICOMETRÍA", 
                font=("Arial", 15, "bold"), 
                fg="white", 
                bg="#002B49"
            )
            lbl_texto_backup.pack(pady=35, padx=20, side="left")

        lbl_titulo_app = tk.Label(
            self.frame_banner, 
            text="Sistema de Análisis Psicométrico", 
            font=("Arial", 12, "italic"), 
            fg="white", 
            bg="#002B49"
        )
        lbl_titulo_app.pack(pady=35, padx=20, side="right")

        # ==========================================
        # 2. CONTENEDOR DE PESTAÑAS (NOTEBOOK)
        # ==========================================
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Crear los contenedores individuales de cada pestaña
        self.tab_etl = ttk.Frame(self.notebook)
        self.tab_tct = ttk.Frame(self.notebook)
        self.tab_tri = ttk.Frame(self.notebook)

        # Añadir pestañas al panel principal
        self.notebook.add(self.tab_etl, text=" Preparación de Datos (ETL) ")
        self.notebook.add(self.tab_tct, text=" Teoría Clásica (TCT) ")
        self.notebook.add(self.tab_tri, text=" Respuestas al Ítem (TRI) ")

        # Cargar iconos globales para los botones de la pestaña ETL
        self.cargar_iconos_botones()

        # Configurar el contenido de cada pestaña
        self.configurar_pestaña_etl()
        self.configurar_pestaña_mantenimiento(self.tab_tct, "Módulo TCT (Reemplazo de Iteman)")
        self.configurar_pestaña_mantenimiento(self.tab_tri, "Módulo TRI (Reemplazo de XCalibre)")

    def cargar_iconos_botones(self):  #PENDIENTE DE PONER LOS ICONOS REALES DE EXCEL Y PDF EN LA CARPETA DEL PROYECTO
        """Intenta cargar los iconos pequeños para los botones de acción."""
        try:
            img_excel = Image.open("icono_excel.png").resize((24, 24), Image.Resampling.LANCZOS)
            self.ico_excel = ImageTk.PhotoImage(img_excel)

            img_pdf = Image.open("icono_pdf.png").resize((24, 24), Image.Resampling.LANCZOS)
            self.ico_pdf = ImageTk.PhotoImage(img_pdf)
        except Exception:
            # Fallback en caso de que no existan las imágenes de los iconos
            self.ico_excel = None
            self.ico_pdf = None

    def configurar_pestaña_etl(self):
        """Estructura visual intuitiva para la carga de datos limpiadora."""
        # Frame superior para los botones de carga externa
        frame_acciones = ttk.LabelFrame(self.tab_etl, text=" Acciones de Carga e Integración ", padding=15)
        frame_acciones.pack(fill="x", padx=15, pady=10)

        # Botón Excel con Icono
        btn_excel = ttk.Button(
            frame_acciones, 
            text=" Seleccionar archivo(s) Excel", 
            image=self.ico_excel, 
            compound="left", 
            command=self.seleccionar_archivos
        )
        btn_excel.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Botón PDF con Icono
        btn_pdf = ttk.Button(
            frame_acciones, 
            text=" Seleccionar PDF de análisis", 
            image=self.ico_pdf, 
            compound="left", 
            command=self.seleccionar_pdf
        )
        btn_pdf.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Botones de ejecución principal
        btn_unir = ttk.Button(frame_acciones, text="⚙️ Leer, separar y unir datos", command=self.leer_y_separar_datos)
        btn_unir.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        btn_generar = ttk.Button(frame_acciones, text="💾 Generar CONTROL y DAT", command=self.generar_archivos_control_y_dat)
        btn_generar.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        # Hacer las columnas del grid responsivas
        frame_acciones.columnconfigure((0, 1, 2, 3), weight=1)

        # Panel inferior para la Consola de salida de texto
        frame_consola = ttk.LabelFrame(self.tab_etl, text=" Consola de Resultados y Diagnóstico ", padding=10)
        frame_consola.pack(fill="both", expand=True, padx=15, pady=10)

        # Añadir barra de desplazamiento a la consola de texto
        scrollbar = ttk.Scrollbar(frame_consola)
        scrollbar.pack(side="right", fill="y")

        self.texto_resultado = tk.Text(frame_consola, font=("Consolas", 10), yscrollcommand=scrollbar.set)
        self.texto_resultado.pack(fill="both", expand=True)
        scrollbar.config(command=self.texto_resultado.yview)

    def configurar_pestaña_mantenimiento(self, tab, titulo_modulo):
        """Crea una vista limpia con una imagen central que indica 'En Desarrollo'."""
        # Contenedor centralizado
        frame_central = ttk.Frame(tab)
        frame_central.place(relx=0.5, rely=0.5, anchor="center")

        lbl_titulo = tk.Label(frame_central, text=titulo_modulo, font=("Arial", 16, "bold"), fg="#333333")
        lbl_titulo.pack(pady=10)

        try:
            # Intentar cargar la imagen de mantenimiento corporativa
            img_maint = Image.open("mantenimiento.png")
            img_maint = img_maint.resize((250, 250), Image.Resampling.LANCZOS)
            
            # Guardamos la referencia dinámicamente en el objeto del tab para evitar el Garbage Collector
            tab.img_maint_photo = ImageTk.PhotoImage(img_maint)
            
            lbl_img = tk.Label(frame_central, image=tab.img_maint_photo)
            lbl_img.pack(pady=10)
        except Exception:
            # Backup visual si no se encuentra el archivo 'mantenimiento.png'
            lbl_Aviso = tk.Label(
                frame_central, 
                text="⚠️", 
                font=("Arial", 48)
            )
            lbl_Aviso.pack(pady=5)

        lbl_msg = tk.Label(
            frame_central, 
            text="Módulo actualmente en fase de ingeniería.\nEstamos trabajando en la integración de algoritmos propios.", 
            font=("Arial", 11, "italic"),
            fg="#666666",
            justify="center"
        )
        lbl_msg.pack(pady=10)

    # ==========================================
    # LOGICA LOGÍSTICA DE ARCHIVOS (SE CONSERVA IGUAL)
    # ==========================================
    def seleccionar_archivos(self):
        self.archivos_excel = filedialog.askopenfilenames(
            title="Seleccionar archivo(s) Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if self.archivos_excel:
            archivos = "\n".join([os.path.basename(archivo) for archivo in self.archivos_excel])
            messagebox.showinfo("Archivos seleccionados", f"Se seleccionaron {len(self.archivos_excel)} archivo(s):\n\n{archivos}")

    def seleccionar_pdf(self):
        self.archivo_pdf = filedialog.askopenfilename(
            title="Seleccionar PDF de análisis",
            filetypes=[("PDF", "*.pdf")]
        )
        if self.archivo_pdf:
            messagebox.showinfo("PDF seleccionado", os.path.basename(self.archivo_pdf))

    def limpiar_texto(self, serie_o_df):
        if isinstance(serie_o_df, pd.DataFrame):
            return serie_o_df.fillna("0").astype(str).apply(lambda col: col.str.strip().str.upper().replace("", "0"))
        return serie_o_df.fillna("0").astype(str).str.strip().str.upper().replace("", "0")

    def leer_archivo_individual(self, archivo):
        hoja = "calificaciones_opcion"
        fila_items, fila_respuestas_correctas, fila_inicio_alumnos = 7, 8, 9
        col_cuenta, col_inicio_preguntas = 2, 12

        df = pd.read_excel(archivo, sheet_name=hoja, header=None, engine="openpyxl")
        columnas_preguntas = []

        for col in range(col_inicio_preguntas, df.shape[1]):
            valor_item = df.iloc[fila_items, col]
            if pd.notna(valor_item) and str(valor_item).strip().isdigit():
                columnas_preguntas.append(col)
            else:
                break

        if len(columnas_preguntas) == 0:
            raise ValueError(f"No se detectaron preguntas en el archivo: {os.path.basename(archivo)}")

        respuestas_correctas = df.iloc[fila_respuestas_correctas, columnas_preguntas]
        datos_alumnos = df.iloc[fila_inicio_alumnos:].copy().dropna(how="all")

        cuentas = datos_alumnos.iloc[:, col_cuenta].fillna("").astype(str).str.strip().reset_index(drop=True)
        respuestas_correctas = self.limpiar_texto(respuestas_correctas).reset_index(drop=True)
        respuestas_alumnos = self.limpiar_texto(datos_alumnos.iloc[:, columnas_preguntas]).reset_index(drop=True)

        respuestas_temp = respuestas_alumnos.replace(["", "NAN", "nan", "NaN"], "0")
        filas_validas_mask = respuestas_temp.ne("0").any(axis=1)
        
        self.alumnos_eliminados += int((~filas_validas_mask).sum())
        filas_validas = filas_validas_mask.tolist()

        cuentas = cuentas[filas_validas].reset_index(drop=True)
        respuestas_alumnos = respuestas_alumnos[filas_validas].reset_index(drop=True)
        respuestas_alumnos.insert(0, "CUENTA", cuentas)

        return respuestas_correctas, respuestas_alumnos

    def leer_pdf_opciones(self):
        if not self.archivo_pdf: return []
        reader = PdfReader(self.archivo_pdf)
        opciones_por_item = []
        for num_pagina, pagina in enumerate(reader.pages, start=1):
            try:
                texto = pagina.extract_text()
                if not texto: continue
                opciones = re.findall(r'([A-E])\s*\[\s*\d+\s*\]', texto, re.MULTILINE)
                if len(opciones) >= 2:
                    opciones_unicas = []
                    for opcion in opciones:
                        if opcion not in opciones_unicas: opciones_unicas.append(opcion)
                    opciones_por_item.append(len(opciones_unicas))
            except Exception as e:
                print(f"Error en página {num_pagina}: {e}")
        return opciones_por_item
        
    def leer_pdf_temas(self, total_preguntas_esperadas=None):
        if not self.archivo_pdf: return []
        reader = PdfReader(self.archivo_pdf)
        temas_detectados = []

        for num_pagina, pagina in enumerate(reader.pages, start=1):
            try:
                texto = pagina.extract_text()
                if not texto or not any(x in texto for x in ["Tema", "Reactivos", "Promedio"]): continue
                texto = " ".join(texto.replace("\n", " ").split())
                if "rpbis Promedio" in texto: texto = texto.split("rpbis Promedio", 1)[1]
                if "Facultad de Medicina" in texto: texto = texto.split("Facultad de Medicina", 1)[0]

                resultados = re.findall(r"([A-ZÁÉÍÓÚÑÜ ,]+?)(\d{1,2})(0?\.\d+|\.\d+)(0?\.\d+|\.\d+)", texto)
                for tema, cantidad_texto, p_promedio, rpbis in resultados:
                    tema = re.sub(r"[^A-ZÁÉÍÓÚÑÜ ,]", "", tema.strip().upper()).strip()
                    palabras_invalidas = ["RESUMEN", "REACTIVOS", "PROMEDIO", "ASISTENTES", "CALIFICACIÓN", "FIABILIDAD", "DIFICULTAD", "DISCRIMINACIÓN", "TEMA"]
                    if any(palabra in tema for palabra in palabras_invalidas) or len(tema) < 3: continue
                    
                    posibles_cantidades = [int(cantidad_texto)]
                    if len(cantidad_texto) == 2 and cantidad_texto.endswith("0"): posibles_cantidades.append(int(cantidad_texto[0]))
                    temas_detectados.append({"tema": tema, "cantidades": list(set(posibles_cantidades)), "capturado": cantidad_texto, "pagina": num_pagina})
            except Exception as e:
                print("Error leyendo temas:", e)

        temas_expandido = []
        for item in temas_detectados:
            tema, cantidades = item["tema"], item["cantidades"]
            cantidad = 20 if "IMÁGENES" in tema else min(cantidades)
            for _ in range(cantidad): temas_expandido.append(tema)

        if total_preguntas_esperadas is not None and len(temas_expandido) > total_preguntas_esperadas:
            temas_expandido = temas_expandido[:total_preguntas_esperadas]
        return temas_expandido
       
    def leer_y_separar_datos(self):
        if not self.archivos_excel:
            messagebox.showwarning("Aviso", "Primero selecciona uno o más archivos Excel.")
            return
        try:
            self.alumnos_eliminados = 0
            lista_correctas, lista_alumnos, resumen_archivos = [], [], []

            for archivo in self.archivos_excel:
                correctas, alumnos = self.leer_archivo_individual(archivo)
                lista_correctas.append(correctas)
                lista_alumnos.append(alumnos)
                resumen_archivos.append(f"{os.path.basename(archivo)}: {len(correctas)} preguntas")

            self.respuestas_correctas = pd.concat(lista_correctas, ignore_index=True)
            data_final = lista_alumnos[0]
            for siguiente in lista_alumnos[1:]:
                data_final = pd.merge(data_final, siguiente, on="CUENTA", how="outer")

            data_final = data_final.fillna("0")
            self.cuentas = data_final["CUENTA"]
            self.respuestas_alumnos = data_final.drop(columns=["CUENTA"])
            self.respuestas_alumnos.columns = [f"Item{str(i + 1).zfill(2)}" for i in range(len(self.respuestas_alumnos.columns))]

            if self.archivo_pdf:
                self.opciones_pdf = self.leer_pdf_opciones()
                self.temas_pdf = self.leer_pdf_temas(total_preguntas_esperadas=len(self.respuestas_correctas))
            else:
                self.opciones_pdf, self.temas_pdf = [], []

            self.mostrar_resumen(len(self.cuentas), len(self.respuestas_correctas), resumen_archivos)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al unir los archivos:\n\n{e}")

    def mostrar_resumen(self, total_alumnos, total_preguntas, resumen_archivos):
        self.texto_resultado.delete("1.0", tk.END)
        self.texto_resultado.insert(tk.END, "LECTURA REALIZADA CORRECTAMENTE\n" + "-" * 70 + "\n\n")
        self.texto_resultado.insert(tk.END, "Archivos Excel procesados:\n")
        for r in resumen_archivos: self.texto_resultado.insert(tk.END, f"- {r}\n")
        self.texto_resultado.insert(tk.END, f"\nTotal alumnos válidos: {total_alumnos}\nAlumnos vacíos eliminados: {self.alumnos_eliminados}\nTotal preguntas unidas: {total_preguntas}\nTemas detectados PDF: {len(self.temas_pdf)}\n")
        if self.archivo_pdf:
            self.texto_resultado.insert(tk.END, f"PDF cargado: {os.path.basename(self.archivo_pdf)}\nReactivos detectados en PDF: {len(self.opciones_pdf)}\n\n")
        else:
            self.texto_resultado.insert(tk.END, "PDF no seleccionado. El CONTROL usará el cálculo anterior.\n\n")
        self.texto_resultado.insert(tk.END, f"Primeras cuentas:\n{str(self.cuentas.head())}\n\nPrimeras respuestas correctas:\n{str(self.respuestas_correctas.head(10))}\n")

    def generar_archivos_control_y_dat(self):
        if self.respuestas_correctas is None or self.respuestas_alumnos is None:
            messagebox.showwarning("Aviso", "Primero debes leer y separar los datos.")
            return
        try:
            nombre_base = os.path.splitext(os.path.basename(self.archivos_excel[0]))[0]
            carpeta_salida = os.path.dirname(self.archivos_excel[0])
            total_preguntas = len(self.respuestas_correctas)

            if self.opciones_pdf and len(self.opciones_pdf) >= total_preguntas:
                total_respuestas_lista = self.opciones_pdf[:total_preguntas]
            else:
                respuestas_posibles = set(str(r).strip().upper() for r in self.respuestas_correctas if pd.notna(r) and r != "0")
                total_respuestas_lista = [len(respuestas_posibles)] * total_preguntas
            
            temas_control = list(self.temas_pdf)
            if len(temas_control) < total_preguntas:
                temas_control.extend(["PRELIMINAR"] * (total_preguntas - len(temas_control)))
            else:
                temas_control = temas_control[:total_preguntas]

            control = pd.DataFrame({
                "ITEM": [f"Item{str(i + 1).zfill(2)}" for i in range(total_preguntas)],
                "RESPUESTA_CORRECTA": self.respuestas_correctas.values,
                "TOTAL_RESPUESTAS": total_respuestas_lista,
                "TEMA": temas_control,
                "Y": ["Y"] * total_preguntas, "M": ["M"] * total_preguntas
            })

            dat = self.respuestas_alumnos.copy()
            dat.insert(0, "CUENTA", self.cuentas.reset_index(drop=True))

            control.to_excel(os.path.join(carpeta_salida, f"{nombre_base}_control.xlsx"), index=False, engine="openpyxl")
            dat.to_excel(os.path.join(carpeta_salida, f"{nombre_base}_DAT.xlsx"), index=False, engine="openpyxl")
            control.to_csv(os.path.join(carpeta_salida, f"{nombre_base}_control.txt"), sep="\t", index=False, header=False, encoding="utf-8")
            dat.to_csv(os.path.join(carpeta_salida, f"{nombre_base}_DAT.txt"), sep="\t", index=False, header=False, encoding="utf-8")

            messagebox.showinfo("Éxito", f"Archivos generados correctamente en:\n{carpeta_salida}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron generar los archivos:\n\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AnalizadorPsicometria(root)
    root.mainloop()