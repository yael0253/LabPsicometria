import numpy as np
import pandas as pd


class MotorTRI:
    """
    Motor inicial para análisis TRI.

    Esta primera versión:
    - prepara la matriz binaria;
    - calcula P y R;
    - detecta Flag K;
    - deja preparada la estructura para estimar a, b y c.
    """

    def __init__(self):
        self.resultados = None
        self.detalle_opciones = None
        self.resumen = None

    def analizar(self, respuestas_alumnos, respuestas_correctas):
        if respuestas_alumnos is None or respuestas_correctas is None:
            raise ValueError(
                "No hay respuestas de alumnos o respuestas correctas."
            )

        respuestas = (
            respuestas_alumnos
            .copy()
            .fillna("0")
            .astype(str)
            .apply(lambda columna: columna.str.strip().str.upper())
        )

        correctas = (
            respuestas_correctas
            .reset_index(drop=True)
            .fillna("0")
            .astype(str)
            .str.strip()
            .str.upper()
        )

        if respuestas.shape[1] != len(correctas):
            raise ValueError(
                "La cantidad de columnas de respuestas no coincide "
                "con la cantidad de respuestas correctas."
            )

        matriz_binaria = self._crear_matriz_binaria(
            respuestas,
            correctas
        )

        puntaje_total = matriz_binaria.sum(axis=1)

        resultados = []
        detalle_opciones = []

        for indice, columna in enumerate(respuestas.columns):
            numero_item = indice + 1
            correcta = correctas.iloc[indice]

            serie_item = matriz_binaria[columna]
            total_sin_item = puntaje_total - serie_item

            p = float(serie_item.mean())
            r = self._correlacion_segura(
                serie_item,
                total_sin_item
            )

            correlaciones_opciones = {}

            valores_columna = respuestas[columna]

            opciones = sorted(
                opcion
                for opcion in valores_columna.unique()
                if opcion not in {
                    "",
                    "0",
                    "NAN",
                    "NONE",
                    "O",
                    "N"
                }
            )

            for opcion in opciones:
                seleccion_opcion = (
                    valores_columna == opcion
                ).astype(int)

                correlacion = self._correlacion_segura(
                    seleccion_opcion,
                    total_sin_item
                )

                correlaciones_opciones[opcion] = correlacion

                detalle_opciones.append({
                    "Item": f"ITEM{numero_item}",
                    "Opcion": opcion,
                    "Es_correcta": opcion == correcta,
                    "N": int(seleccion_opcion.sum()),
                    "Proporcion": float(
                        seleccion_opcion.mean()
                    ),
                    "R": float(correlacion)
                })

            correlacion_correcta = correlaciones_opciones.get(
                correcta,
                r
            )

            distractores_superiores = [
                opcion
                for opcion, correlacion
                in correlaciones_opciones.items()
                if (
                    opcion != correcta
                    and correlacion > correlacion_correcta
                )
            ]

            flag_k = len(distractores_superiores) > 0

            # Valores provisionales.
            # Después serán reemplazados por estimación 3PL real.
            a = self._estimacion_inicial_a(r)
            b = self._estimacion_inicial_b(p)
            c = self._estimacion_inicial_c(
                numero_opciones=max(len(opciones), 1)
            )

            flags = self._generar_flags(
                a=a,
                b=b,
                c=c,
                flag_k=flag_k
            )

            resultados.append({
                "Item": f"ITEM{numero_item}",
                "Correcta": correcta,
                "P": p,
                "R": r,
                "a": a,
                "b": b,
                "c": c,
                "Flag": ", ".join(flags),
                "Distractores_superiores": ", ".join(
                    distractores_superiores
                )
            })

        self.resultados = pd.DataFrame(resultados)
        self.detalle_opciones = pd.DataFrame(
            detalle_opciones
        )

        items_k = self.resultados[
            self.resultados["Flag"].str.contains(
                r"(^|,\s*)K($|,)",
                regex=True,
                na=False
            )
        ]

        self.resumen = {
            "alumnos": len(respuestas),
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
            "items_k": items_k["Item"].tolist()
        }

        return (
            self.resultados,
            self.detalle_opciones,
            self.resumen
        )

    def _crear_matriz_binaria(
        self,
        respuestas,
        correctas
    ):
        matriz = pd.DataFrame(index=respuestas.index)

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
        serie_a,
        serie_b
    ):
        if (
            serie_a.nunique() <= 1
            or serie_b.nunique() <= 1
        ):
            return 0.0

        correlacion = serie_a.corr(serie_b)

        if pd.isna(correlacion):
            return 0.0

        return float(correlacion)

    def _estimacion_inicial_a(self, r):
        """
        Aproximación provisional.
        No es todavía la estimación 3PL de Xcalibre.
        """

        valor = max(0.05, abs(float(r)) * 4.0)

        return float(
            np.clip(valor, 0.05, 6.0)
        )

    def _estimacion_inicial_b(self, p):
        """
        Aproximación provisional basada en logit.

        P alto produce b negativo.
        P bajo produce b positivo.
        """

        p_ajustado = float(
            np.clip(p, 0.001, 0.999)
        )

        b = np.log(
            (1.0 - p_ajustado) / p_ajustado
        )

        return float(
            np.clip(b, -4.0, 4.0)
        )

    def _estimacion_inicial_c(
        self,
        numero_opciones
    ):
        """
        Aproximación inicial por azar.
        Después será estimada con el modelo 3PL.
        """

        if numero_opciones <= 0:
            return 0.0

        c = 1.0 / numero_opciones

        return float(
            np.clip(c, 0.0, 0.70)
        )

    def _generar_flags(
        self,
        a,
        b,
        c,
        flag_k
    ):
        flags = []

        if flag_k:
            flags.append("K")

        if a < 0.30:
            flags.append("La")
        elif a > 4.00:
            flags.append("Ha")

        if b < -3.00:
            flags.append("Lb")
        elif b > 3.00:
            flags.append("Hb")

        if c < 0.00:
            flags.append("Lc")
        elif c > 0.40:
            flags.append("Hc")

        return flags