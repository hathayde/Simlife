# ambiente.py
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterator

from configuracoes import (
    ALTURA,
    AREA_SIMULACAO_LARGURA,
    DURACAO_CICLO,
    DURACAO_ESTACAO,
    INTENSIDADE_LUZ_DIA,
    INTENSIDADE_LUZ_NOITE,
    INTENSIDADE_MINIMA_FOTOSSINTESE,
    NIVEL_NUTRIENTES_INICIAL,
    NIVEL_NUTRIENTES_MAXIMO,
    NIVEL_NUTRIENTES_MINIMO,
    RAIO_DISTRIBUICAO_NUTRIENTES,
    REGENERACAO_NATURAL_NUTRIENTES,
    TAMANHO_CELULA_NUTRIENTES,
    TEMPERATURA_MEDIA,
    UMIDADE_MEDIA,
    VARIACAO_INICIAL_NUTRIENTES,
)


# ============================================================
# CONDIÇÕES AMBIENTAIS
# ============================================================

@dataclass(slots=True)
class CondicoesAmbientais:
    """
    Representa um retrato das condições ambientais atuais.
    """

    ciclo_luz: str
    intensidade_luz: float
    temperatura: float
    umidade: float
    fator_sazonal: float
    nutrientes_medios: float


# ============================================================
# AMBIENTE
# ============================================================

class Ambiente:
    """
    Gerencia o ambiente físico e químico da simulação.

    Responsabilidades:

    - controlar dia e noite;
    - calcular intensidade luminosa;
    - calcular temperatura e umidade;
    - armazenar um mapa mutável de nutrientes;
    - permitir consumo local de nutrientes;
    - receber nutrientes provenientes da decomposição;
    - regenerar e difundir nutrientes;
    - calcular fatores ambientais para fotossíntese e metabolismo.
    """

    def __init__(
        self,
        duracao_ciclo: int = DURACAO_CICLO,
        duracao_estacao: int = DURACAO_ESTACAO,
        temperatura_media: float = TEMPERATURA_MEDIA,
        umidade_media: float = UMIDADE_MEDIA,
        semente: int | None = None,
    ) -> None:
        if duracao_ciclo <= 0:
            raise ValueError(
                "duracao_ciclo deve ser maior que zero."
            )

        if duracao_estacao <= 0:
            raise ValueError(
                "duracao_estacao deve ser maior que zero."
            )

        if TAMANHO_CELULA_NUTRIENTES <= 0:
            raise ValueError(
                "TAMANHO_CELULA_NUTRIENTES deve ser maior que zero."
            )

        self.duracao_ciclo = int(
            duracao_ciclo
        )

        self.duracao_estacao = int(
            duracao_estacao
        )

        self.temperatura_media = float(
            temperatura_media
        )

        self.umidade_media = self.limitar(
            float(
                umidade_media
            ),
            0.0,
            1.0,
        )

        self.tempo = 0

        self._gerador = random.Random(
            semente
        )

        self._ruido_temperatura = 0.0
        self._ruido_umidade = 0.0

        self.tamanho_celula_nutrientes = (
            TAMANHO_CELULA_NUTRIENTES
        )

        self.colunas_nutrientes = max(
            1,
            math.ceil(
                AREA_SIMULACAO_LARGURA
                / self.tamanho_celula_nutrientes
            ),
        )

        self.linhas_nutrientes = max(
            1,
            math.ceil(
                ALTURA
                / self.tamanho_celula_nutrientes
            ),
        )

        self._centros_nutrientes = (
            self._criar_centros_nutrientes()
        )

        self._mapa_base_nutrientes = (
            self._criar_mapa_base_nutrientes()
        )

        self._nutrientes = [
            linha.copy()
            for linha
            in self._mapa_base_nutrientes
        ]

        self._intervalo_difusao = 10
        self._fator_difusao = 0.025

    # ========================================================
    # ATUALIZAÇÃO
    # ========================================================

    def atualizar(
        self,
        passos: int = 1,
    ) -> None:
        """
        Avança o ambiente pelo número informado de passos.
        """

        if passos < 1:
            raise ValueError(
                "passos deve ser maior ou igual a 1."
            )

        for _ in range(
            passos
        ):
            self.tempo += 1

            self._atualizar_ruidos()
            self.regenerar_nutrientes_naturalmente()

            if (
                self.tempo
                % self._intervalo_difusao
                == 0
            ):
                self.difundir_nutrientes()

    def obter_condicoes(
        self,
    ) -> CondicoesAmbientais:
        """
        Retorna as condições ambientais atuais.
        """

        return CondicoesAmbientais(
            ciclo_luz=self.ciclo_luz(),
            intensidade_luz=(
                self.intensidade_luz()
            ),
            temperatura=self.temperatura(),
            umidade=self.umidade(),
            fator_sazonal=(
                self.fator_sazonal()
            ),
            nutrientes_medios=(
                self.obter_nivel_medio_nutrientes()
            ),
        )

    # ========================================================
    # LUZ E CICLO AMBIENTAL
    # ========================================================

    def ciclo_luz(
        self,
    ) -> str:
        """
        Retorna 'dia' ou 'noite' conforme a intensidade da luz.
        """

        limite_dia = max(
            INTENSIDADE_MINIMA_FOTOSSINTESE,
            INTENSIDADE_LUZ_NOITE + 0.08,
        )

        if (
            self.intensidade_luz()
            >= limite_dia
        ):
            return "dia"

        return "noite"

    def intensidade_luz(
        self,
    ) -> float:
        """
        Retorna a intensidade luminosa entre 0 e 1.

        A transição entre noite e dia é gradual.
        """

        duracao_total = (
            self.duracao_ciclo
            * 2
        )

        fase = (
            self.tempo
            % duracao_total
        ) / duracao_total

        onda_diurna = math.sin(
            2.0
            * math.pi
            * fase
        )

        componente_diurna = max(
            0.0,
            onda_diurna,
        )

        componente_diurna *= (
            self.fator_sazonal()
        )

        intensidade = (
            INTENSIDADE_LUZ_NOITE
            + (
                INTENSIDADE_LUZ_DIA
                - INTENSIDADE_LUZ_NOITE
            )
            * componente_diurna
        )

        return self.limitar(
            intensidade,
            0.0,
            1.0,
        )

    def fator_sazonal(
        self,
    ) -> float:
        """
        Retorna um fator sazonal aproximadamente entre 0,70 e 1,0.
        """

        fase = (
            self.tempo
            % self.duracao_estacao
        ) / self.duracao_estacao

        oscilacao = (
            math.sin(
                2.0
                * math.pi
                * fase
            )
            + 1.0
        ) / 2.0

        return (
            0.70
            + oscilacao * 0.30
        )

    # ========================================================
    # TEMPERATURA E UMIDADE
    # ========================================================

    def temperatura(
        self,
    ) -> float:
        """
        Retorna a temperatura atual em graus Celsius.
        """

        luz = (
            self.intensidade_luz()
        )

        componente_diurno = (
            luz - 0.5
        ) * 6.0

        componente_sazonal = (
            self.fator_sazonal()
            - 0.85
        ) * 14.0

        return (
            self.temperatura_media
            + componente_diurno
            + componente_sazonal
            + self._ruido_temperatura
        )

    def umidade(
        self,
    ) -> float:
        """
        Retorna a umidade normalizada entre 0 e 1.
        """

        luz = (
            self.intensidade_luz()
        )

        perda_por_luz = (
            luz * 0.12
        )

        ganho_noturno = (
            1.0 - luz
        ) * 0.08

        valor = (
            self.umidade_media
            - perda_por_luz
            + ganho_noturno
            + self._ruido_umidade
        )

        return self.limitar(
            valor,
            0.05,
            1.0,
        )

    # ========================================================
    # CONSULTA DE NUTRIENTES
    # ========================================================

    def nivel_nutrientes(
        self,
        x: float,
        y: float,
    ) -> float:
        """
        Retorna a concentração de nutrientes em uma posição.

        O valor é interpolado entre células próximas para evitar
        transições visuais e ecológicas abruptas.
        """

        x = self.limitar(
            float(x),
            0.0,
            float(
                AREA_SIMULACAO_LARGURA - 1
            ),
        )

        y = self.limitar(
            float(y),
            0.0,
            float(
                ALTURA - 1
            ),
        )

        coluna_decimal = (
            x
            / self.tamanho_celula_nutrientes
        )

        linha_decimal = (
            y
            / self.tamanho_celula_nutrientes
        )

        coluna_inicial = int(
            math.floor(
                coluna_decimal
            )
        )

        linha_inicial = int(
            math.floor(
                linha_decimal
            )
        )

        coluna_final = min(
            coluna_inicial + 1,
            self.colunas_nutrientes - 1,
        )

        linha_final = min(
            linha_inicial + 1,
            self.linhas_nutrientes - 1,
        )

        coluna_inicial = min(
            coluna_inicial,
            self.colunas_nutrientes - 1,
        )

        linha_inicial = min(
            linha_inicial,
            self.linhas_nutrientes - 1,
        )

        fracao_x = (
            coluna_decimal
            - coluna_inicial
        )

        fracao_y = (
            linha_decimal
            - linha_inicial
        )

        superior_esquerdo = (
            self._nutrientes[
                linha_inicial
            ][
                coluna_inicial
            ]
        )

        superior_direito = (
            self._nutrientes[
                linha_inicial
            ][
                coluna_final
            ]
        )

        inferior_esquerdo = (
            self._nutrientes[
                linha_final
            ][
                coluna_inicial
            ]
        )

        inferior_direito = (
            self._nutrientes[
                linha_final
            ][
                coluna_final
            ]
        )

        superior = (
            superior_esquerdo
            * (
                1.0 - fracao_x
            )
            + superior_direito
            * fracao_x
        )

        inferior = (
            inferior_esquerdo
            * (
                1.0 - fracao_x
            )
            + inferior_direito
            * fracao_x
        )

        valor = (
            superior
            * (
                1.0 - fracao_y
            )
            + inferior
            * fracao_y
        )

        return self.limitar(
            valor,
            NIVEL_NUTRIENTES_MINIMO,
            NIVEL_NUTRIENTES_MAXIMO,
        )

    def obter_nivel_medio_nutrientes(
        self,
    ) -> float:
        """
        Retorna a média de nutrientes de todo o ambiente.
        """

        total = 0.0
        quantidade = 0

        for linha in self._nutrientes:
            for valor in linha:
                total += valor
                quantidade += 1

        if quantidade <= 0:
            return 0.0

        return (
            total / quantidade
        )

    def obter_mapa_nutrientes(
        self,
    ) -> tuple[
        tuple[float, ...],
        ...,
    ]:
        """
        Retorna uma cópia imutável do mapa de nutrientes.
        """

        return tuple(
            tuple(
                linha
            )
            for linha
            in self._nutrientes
        )

    # ========================================================
    # CONSUMO DE NUTRIENTES
    # ========================================================

    def consumir_nutrientes(
        self,
        x: float,
        y: float,
        quantidade: float,
        raio: float | None = None,
    ) -> float:
        """
        Remove nutrientes de uma região.

        Retorna a quantidade efetivamente consumida.
        """

        quantidade = max(
            0.0,
            float(
                quantidade
            ),
        )

        if quantidade <= 0.0:
            return 0.0

        if raio is None:
            raio = (
                self.tamanho_celula_nutrientes
                * 0.75
            )

        raio = max(
            1.0,
            float(
                raio
            ),
        )

        celulas = list(
            self._iterar_celulas_no_raio(
                x=x,
                y=y,
                raio=raio,
            )
        )

        if not celulas:
            return 0.0

        restante = quantidade
        consumido_total = 0.0

        # Mais de uma passagem reduz perdas causadas pelo esgotamento
        # de células individuais.
        for _ in range(
            3
        ):
            if restante <= 0.000001:
                break

            pesos: list[
                tuple[int, int, float]
            ] = []

            peso_total = 0.0

            for (
                linha,
                coluna,
                peso_espacial,
            ) in celulas:
                disponivel = max(
                    0.0,
                    self._nutrientes[
                        linha
                    ][
                        coluna
                    ]
                    - NIVEL_NUTRIENTES_MINIMO,
                )

                peso = (
                    disponivel
                    * peso_espacial
                )

                if peso <= 0.0:
                    continue

                pesos.append(
                    (
                        linha,
                        coluna,
                        peso,
                    )
                )

                peso_total += peso

            if peso_total <= 0.0:
                break

            consumido_passagem = 0.0

            for (
                linha,
                coluna,
                peso,
            ) in pesos:
                proporcao = (
                    peso / peso_total
                )

                solicitado = (
                    restante
                    * proporcao
                )

                disponivel = max(
                    0.0,
                    self._nutrientes[
                        linha
                    ][
                        coluna
                    ]
                    - NIVEL_NUTRIENTES_MINIMO,
                )

                retirado = min(
                    solicitado,
                    disponivel,
                )

                self._nutrientes[
                    linha
                ][
                    coluna
                ] -= retirado

                consumido_passagem += (
                    retirado
                )

            consumido_total += (
                consumido_passagem
            )

            restante -= (
                consumido_passagem
            )

            if consumido_passagem <= 0.000001:
                break

        return consumido_total

    # ========================================================
    # ADIÇÃO DE NUTRIENTES
    # ========================================================

    def adicionar_nutrientes(
        self,
        x: float,
        y: float,
        quantidade: float,
        raio: float = RAIO_DISTRIBUICAO_NUTRIENTES,
    ) -> float:
        """
        Adiciona nutrientes ao redor de uma posição.

        É usado principalmente quando carcaças se decompõem.

        Retorna a quantidade efetivamente adicionada.
        """

        quantidade = max(
            0.0,
            float(
                quantidade
            ),
        )

        raio = max(
            1.0,
            float(
                raio
            ),
        )

        if quantidade <= 0.0:
            return 0.0

        celulas = list(
            self._iterar_celulas_no_raio(
                x=x,
                y=y,
                raio=raio,
            )
        )

        if not celulas:
            return 0.0

        restante = quantidade
        adicionado_total = 0.0

        for _ in range(
            3
        ):
            if restante <= 0.000001:
                break

            pesos: list[
                tuple[int, int, float]
            ] = []

            peso_total = 0.0

            for (
                linha,
                coluna,
                peso_espacial,
            ) in celulas:
                capacidade = max(
                    0.0,
                    NIVEL_NUTRIENTES_MAXIMO
                    - self._nutrientes[
                        linha
                    ][
                        coluna
                    ],
                )

                peso = (
                    capacidade
                    * peso_espacial
                )

                if peso <= 0.0:
                    continue

                pesos.append(
                    (
                        linha,
                        coluna,
                        peso,
                    )
                )

                peso_total += peso

            if peso_total <= 0.0:
                break

            adicionado_passagem = 0.0

            for (
                linha,
                coluna,
                peso,
            ) in pesos:
                proporcao = (
                    peso / peso_total
                )

                solicitado = (
                    restante
                    * proporcao
                )

                capacidade = max(
                    0.0,
                    NIVEL_NUTRIENTES_MAXIMO
                    - self._nutrientes[
                        linha
                    ][
                        coluna
                    ],
                )

                adicionado = min(
                    solicitado,
                    capacidade,
                )

                self._nutrientes[
                    linha
                ][
                    coluna
                ] += adicionado

                adicionado_passagem += (
                    adicionado
                )

            adicionado_total += (
                adicionado_passagem
            )

            restante -= (
                adicionado_passagem
            )

            if adicionado_passagem <= 0.000001:
                break

        return adicionado_total

    # ========================================================
    # REGENERAÇÃO E DIFUSÃO
    # ========================================================

    def regenerar_nutrientes_naturalmente(
        self,
    ) -> None:
        """
        Move lentamente cada célula em direção ao seu nível-base.
        """

        taxa = max(
            0.0,
            REGENERACAO_NATURAL_NUTRIENTES,
        )

        if taxa <= 0.0:
            return

        for linha in range(
            self.linhas_nutrientes
        ):
            for coluna in range(
                self.colunas_nutrientes
            ):
                atual = (
                    self._nutrientes[
                        linha
                    ][
                        coluna
                    ]
                )

                alvo = (
                    self._mapa_base_nutrientes[
                        linha
                    ][
                        coluna
                    ]
                )

                novo_valor = (
                    atual
                    + (
                        alvo - atual
                    )
                    * taxa
                )

                self._nutrientes[
                    linha
                ][
                    coluna
                ] = self.limitar(
                    novo_valor,
                    NIVEL_NUTRIENTES_MINIMO,
                    NIVEL_NUTRIENTES_MAXIMO,
                )

    def difundir_nutrientes(
        self,
    ) -> None:
        """
        Espalha lentamente nutrientes entre células vizinhas.
        """

        novo_mapa = [
            linha.copy()
            for linha
            in self._nutrientes
        ]

        for linha in range(
            self.linhas_nutrientes
        ):
            for coluna in range(
                self.colunas_nutrientes
            ):
                vizinhos: list[
                    float
                ] = []

                for deslocamento_linha in (
                    -1,
                    0,
                    1,
                ):
                    for deslocamento_coluna in (
                        -1,
                        0,
                        1,
                    ):
                        if (
                            deslocamento_linha == 0
                            and deslocamento_coluna == 0
                        ):
                            continue

                        linha_vizinha = (
                            linha
                            + deslocamento_linha
                        )

                        coluna_vizinha = (
                            coluna
                            + deslocamento_coluna
                        )

                        if not (
                            0
                            <= linha_vizinha
                            < self.linhas_nutrientes
                        ):
                            continue

                        if not (
                            0
                            <= coluna_vizinha
                            < self.colunas_nutrientes
                        ):
                            continue

                        vizinhos.append(
                            self._nutrientes[
                                linha_vizinha
                            ][
                                coluna_vizinha
                            ]
                        )

                if not vizinhos:
                    continue

                media_vizinhos = (
                    sum(
                        vizinhos
                    )
                    / len(
                        vizinhos
                    )
                )

                atual = (
                    self._nutrientes[
                        linha
                    ][
                        coluna
                    ]
                )

                novo_valor = (
                    atual
                    + (
                        media_vizinhos
                        - atual
                    )
                    * self._fator_difusao
                )

                novo_mapa[
                    linha
                ][
                    coluna
                ] = self.limitar(
                    novo_valor,
                    NIVEL_NUTRIENTES_MINIMO,
                    NIVEL_NUTRIENTES_MAXIMO,
                )

        self._nutrientes = novo_mapa

    def regenerar_mapa_nutrientes(
        self,
    ) -> None:
        """
        Cria uma nova distribuição ambiental de nutrientes.
        """

        self._centros_nutrientes = (
            self._criar_centros_nutrientes()
        )

        self._mapa_base_nutrientes = (
            self._criar_mapa_base_nutrientes()
        )

        self._nutrientes = [
            linha.copy()
            for linha
            in self._mapa_base_nutrientes
        ]

    # Compatibilidade com a versão anterior.
    def regenerar_centros_nutrientes(
        self,
    ) -> None:
        self.regenerar_mapa_nutrientes()

    # ========================================================
    # FATORES BIOLÓGICOS
    # ========================================================

    def fator_fotossintese(
        self,
        x: float,
        y: float,
    ) -> float:
        """
        Retorna um multiplicador ambiental para a fotossíntese.

        Considera:

        - intensidade da luz;
        - nutrientes locais;
        - temperatura;
        - umidade.
        """

        luz = self.intensidade_luz()

        if (
            luz
            < INTENSIDADE_MINIMA_FOTOSSINTESE
        ):
            return 0.0

        nutrientes = (
            self.nivel_nutrientes(
                x,
                y,
            )
        )

        fator_temperatura = (
            self.fator_temperatura(
                temperatura=(
                    self.temperatura()
                ),
                temperatura_otima=26.0,
                tolerancia=15.0,
            )
        )

        fator_umidade = (
            self.fator_umidade(
                umidade=self.umidade(),
                umidade_otima=0.75,
                tolerancia=0.60,
            )
        )

        fator = (
            luz
            * nutrientes
            * fator_temperatura
            * fator_umidade
        )

        return self.limitar(
            fator,
            0.0,
            1.5,
        )

    def fator_metabolico(
        self,
    ) -> float:
        """
        Retorna um multiplicador global de atividade metabólica.
        """

        fator_temperatura = (
            self.fator_temperatura(
                temperatura=(
                    self.temperatura()
                ),
                temperatura_otima=28.0,
                tolerancia=20.0,
            )
        )

        fator_umidade = (
            self.fator_umidade(
                umidade=self.umidade(),
                umidade_otima=0.70,
                tolerancia=0.70,
            )
        )

        fator = (
            fator_temperatura
            * 0.70
            + fator_umidade
            * 0.30
        )

        return self.limitar(
            fator,
            0.20,
            1.0,
        )

    def custo_metabolico(
        self,
    ) -> float:
        """
        Retorna o custo ambiental adicional por passo.
        """

        temperatura = (
            self.temperatura()
        )

        umidade = (
            self.umidade()
        )

        custo = 0.0

        if temperatura < 10.0:
            custo += (
                10.0 - temperatura
            ) * 0.0008

        if temperatura > 38.0:
            custo += (
                temperatura - 38.0
            ) * 0.0015

        if umidade < 0.30:
            custo += (
                0.30 - umidade
            ) * 0.04

        return max(
            0.0,
            custo,
        )

    def degradacao_carcaca(
        self,
    ) -> float:
        """
        Retorna a taxa de degradação natural das carcaças.

        Calor e umidade aceleram a decomposição.
        """

        temperatura = (
            self.temperatura()
        )

        umidade = (
            self.umidade()
        )

        fator_temperatura = self.limitar(
            (
                temperatura - 5.0
            ) / 35.0,
            0.10,
            1.50,
        )

        fator_umidade = self.limitar(
            umidade / 0.70,
            0.20,
            1.50,
        )

        return (
            0.03
            * fator_temperatura
            * fator_umidade
        )

    # ========================================================
    # CONSTRUÇÃO DO MAPA
    # ========================================================

    def _criar_mapa_base_nutrientes(
        self,
    ) -> list[list[float]]:
        """
        Cria o mapa-base de nutrientes.

        O mapa combina:

        - nível inicial;
        - variação aleatória;
        - manchas concentradas;
        - gradiente central;
        - variações espaciais suaves.
        """

        mapa: list[
            list[float]
        ] = []

        for linha in range(
            self.linhas_nutrientes
        ):
            linha_nutrientes: list[
                float
            ] = []

            for coluna in range(
                self.colunas_nutrientes
            ):
                x = (
                    coluna
                    * self.tamanho_celula_nutrientes
                    + self.tamanho_celula_nutrientes
                    / 2.0
                )

                y = (
                    linha
                    * self.tamanho_celula_nutrientes
                    + self.tamanho_celula_nutrientes
                    / 2.0
                )

                variacao_aleatoria = (
                    self._gerador.uniform(
                        -VARIACAO_INICIAL_NUTRIENTES,
                        VARIACAO_INICIAL_NUTRIENTES,
                    )
                )

                concentracao_centros = (
                    self._concentracao_centros(
                        x,
                        y,
                    )
                )

                gradiente_central = (
                    self._gradiente_central(
                        x,
                        y,
                    )
                )

                variacao_espacial = (
                    self._variacao_espacial(
                        x,
                        y,
                    )
                )

                valor = (
                    NIVEL_NUTRIENTES_INICIAL
                    + variacao_aleatoria
                    + concentracao_centros
                    * 0.25
                    + gradiente_central
                    * 0.08
                    + (
                        variacao_espacial
                        - 0.5
                    )
                    * 0.12
                )

                valor = self.limitar(
                    valor,
                    NIVEL_NUTRIENTES_MINIMO,
                    NIVEL_NUTRIENTES_MAXIMO,
                )

                linha_nutrientes.append(
                    valor
                )

            mapa.append(
                linha_nutrientes
            )

        return mapa

    def _criar_centros_nutrientes(
        self,
    ) -> list[
        tuple[
            float,
            float,
            float,
            float,
        ]
    ]:
        """
        Cria manchas de concentração de nutrientes.

        Cada item possui:

        - coordenada X;
        - coordenada Y;
        - intensidade;
        - raio.
        """

        quantidade = 6

        centros: list[
            tuple[
                float,
                float,
                float,
                float,
            ]
        ] = []

        for _ in range(
            quantidade
        ):
            centros.append(
                (
                    self._gerador.uniform(
                        0.0,
                        float(
                            AREA_SIMULACAO_LARGURA
                        ),
                    ),
                    self._gerador.uniform(
                        0.0,
                        float(
                            ALTURA
                        ),
                    ),
                    self._gerador.uniform(
                        0.25,
                        0.75,
                    ),
                    self._gerador.uniform(
                        80.0,
                        220.0,
                    ),
                )
            )

        return centros

    def obter_centros_nutrientes(
        self,
    ) -> tuple[
        tuple[
            float,
            float,
            float,
            float,
        ],
        ...,
    ]:
        """
        Retorna uma cópia imutável dos centros de nutrientes.
        """

        return tuple(
            self._centros_nutrientes
        )

    def _concentracao_centros(
        self,
        x: float,
        y: float,
    ) -> float:
        """
        Calcula a influência das manchas de nutrientes.
        """

        concentracao_total = 0.0

        for (
            centro_x,
            centro_y,
            intensidade,
            raio,
        ) in self._centros_nutrientes:
            dx = x - centro_x
            dy = y - centro_y

            distancia_quadrada = (
                dx * dx
                + dy * dy
            )

            raio_quadrado = max(
                raio * raio,
                1.0,
            )

            concentracao = (
                intensidade
                * math.exp(
                    -distancia_quadrada
                    / (
                        2.0
                        * raio_quadrado
                    )
                )
            )

            concentracao_total += (
                concentracao
            )

        return self.limitar(
            concentracao_total,
            0.0,
            1.0,
        )

    # ========================================================
    # ITERAÇÃO ESPACIAL
    # ========================================================

    def _iterar_celulas_no_raio(
        self,
        x: float,
        y: float,
        raio: float,
    ) -> Iterator[
        tuple[
            int,
            int,
            float,
        ]
    ]:
        """
        Retorna células próximas de uma coordenada.

        Cada resultado contém:

        - linha;
        - coluna;
        - peso espacial.
        """

        x = self.limitar(
            float(x),
            0.0,
            float(
                AREA_SIMULACAO_LARGURA - 1
            ),
        )

        y = self.limitar(
            float(y),
            0.0,
            float(
                ALTURA - 1
            ),
        )

        raio = max(
            1.0,
            float(
                raio
            ),
        )

        coluna_minima = max(
            0,
            int(
                (
                    x - raio
                )
                // self.tamanho_celula_nutrientes
            ),
        )

        coluna_maxima = min(
            self.colunas_nutrientes - 1,
            int(
                (
                    x + raio
                )
                // self.tamanho_celula_nutrientes
            ),
        )

        linha_minima = max(
            0,
            int(
                (
                    y - raio
                )
                // self.tamanho_celula_nutrientes
            ),
        )

        linha_maxima = min(
            self.linhas_nutrientes - 1,
            int(
                (
                    y + raio
                )
                // self.tamanho_celula_nutrientes
            ),
        )

        raio_ampliado = (
            raio
            + self.tamanho_celula_nutrientes
            * 0.75
        )

        for linha in range(
            linha_minima,
            linha_maxima + 1,
        ):
            for coluna in range(
                coluna_minima,
                coluna_maxima + 1,
            ):
                centro_x = (
                    coluna
                    * self.tamanho_celula_nutrientes
                    + self.tamanho_celula_nutrientes
                    / 2.0
                )

                centro_y = (
                    linha
                    * self.tamanho_celula_nutrientes
                    + self.tamanho_celula_nutrientes
                    / 2.0
                )

                distancia = math.hypot(
                    centro_x - x,
                    centro_y - y,
                )

                if distancia > raio_ampliado:
                    continue

                peso = max(
                    0.05,
                    1.0
                    - distancia
                    / max(
                        raio_ampliado,
                        0.001,
                    ),
                )

                yield (
                    linha,
                    coluna,
                    peso,
                )

    # ========================================================
    # RUÍDO E GRADIENTES
    # ========================================================

    def _atualizar_ruidos(
        self,
    ) -> None:
        """
        Atualiza pequenas flutuações ambientais gradualmente.
        """

        alvo_temperatura = (
            self._gerador.uniform(
                -1.5,
                1.5,
            )
        )

        alvo_umidade = (
            self._gerador.uniform(
                -0.04,
                0.04,
            )
        )

        self._ruido_temperatura += (
            alvo_temperatura
            - self._ruido_temperatura
        ) * 0.01

        self._ruido_umidade += (
            alvo_umidade
            - self._ruido_umidade
        ) * 0.01

    @staticmethod
    def _gradiente_central(
        x: float,
        y: float,
    ) -> float:
        """
        Retorna um gradiente com maior valor no centro do mapa.
        """

        centro_x = (
            AREA_SIMULACAO_LARGURA
            / 2.0
        )

        centro_y = (
            ALTURA / 2.0
        )

        distancia = math.hypot(
            x - centro_x,
            y - centro_y,
        )

        distancia_maxima = math.hypot(
            centro_x,
            centro_y,
        )

        if distancia_maxima <= 0.0:
            return 0.0

        return max(
            0.0,
            1.0
            - distancia
            / distancia_maxima,
        )

    @staticmethod
    def _variacao_espacial(
        x: float,
        y: float,
    ) -> float:
        """
        Gera uma variação espacial determinística entre 0 e 1.
        """

        valor = (
            math.sin(
                x * 0.018
            )
            + math.cos(
                y * 0.015
            )
            + math.sin(
                (
                    x + y
                )
                * 0.008
            )
        )

        normalizado = (
            valor + 3.0
        ) / 6.0

        return Ambiente.limitar(
            normalizado,
            0.0,
            1.0,
        )

    # ========================================================
    # FUNÇÕES MATEMÁTICAS
    # ========================================================

    @staticmethod
    def fator_temperatura(
        temperatura: float,
        temperatura_otima: float,
        tolerancia: float,
    ) -> float:
        """
        Calcula a adequação térmica entre 0 e 1.
        """

        if tolerancia <= 0.0:
            raise ValueError(
                "tolerancia deve ser maior que zero."
            )

        distancia = abs(
            temperatura
            - temperatura_otima
        )

        return Ambiente.limitar(
            1.0
            - distancia
            / tolerancia,
            0.0,
            1.0,
        )

    @staticmethod
    def fator_umidade(
        umidade: float,
        umidade_otima: float,
        tolerancia: float,
    ) -> float:
        """
        Calcula a adequação da umidade entre 0 e 1.
        """

        if tolerancia <= 0.0:
            raise ValueError(
                "tolerancia deve ser maior que zero."
            )

        distancia = abs(
            umidade
            - umidade_otima
        )

        return Ambiente.limitar(
            1.0
            - distancia
            / tolerancia,
            0.0,
            1.0,
        )

    @staticmethod
    def limitar(
        valor: float,
        minimo: float,
        maximo: float,
    ) -> float:
        """
        Limita um valor ao intervalo informado.
        """

        if minimo > maximo:
            raise ValueError(
                "minimo não pode ser maior que maximo."
            )

        return max(
            minimo,
            min(
                float(valor),
                maximo,
            ),
        )

    def __repr__(
        self,
    ) -> str:
        condicoes = (
            self.obter_condicoes()
        )

        return (
            "Ambiente("
            f"tempo={self.tempo}, "
            f"ciclo={condicoes.ciclo_luz!r}, "
            f"luz={condicoes.intensidade_luz:.2f}, "
            f"temperatura={condicoes.temperatura:.2f}, "
            f"umidade={condicoes.umidade:.2f}, "
            f"nutrientes={condicoes.nutrientes_medios:.2f}"
            ")"
        )


# ============================================================
# AMBIENTE GLOBAL DE COMPATIBILIDADE
# ============================================================

_ambiente_padrao = Ambiente()


def nivel_nutrientes(
    x: float,
    y: float,
) -> float:
    """
    Compatibilidade com versões anteriores do projeto.
    """

    return _ambiente_padrao.nivel_nutrientes(
        x,
        y,
    )


def fator_fotossintese(
    x: float,
    y: float,
) -> float:
    """
    Compatibilidade com versões anteriores do projeto.
    """

    return _ambiente_padrao.fator_fotossintese(
        x,
        y,
    )


def atualizar_ambiente(
    passos: int = 1,
) -> None:
    """
    Atualiza o ambiente global de compatibilidade.
    """

    _ambiente_padrao.atualizar(
        passos
    )
