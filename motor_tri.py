import numpy as np
import pandas as pd


class MotorTRI:
    """
    Motor para análisis mediante Teoría de Respuesta al Ítem.

    Modelo inicial:
    - Modelo logístico de tres parámetros (3PL).
    - Preparación de matriz binaria.
    - Cuadratura Gauss-Hermite.
    - Cálculo de probabilidades 3PL.

    Pendiente:
    - Algoritmo EM.
    - Estimación de a, b y c.
    - Estimación de theta.
    - Cálculo de ajuste y Flag F.
    - Detección definitiva de Flag K basada en theta.
    """

    def __init__(self):
        # ==========================================
        # CONFIGURACIÓN DEL MODELO 3PL
        # ==========================================
        self.constante_logistica = 1.7

        # Algoritmo EM
        self.max_iteraciones = 60
        self.tolerancia = 0.001
        self.puntos_cuadratura = 40

        # Rango de habilidad
        self.theta_min = -7.0
        self.theta_max = 7.0

        # Valores iniciales
        self.a_inicial = 1.0
        self.b_inicial = 0.0
        self.c_inicial = 0.25

        # Límites permitidos
        self.a_min = 0.05
        self.a_max = 6.0

        self.b_min = -4.0
        self.b_max = 4.0

        self.c_min = 0.0
        self.c_max = 0.70

        # Límites para flags
        self.flag_a_bajo = 0.30
        self.flag_a_alto = 4.00

        self.flag_b_bajo = -3.00
        self.flag_b_alto = 3.00

        self.flag_c_bajo = 0.00
        self.flag_c_alto = 0.40

        # Resultados
        self.resultados = None
        self.detalle_opciones = None
        self.resumen = None
        self.thetas = None
        self.matriz_binaria = None

    def analizar(
        self,
        respuestas_alumnos,
        respuestas_correctas
    ):
        """
        Prepara los datos para el análisis TRI.

        Todavía no realiza la calibración EM completa.
        """

        if (
            respuestas_alumnos is None
            or respuestas_correctas is None
        ):
            raise ValueError(
                "No hay respuestas de alumnos "
                "o respuestas correctas."
            )

        respuestas = self._normalizar_respuestas(
            respuestas_alumnos
        )

        correctas = self._normalizar_correctas(
            respuestas_correctas
        )

        if respuestas.shape[1] != len(correctas):
            raise ValueError(
                "La cantidad de columnas de respuestas "
                "no coincide con la cantidad de claves correctas."
            )

        self.matriz_binaria = self._crear_matriz_binaria(
            respuestas,
            correctas
        )

        puntaje_total = self.matriz_binaria.sum(axis=1)

        puntos_theta, pesos_theta = (
            self._crear_cuadratura()
        )

        parametros_iniciales = (
            self._inicializar_parametros(
                total_items=respuestas.shape[1]
            )
        )

        self.thetas = self._inicializar_theta(
            total_alumnos=respuestas.shape[0]
        )

        # De momento mostramos la estructura inicial.
        # Después este bloque será reemplazado por EM.
        resultados = []

        for indice, columna in enumerate(
            respuestas.columns
        ):
            serie_item = self.matriz_binaria[columna]

            # Puntaje total sin incluir el reactivo actual
            total_sin_item = puntaje_total - serie_item

            # Proporción de respuestas correctas
            p = float(serie_item.mean())

            # Correlación reactivo-total corregida
            r = self._correlacion_segura(
                serie_item,
                total_sin_item
            )

            a = float(
                parametros_iniciales["a"][indice]
            )
            b = float(
                parametros_iniciales["b"][indice]
            )
            c = float(
                parametros_iniciales["c"][indice]
            )

            flags = self._generar_flags(
                a=a,
                b=b,
                c=c
            )

            resultados.append({
                "Item": f"ITEM{indice + 1}",
                "Correcta": correctas.iloc[indice],
                "P": p,
                "R": r,
                "a": a,
                "b": b,
                "c": c,
                "Flag": ", ".join(flags)
            })

        self.resultados = pd.DataFrame(resultados)

        self.resumen = {
            "alumnos": respuestas.shape[0],
            "reactivos": respuestas.shape[1],
            "media_a": float(
                self.resultados["a"].mean()
            ),
            "media_b": float(
                self.resultados["b"].mean()
            ),
            "media_c": float(
                self.resultados["c"].mean()
            ),
            "items_k": [],
            "iteraciones": 0,
            "convergencia": False
        }

        self.detalle_opciones = pd.DataFrame()

        return (
            self.resultados,
            self.detalle_opciones,
            self.resumen
        )

    def _normalizar_respuestas(
        self,
        respuestas_alumnos
    ):
        return (
            respuestas_alumnos
            .copy()
            .fillna("0")
            .astype(str)
            .apply(
                lambda columna:
                columna.str.strip().str.upper()
            )
        )

    def _normalizar_correctas(
        self,
        respuestas_correctas
    ):
        return (
            respuestas_correctas
            .reset_index(drop=True)
            .fillna("0")
            .astype(str)
            .str.strip()
            .str.upper()
        )

    def _crear_matriz_binaria(
        self,
        respuestas,
        correctas
    ):
        """
        Convierte las respuestas a:

        1 = respuesta correcta
        0 = respuesta incorrecta
        """

        matriz = pd.DataFrame(
            index=respuestas.index
        )

        for indice, columna in enumerate(
            respuestas.columns
        ):
            correcta = correctas.iloc[indice]

            matriz[columna] = (
                respuestas[columna] == correcta
            ).astype(int)

        return matriz

    def _correlacion_segura(
        self,
        serie_x,
        serie_y
    ):
        """
        Calcula una correlación de Pearson evitando errores
        cuando alguna serie no tiene variación.
        """

        x = pd.Series(
            serie_x,
            dtype=float
        )

        y = pd.Series(
            serie_y,
            dtype=float
        )

        if len(x) < 2 or len(y) < 2:
            return 0.0

        if x.nunique() <= 1 or y.nunique() <= 1:
            return 0.0

        correlacion = x.corr(y)

        if pd.isna(correlacion):
            return 0.0

        return float(correlacion)

    def _probabilidad_3pl(
        self,
        theta,
        a,
        b,
        c
    ):
        """
        Calcula la probabilidad de respuesta correcta
        bajo el modelo logístico 3PL.
        """

        exponente = (
            -self.constante_logistica
            * a
            * (theta - b)
        )

        exponente = np.clip(
            exponente,
            -700,
            700
        )

        probabilidad = (
            c
            + (
                (1.0 - c)
                / (1.0 + np.exp(exponente))
            )
        )

        return np.clip(
            probabilidad,
            1e-9,
            1.0 - 1e-9
        )

    def _crear_cuadratura(self):
        """
        Genera puntos y pesos Gauss-Hermite
        para aproximar una distribución normal estándar.
        """

        puntos, pesos = (
            np.polynomial.hermite.hermgauss(
                self.puntos_cuadratura
            )
        )

        thetas = np.sqrt(2.0) * puntos
        pesos = pesos / np.sqrt(np.pi)

        thetas = np.clip(
            thetas,
            self.theta_min,
            self.theta_max
        )

        pesos = pesos / pesos.sum()

        return thetas, pesos

    def _inicializar_parametros(
        self,
        total_items
    ):
        """
        Inicializa los parámetros de todos los reactivos.
        """

        return {
            "a": np.full(
                total_items,
                self.a_inicial,
                dtype=float
            ),
            "b": np.full(
                total_items,
                self.b_inicial,
                dtype=float
            ),
            "c": np.full(
                total_items,
                self.c_inicial,
                dtype=float
            )
        }

    def _inicializar_theta(self, total_alumnos):
        """
        Inicializa la habilidad (theta) de todos los alumnos.

        En la primera iteración todos comienzan con
        una habilidad igual a cero.
        """

        return np.zeros(
            total_alumnos,
            dtype=float
        )

    def _generar_flags(
        self,
        a,
        b,
        c,
        flag_k=False,
        flag_f=False
    ):
        """
        Genera las flags de acuerdo con los límites.
        """

        flags = []

        if flag_k:
            flags.append("K")

        if flag_f:
            flags.append("F")

        if a < self.flag_a_bajo:
            flags.append("La")
        elif a > self.flag_a_alto:
            flags.append("Ha")

        if b < self.flag_b_bajo:
            flags.append("Lb")
        elif b > self.flag_b_alto:
            flags.append("Hb")

        if c < self.flag_c_bajo:
            flags.append("Lc")
        elif c > self.flag_c_alto:
            flags.append("Hc")

        return flags