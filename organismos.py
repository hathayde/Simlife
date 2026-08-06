# organismos.py
from __future__ import annotations

import math
import random
import string
from typing import Any

import pygame

from configuracoes import (
    ALTURA,
    AREA_SIMULACAO_LARGURA,
    ATAQUE_INICIAL_MAXIMO,
    ATAQUE_INICIAL_MINIMO,
    ATAQUE_MAXIMO,
    ATAQUE_MINIMO,
    CORES_ESTRATEGIAS,
    CONSUMO_MAXIMO_CARCACA_POR_FRAME,
    COR_CARCACA,
    CUSTO_METABOLICO_BACTERIA,
    CUSTO_MOVIMENTO_BACTERIA,
    CUSTO_NOTURNO_FOTOSSINTETICA,
    CUSTO_REPRODUCAO_BACTERIA,
    DEFESA_INICIAL_MAXIMA,
    DEFESA_INICIAL_MINIMA,
    DEFESA_MAXIMA,
    DEFESA_MINIMA,
    DEGRADACAO_CARCACA_PADRAO,
    DISTANCIA_AMOSTRA_QUIMIOTAXIA,
    DISTANCIA_GENETICA_NOVA_ESPECIE,
    DISTANCIA_MAXIMA_DESCENDENTE,
    DIVISAO_ENERGIA_REPRODUCAO,
    EFICIENCIA_CONSUMO_CARCACA,
    EFICIENCIA_FOTOSSINTESE_INICIAL_MAXIMA,
    EFICIENCIA_FOTOSSINTESE_INICIAL_MINIMA,
    EFICIENCIA_FOTOSSINTESE_MAXIMA,
    EFICIENCIA_FOTOSSINTESE_MINIMA,
    EFICIENCIA_METABOLICA_INICIAL_MAXIMA,
    EFICIENCIA_METABOLICA_INICIAL_MINIMA,
    EFICIENCIA_METABOLICA_MAXIMA,
    EFICIENCIA_METABOLICA_MINIMA,
    ENERGIA_INICIAL_BACTERIA,
    ENERGIA_INICIAL_CARCACA,
    ENERGIA_MAXIMA_BACTERIA,
    ENERGIA_MINIMA_CARCACA,
    ENERGIA_PREDACAO_BACTERIA,
    ENERGIA_REPRODUCAO_BACTERIA,
    ESPERANCA_VIDA_INICIAL_MAXIMA,
    ESPERANCA_VIDA_INICIAL_MINIMA,
    ESPERANCA_VIDA_MINIMA,
    ESTRATEGIA_FOTOSSINTESE,
    ESTRATEGIA_NECROFAGIA,
    ESTRATEGIA_PREDACAO,
    ESTRATEGIAS_ALIMENTARES,
    FATOR_REPULSAO,
    GANHO_BASE_FOTOSSINTESE,
    INTENSIDADE_MINIMA_FOTOSSINTESE,
    INTENSIDADE_QUIMIOTAXIA_INTELIGENTE,
    INTENSIDADE_QUIMIOTAXIA_PADRAO,
    MOVIMENTO_FOTOSSINTETICA_MAXIMO,
    MOVIMENTO_FOTOSSINTETICA_MINIMO,
    MUTACAO_ATAQUE_DESVIO,
    MUTACAO_DEFESA_DESVIO,
    MUTACAO_EFICIENCIA_FOTOSSINTESE_DESVIO,
    MUTACAO_EFICIENCIA_METABOLICA_DESVIO,
    MUTACAO_ESPERANCA_VIDA_MAXIMA,
    MUTACAO_RAIO_DETECCAO_DESVIO,
    MUTACAO_TAMANHO_MAXIMA,
    MUTACAO_TAXA_MUTACAO_DESVIO,
    MUTACAO_VELOCIDADE_DESVIO,
    PENALIDADE_FALHA_PREDACAO,
    PENALIDADE_SEM_ALIMENTO,
    PREDADOR_PODE_ATACAR_MESMA_ESPECIE,
    PROBABILIDADE_MUTACAO_ESPECIE_ALVO,
    PROBABILIDADE_MUTACAO_ESTRATEGIA,
    PROBABILIDADE_REPRODUCAO_POR_FRAME,
    RAIO_BUSCA_CARCACA_PADRAO,
    RAIO_CACA_PADRAO,
    RAIO_DETECCAO_INICIAL_MAXIMO,
    RAIO_DETECCAO_INICIAL_MINIMO,
    RAIO_DETECCAO_MAXIMO,
    RAIO_DETECCAO_MINIMO,
    RUIDO_BROWNIANO_INTELIGENTE,
    RUIDO_BROWNIANO_PADRAO,
    TAMANHO_CARCACA,
    TAMANHO_INICIAL_MAXIMO,
    TAMANHO_INICIAL_MINIMO,
    TAMANHO_MAXIMO_BACTERIA,
    TAMANHO_MINIMO_BACTERIA,
    TAXA_MUTACAO_INICIAL_MAXIMA,
    TAXA_MUTACAO_INICIAL_MINIMA,
    TAXA_MUTACAO_MAXIMA,
    TAXA_MUTACAO_MINIMA,
    TEMPO_RECUPERACAO_ATAQUE,
    VELOCIDADE_INICIAL_MAXIMA,
    VELOCIDADE_INICIAL_MINIMA,
    VELOCIDADE_MAXIMA,
    VELOCIDADE_MINIMA,
)


# ============================================================
# REGISTRO VISUAL DE ESPÉCIES
# ============================================================

cores_especies: dict[
    str,
    tuple[int, int, int],
] = {}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def limitar(
    valor: float,
    minimo: float,
    maximo: float,
) -> float:
    """
    Limita um valor numérico ao intervalo informado.
    """

    if minimo > maximo:
        raise ValueError(
            "minimo não pode ser maior que maximo."
        )

    return max(
        minimo,
        min(
            valor,
            maximo,
        ),
    )


def gerar_identificador_especie(
    prefixo: str = "bacteria",
) -> str:
    """
    Gera um identificador curto para uma nova espécie.
    """

    caracteres = (
        string.ascii_lowercase
        + string.digits
    )

    sufixo = "".join(
        random.choice(caracteres)
        for _ in range(5)
    )

    return f"{prefixo}_{sufixo}"


def obter_cor_especie(
    especie: str,
) -> tuple[int, int, int]:
    """
    Retorna uma cor consistente para uma espécie.

    A estratégia alimentar não define a cor principal da bactéria.
    A cor principal representa a espécie; um marcador interno representa
    a estratégia alimentar.
    """

    if especie in cores_especies:
        return cores_especies[especie]

    gerador = random.Random(
        especie
    )

    cor = (
        gerador.randint(70, 235),
        gerador.randint(70, 235),
        gerador.randint(70, 235),
    )

    cores_especies[especie] = cor

    return cor


def obter_prefixo_estrategia(
    estrategia: str,
) -> str:
    """
    Retorna um prefixo curto usado nos nomes das espécies.
    """

    prefixos = {
        ESTRATEGIA_FOTOSSINTESE: "foto",
        ESTRATEGIA_PREDACAO: "pred",
        ESTRATEGIA_NECROFAGIA: "necro",
    }

    return prefixos.get(
        estrategia,
        "bacteria",
    )


# ============================================================
# ORGANISMO BASE
# ============================================================

class Organismo:
    """
    Classe-base para elementos posicionados no ecossistema.

    Atualmente existem dois tipos:

    - Bacteria;
    - Carcaca.
    """

    def __init__(
        self,
        x: float,
        y: float,
        energia: float,
        tamanho: int,
        cor: tuple[int, int, int],
    ) -> None:
        self.x = self.limitar_x(x)
        self.y = self.limitar_y(y)

        self.energia = float(
            energia
        )

        self.tamanho = max(
            1,
            int(tamanho),
        )

        self.cor = cor

        self.direcao = random.uniform(
            0.0,
            2.0 * math.pi,
        )

    def desenhar(
        self,
        tela: pygame.Surface,
    ) -> None:
        """
        Desenha o organismo como um círculo simples.

        Bacteria e Carcaca sobrescrevem este método.
        """

        pygame.draw.circle(
            tela,
            self.cor,
            (
                int(self.x),
                int(self.y),
            ),
            self.tamanho,
        )

    def distancia_quadrada_para(
        self,
        outro: Any,
    ) -> float:
        """
        Calcula a distância quadrática até outro objeto.
        """

        dx = float(outro.x) - self.x
        dy = float(outro.y) - self.y

        return (
            dx * dx
            + dy * dy
        )

    def distancia_para(
        self,
        outro: Any,
    ) -> float:
        """
        Calcula a distância real até outro objeto.
        """

        return math.sqrt(
            self.distancia_quadrada_para(
                outro
            )
        )

    def esta_em_contato(
        self,
        outro: Any,
        margem: float = 0.0,
    ) -> bool:
        """
        Verifica se este organismo está tocando outro.
        """

        tamanho_outro = float(
            getattr(
                outro,
                "tamanho",
                0.0,
            )
        )

        raio_total = (
            self.tamanho
            + tamanho_outro
            + margem
        )

        return (
            self.distancia_quadrada_para(
                outro
            )
            <= raio_total * raio_total
        )

    def apontar_para(
        self,
        x: float,
        y: float,
    ) -> None:
        """
        Aponta a direção do organismo para uma coordenada.
        """

        self.direcao = math.atan2(
            y - self.y,
            x - self.x,
        )

    def manter_dentro_dos_limites(
        self,
    ) -> None:
        """
        Mantém o organismo dentro da área válida.
        """

        if self.x <= 0.0:
            self.x = 0.0

            self.direcao = random.uniform(
                -math.pi / 2.0,
                math.pi / 2.0,
            )

        elif self.x >= AREA_SIMULACAO_LARGURA - 1:
            self.x = float(
                AREA_SIMULACAO_LARGURA - 1
            )

            self.direcao = random.uniform(
                math.pi / 2.0,
                3.0 * math.pi / 2.0,
            )

        if self.y <= 0.0:
            self.y = 0.0

            self.direcao = random.uniform(
                0.0,
                math.pi,
            )

        elif self.y >= ALTURA - 1:
            self.y = float(
                ALTURA - 1
            )

            self.direcao = random.uniform(
                math.pi,
                2.0 * math.pi,
            )

    @staticmethod
    def limitar_x(
        x: float,
    ) -> float:
        return limitar(
            float(x),
            0.0,
            float(
                AREA_SIMULACAO_LARGURA - 1
            ),
        )

    @staticmethod
    def limitar_y(
        y: float,
    ) -> float:
        return limitar(
            float(y),
            0.0,
            float(
                ALTURA - 1
            ),
        )


# ============================================================
# CARCAÇA
# ============================================================

class Carcaca(Organismo):
    """
    Representa matéria orgânica deixada pela morte de uma bactéria.

    Carcaças:

    - não são organismos vivos;
    - podem ser consumidas por bactérias necrófagas;
    - degradam-se naturalmente;
    - podem devolver nutrientes ao ambiente.
    """

    def __init__(
        self,
        x: float,
        y: float,
        energia: float = ENERGIA_INICIAL_CARCACA,
        *,
        origem_especie: str | None = None,
        origem_estrategia: str | None = None,
    ) -> None:
        energia = max(
            0.0,
            float(energia),
        )

        super().__init__(
            x=x,
            y=y,
            energia=energia,
            tamanho=TAMANHO_CARCACA,
            cor=COR_CARCACA,
        )

        self.energia_inicial = max(
            energia,
            ENERGIA_MINIMA_CARCACA,
        )

        self.origem_especie = (
            origem_especie
        )

        self.origem_estrategia = (
            origem_estrategia
        )

        self.idade = 0

    def degradar(
        self,
        taxa: float = DEGRADACAO_CARCACA_PADRAO,
    ) -> float:
        """
        Reduz a energia da carcaça.

        Retorna a energia degradada no passo. O Mundo pode usar esse
        valor para devolver nutrientes ao ambiente.
        """

        taxa = max(
            0.0,
            float(taxa),
        )

        energia_antes = self.energia

        self.energia = max(
            0.0,
            self.energia - taxa,
        )

        self.idade += 1

        return (
            energia_antes
            - self.energia
        )

    def consumir(
        self,
        quantidade_maxima: float,
    ) -> float:
        """
        Remove energia da carcaça e retorna o valor consumido.
        """

        quantidade_maxima = max(
            0.0,
            float(quantidade_maxima),
        )

        quantidade_consumida = min(
            self.energia,
            quantidade_maxima,
        )

        self.energia -= (
            quantidade_consumida
        )

        return quantidade_consumida

    def esta_disponivel(
        self,
    ) -> bool:
        """
        Informa se a carcaça ainda possui energia consumível.
        """

        return (
            self.energia
            >= ENERGIA_MINIMA_CARCACA
        )

    def desenhar(
        self,
        tela: pygame.Surface,
    ) -> None:
        """
        Desenha uma carcaça que diminui conforme perde energia.
        """

        proporcao = limitar(
            self.energia
            / max(
                self.energia_inicial,
                0.001,
            ),
            0.0,
            1.0,
        )

        raio = max(
            1,
            int(
                self.tamanho
                * (
                    0.45
                    + proporcao * 0.55
                )
            ),
        )

        centro = (
            int(self.x),
            int(self.y),
        )

        pygame.draw.circle(
            tela,
            (
                70,
                45,
                28,
            ),
            centro,
            raio + 1,
        )

        pygame.draw.circle(
            tela,
            self.cor,
            centro,
            raio,
        )

        if raio >= 3:
            pygame.draw.circle(
                tela,
                (
                    205,
                    145,
                    80,
                ),
                (
                    centro[0] - 1,
                    centro[1] - 1,
                ),
                1,
            )


# ============================================================
# BACTÉRIA
# ============================================================

class Bacteria(Organismo):
    """
    Representa uma bactéria evolutiva.

    Todas as entidades vivas da simulação são bactérias. A diferença
    ecológica entre elas está na estratégia alimentar:

    - fotossíntese;
    - predação;
    - necrofagia.

    A cor principal representa a espécie. Um marcador interno indica
    a estratégia alimentar.
    """

    def __init__(
        self,
        x: float,
        y: float,
        estrategia_alimentar: str = ESTRATEGIA_FOTOSSINTESE,
        genes: dict[str, Any] | None = None,
        *,
        especie_alvo: str | None = None,
        geracao: int = 0,
    ) -> None:
        if (
            estrategia_alimentar
            not in ESTRATEGIAS_ALIMENTARES
        ):
            raise ValueError(
                "Estratégia alimentar inválida: "
                f"{estrategia_alimentar!r}."
            )

        self.idade = 0
        self.geracao = max(
            0,
            int(geracao),
        )

        self.tempo_recuperacao_ataque = 0

        self.alvo_atual: Any | None = None

        if genes is None:
            self.genes = (
                self.gerar_genes_iniciais(
                    estrategia_alimentar
                )
            )

        else:
            self.genes = genes.copy()

            self.genes.setdefault(
                "estrategia_alimentar",
                estrategia_alimentar,
            )

        if especie_alvo is not None:
            self.genes[
                "especie_alvo"
            ] = especie_alvo

        self.completar_genes_ausentes()
        self.aplicar_genes()

        cor = obter_cor_especie(
            self.especie
        )

        super().__init__(
            x=x,
            y=y,
            energia=ENERGIA_INICIAL_BACTERIA,
            tamanho=self.tamanho,
            cor=cor,
        )

        # Organismo.__init__ redefine alguns atributos.
        self.aplicar_genes()

        self.cor = obter_cor_especie(
            self.especie
        )

    # ========================================================
    # CRIAÇÃO E GENOMA
    # ========================================================

    @staticmethod
    def gerar_genes_iniciais(
        estrategia_alimentar: str,
    ) -> dict[str, Any]:
        """
        Gera o genoma inicial de uma bactéria.
        """

        if (
            estrategia_alimentar
            == ESTRATEGIA_FOTOSSINTESE
        ):
            velocidade = random.uniform(
                MOVIMENTO_FOTOSSINTETICA_MINIMO,
                MOVIMENTO_FOTOSSINTETICA_MAXIMO,
            )

            ataque = random.uniform(
                ATAQUE_INICIAL_MINIMO,
                min(
                    ATAQUE_INICIAL_MAXIMO,
                    0.45,
                ),
            )

            inteligencia = (
                random.random() < 0.08
            )

        elif (
            estrategia_alimentar
            == ESTRATEGIA_PREDACAO
        ):
            velocidade = random.uniform(
                max(
                    VELOCIDADE_INICIAL_MINIMA,
                    0.85,
                ),
                min(
                    VELOCIDADE_MAXIMA,
                    VELOCIDADE_INICIAL_MAXIMA
                    + 0.50,
                ),
            )

            ataque = random.uniform(
                max(
                    ATAQUE_INICIAL_MINIMO,
                    0.55,
                ),
                min(
                    ATAQUE_MAXIMO,
                    ATAQUE_INICIAL_MAXIMO
                    + 0.60,
                ),
            )

            inteligencia = (
                random.random() < 0.30
            )

        else:
            velocidade = random.uniform(
                max(
                    VELOCIDADE_INICIAL_MINIMA,
                    0.55,
                ),
                min(
                    VELOCIDADE_MAXIMA,
                    VELOCIDADE_INICIAL_MAXIMA
                    + 0.15,
                ),
            )

            ataque = random.uniform(
                ATAQUE_INICIAL_MINIMO,
                ATAQUE_INICIAL_MAXIMO,
            )

            inteligencia = (
                random.random() < 0.18
            )

        prefixo = obter_prefixo_estrategia(
            estrategia_alimentar
        )

        especie = f"{prefixo}_base"

        return {
            "velocidade": velocidade,
            "tamanho": random.randint(
                TAMANHO_INICIAL_MINIMO,
                TAMANHO_INICIAL_MAXIMO,
            ),
            "inteligencia": inteligencia,
            "especie": especie,
            "esperanca_vida": random.randint(
                ESPERANCA_VIDA_INICIAL_MINIMA,
                ESPERANCA_VIDA_INICIAL_MAXIMA,
            ),
            "defesa": random.uniform(
                DEFESA_INICIAL_MINIMA,
                DEFESA_INICIAL_MAXIMA,
            ),
            "ataque": ataque,
            "eficiencia_metabolica": random.uniform(
                EFICIENCIA_METABOLICA_INICIAL_MINIMA,
                EFICIENCIA_METABOLICA_INICIAL_MAXIMA,
            ),
            "eficiencia_fotossintese": random.uniform(
                EFICIENCIA_FOTOSSINTESE_INICIAL_MINIMA,
                EFICIENCIA_FOTOSSINTESE_INICIAL_MAXIMA,
            ),
            "raio_deteccao": random.uniform(
                RAIO_DETECCAO_INICIAL_MINIMO,
                RAIO_DETECCAO_INICIAL_MAXIMO,
            ),
            "taxa_mutacao": random.uniform(
                TAXA_MUTACAO_INICIAL_MINIMA,
                TAXA_MUTACAO_INICIAL_MAXIMA,
            ),
            "estrategia_alimentar": estrategia_alimentar,
            "especie_alvo": None,
            "distancia_acumulada_especie": 0.0,
        }

    def completar_genes_ausentes(
        self,
    ) -> None:
        """
        Adiciona genes ausentes para manter compatibilidade com genomas
        de versões anteriores.
        """

        estrategia = str(
            self.genes.get(
                "estrategia_alimentar",
                ESTRATEGIA_FOTOSSINTESE,
            )
        )

        if estrategia not in ESTRATEGIAS_ALIMENTARES:
            estrategia = (
                ESTRATEGIA_FOTOSSINTESE
            )

        valores_padrao = (
            self.gerar_genes_iniciais(
                estrategia
            )
        )

        for gene, valor in valores_padrao.items():
            self.genes.setdefault(
                gene,
                valor,
            )

    def aplicar_genes(
        self,
    ) -> None:
        """
        Aplica os valores do genoma aos atributos da bactéria.
        """

        estrategia = str(
            self.genes[
                "estrategia_alimentar"
            ]
        )

        if estrategia not in ESTRATEGIAS_ALIMENTARES:
            estrategia = (
                ESTRATEGIA_FOTOSSINTESE
            )

        self.estrategia_alimentar = estrategia

        self.velocidade = limitar(
            float(
                self.genes[
                    "velocidade"
                ]
            ),
            VELOCIDADE_MINIMA,
            VELOCIDADE_MAXIMA,
        )

        self.tamanho = int(
            limitar(
                float(
                    self.genes[
                        "tamanho"
                    ]
                ),
                float(
                    TAMANHO_MINIMO_BACTERIA
                ),
                float(
                    TAMANHO_MAXIMO_BACTERIA
                ),
            )
        )

        self.inteligencia = bool(
            self.genes[
                "inteligencia"
            ]
        )

        self.especie = str(
            self.genes[
                "especie"
            ]
        )

        self.esperanca_vida = max(
            ESPERANCA_VIDA_MINIMA,
            int(
                self.genes[
                    "esperanca_vida"
                ]
            ),
        )

        self.defesa = limitar(
            float(
                self.genes[
                    "defesa"
                ]
            ),
            DEFESA_MINIMA,
            DEFESA_MAXIMA,
        )

        self.ataque = limitar(
            float(
                self.genes[
                    "ataque"
                ]
            ),
            ATAQUE_MINIMO,
            ATAQUE_MAXIMO,
        )

        self.eficiencia_metabolica = limitar(
            float(
                self.genes[
                    "eficiencia_metabolica"
                ]
            ),
            EFICIENCIA_METABOLICA_MINIMA,
            EFICIENCIA_METABOLICA_MAXIMA,
        )

        self.eficiencia_fotossintese = limitar(
            float(
                self.genes[
                    "eficiencia_fotossintese"
                ]
            ),
            EFICIENCIA_FOTOSSINTESE_MINIMA,
            EFICIENCIA_FOTOSSINTESE_MAXIMA,
        )

        self.raio_deteccao = limitar(
            float(
                self.genes[
                    "raio_deteccao"
                ]
            ),
            RAIO_DETECCAO_MINIMO,
            RAIO_DETECCAO_MAXIMO,
        )

        self.taxa_mutacao = limitar(
            float(
                self.genes[
                    "taxa_mutacao"
                ]
            ),
            TAXA_MUTACAO_MINIMA,
            TAXA_MUTACAO_MAXIMA,
        )

        especie_alvo = self.genes.get(
            "especie_alvo"
        )

        if especie_alvo in (
            "",
            "None",
        ):
            especie_alvo = None

        self.especie_alvo = especie_alvo

        self.distancia_acumulada_especie = max(
            0.0,
            float(
                self.genes.get(
                    "distancia_acumulada_especie",
                    0.0,
                )
            ),
        )

        self.sincronizar_genes()

    def sincronizar_genes(
        self,
    ) -> None:
        """
        Mantém o dicionário de genes sincronizado com os atributos.
        """

        self.genes[
            "velocidade"
        ] = self.velocidade

        self.genes[
            "tamanho"
        ] = self.tamanho

        self.genes[
            "inteligencia"
        ] = self.inteligencia

        self.genes[
            "especie"
        ] = self.especie

        self.genes[
            "esperanca_vida"
        ] = self.esperanca_vida

        self.genes[
            "defesa"
        ] = self.defesa

        self.genes[
            "ataque"
        ] = self.ataque

        self.genes[
            "eficiencia_metabolica"
        ] = self.eficiencia_metabolica

        self.genes[
            "eficiencia_fotossintese"
        ] = self.eficiencia_fotossintese

        self.genes[
            "raio_deteccao"
        ] = self.raio_deteccao

        self.genes[
            "taxa_mutacao"
        ] = self.taxa_mutacao

        self.genes[
            "estrategia_alimentar"
        ] = self.estrategia_alimentar

        self.genes[
            "especie_alvo"
        ] = self.especie_alvo

        self.genes[
            "distancia_acumulada_especie"
        ] = self.distancia_acumulada_especie

    # ========================================================
    # ESTADO GERAL
    # ========================================================

    def esta_viva(
        self,
    ) -> bool:
        """
        Informa se a bactéria ainda está viva.
        """

        return (
            self.energia > 0.0
            and self.idade
            < self.esperanca_vida
        )

    def receber_energia(
        self,
        quantidade: float,
    ) -> float:
        """
        Adiciona energia respeitando o limite máximo.

        Retorna a energia efetivamente recebida.
        """

        quantidade = max(
            0.0,
            float(quantidade),
        )

        energia_antes = self.energia

        self.energia = limitar(
            self.energia + quantidade,
            0.0,
            ENERGIA_MAXIMA_BACTERIA,
        )

        return (
            self.energia
            - energia_antes
        )

    def perder_energia(
        self,
        quantidade: float,
    ) -> float:
        """
        Remove energia e retorna a quantidade efetivamente perdida.
        """

        quantidade = max(
            0.0,
            float(quantidade),
        )

        energia_antes = self.energia

        self.energia = max(
            0.0,
            self.energia - quantidade,
        )

        return (
            energia_antes
            - self.energia
        )

    # ========================================================
    # MOVIMENTO
    # ========================================================

    def mover(
        self,
        quadtree: Any | None = None,
        ambiente: Any | None = None,
    ) -> None:
        """
        Atualiza movimento, energia, idade e recuperação de ataque.

        O Mundo pode apontar previamente a bactéria para uma presa ou
        carcaça. Bactérias fotossintéticas também podem procurar regiões
        ambientalmente mais favoráveis.
        """

        if not self.esta_viva():
            self.energia = 0.0
            return

        fator_atividade = 1.0

        if ambiente is not None:
            metodo_fator = getattr(
                ambiente,
                "fator_metabolico",
                None,
            )

            if callable(metodo_fator):
                fator_atividade = limitar(
                    float(
                        metodo_fator()
                    ),
                    0.20,
                    1.0,
                )

        if (
            self.estrategia_alimentar
            == ESTRATEGIA_FOTOSSINTESE
            and ambiente is not None
        ):
            self.aplicar_quimiotaxia_ambiental(
                ambiente
            )

        self.aplicar_movimento_browniano()

        deslocamento = (
            self.velocidade
            * fator_atividade
        )

        self.x += (
            math.cos(
                self.direcao
            )
            * deslocamento
        )

        self.y += (
            math.sin(
                self.direcao
            )
            * deslocamento
        )

        self.manter_dentro_dos_limites()

        if quadtree is not None:
            self.aplicar_repulsao(
                quadtree
            )

        custo_movimento = (
            CUSTO_MOVIMENTO_BACTERIA
            * deslocamento
            * max(
                self.tamanho / 5.0,
                0.5,
            )
        )

        custo_metabolico = (
            CUSTO_METABOLICO_BACTERIA
            / max(
                self.eficiencia_metabolica,
                0.01,
            )
        )

        if ambiente is not None:
            metodo_custo = getattr(
                ambiente,
                "custo_metabolico",
                None,
            )

            if callable(metodo_custo):
                custo_metabolico += max(
                    0.0,
                    float(
                        metodo_custo()
                    ),
                )

        self.perder_energia(
            custo_movimento
            + custo_metabolico
        )

        self.idade += 1

        if self.tempo_recuperacao_ataque > 0:
            self.tempo_recuperacao_ataque -= 1

        if self.idade >= self.esperanca_vida:
            self.energia = 0.0

    def aplicar_movimento_browniano(
        self,
    ) -> None:
        """
        Aplica uma pequena alteração aleatória na direção.
        """

        intensidade = (
            RUIDO_BROWNIANO_INTELIGENTE
            if self.inteligencia
            else RUIDO_BROWNIANO_PADRAO
        )

        self.direcao += random.uniform(
            -intensidade,
            intensidade,
        )

        self.direcao %= (
            2.0 * math.pi
        )

    def aplicar_quimiotaxia_ambiental(
        self,
        ambiente: Any,
    ) -> None:
        """
        Orienta levemente a bactéria fotossintética para regiões com
        melhor potencial de fotossíntese.
        """

        metodo_fator = getattr(
            ambiente,
            "fator_fotossintese",
            None,
        )

        if not callable(metodo_fator):
            return

        distancia = (
            DISTANCIA_AMOSTRA_QUIMIOTAXIA
        )

        direcoes = (
            self.direcao,
            self.direcao - math.pi / 3.0,
            self.direcao + math.pi / 3.0,
        )

        melhor_direcao = self.direcao
        melhor_fator = -1.0

        for direcao in direcoes:
            amostra_x = self.limitar_x(
                self.x
                + math.cos(direcao)
                * distancia
            )

            amostra_y = self.limitar_y(
                self.y
                + math.sin(direcao)
                * distancia
            )

            fator = float(
                metodo_fator(
                    amostra_x,
                    amostra_y,
                )
            )

            if fator > melhor_fator:
                melhor_fator = fator
                melhor_direcao = direcao

        intensidade = (
            INTENSIDADE_QUIMIOTAXIA_INTELIGENTE
            if self.inteligencia
            else INTENSIDADE_QUIMIOTAXIA_PADRAO
        )

        diferenca = self.normalizar_angulo(
            melhor_direcao
            - self.direcao
        )

        self.direcao += (
            diferenca
            * intensidade
        )

        self.direcao %= (
            2.0 * math.pi
        )

    def aplicar_repulsao(
        self,
        quadtree: Any,
    ) -> None:
        """
        Evita que muitas bactérias ocupem exatamente o mesmo ponto.
        """

        raio_busca = max(
            float(
                self.tamanho * 3
            ),
            10.0,
        )

        candidatos: list[Any]

        metodo_query_circle = getattr(
            quadtree,
            "query_circle",
            None,
        )

        if callable(
            metodo_query_circle
        ):
            candidatos = metodo_query_circle(
                self.x,
                self.y,
                raio_busca,
            )

        else:
            metodo_query = getattr(
                quadtree,
                "query",
                None,
            )

            if not callable(
                metodo_query
            ):
                return

            candidatos = metodo_query(
                (
                    self.x - raio_busca,
                    self.y - raio_busca,
                    raio_busca * 2.0,
                    raio_busca * 2.0,
                )
            )

        repulsao_x = 0.0
        repulsao_y = 0.0
        quantidade = 0

        for outro in candidatos:
            if (
                outro is self
                or not isinstance(
                    outro,
                    Bacteria,
                )
            ):
                continue

            dx = self.x - outro.x
            dy = self.y - outro.y

            distancia_quadrada = (
                dx * dx
                + dy * dy
            )

            if distancia_quadrada <= 0.0001:
                angulo = random.uniform(
                    0.0,
                    2.0 * math.pi,
                )

                dx = math.cos(
                    angulo
                )

                dy = math.sin(
                    angulo
                )

                distancia_quadrada = 1.0

            distancia = math.sqrt(
                distancia_quadrada
            )

            limite = (
                self.tamanho
                + outro.tamanho
                + 3.0
            )

            if distancia > limite:
                continue

            intensidade = (
                1.0
                - distancia
                / max(
                    limite,
                    0.001,
                )
            )

            repulsao_x += (
                dx
                / distancia
                * intensidade
            )

            repulsao_y += (
                dy
                / distancia
                * intensidade
            )

            quantidade += 1

        if quantidade <= 0:
            return

        self.x += (
            repulsao_x
            / quantidade
            * FATOR_REPULSAO
        )

        self.y += (
            repulsao_y
            / quantidade
            * FATOR_REPULSAO
        )

        self.manter_dentro_dos_limites()

    @staticmethod
    def normalizar_angulo(
        angulo: float,
    ) -> float:
        """
        Normaliza um ângulo para o intervalo de -π a π.
        """

        return (
            angulo + math.pi
        ) % (
            2.0 * math.pi
        ) - math.pi

    # ========================================================
    # FOTOSSÍNTESE
    # ========================================================

    def realizar_fotossintese(
        self,
        ambiente: Any,
    ) -> float:
        """
        Converte luz e condições ambientais em energia.

        Retorna a energia efetivamente recebida.
        """

        if (
            self.estrategia_alimentar
            != ESTRATEGIA_FOTOSSINTESE
        ):
            return 0.0

        metodo_luz = getattr(
            ambiente,
            "intensidade_luz",
            None,
        )

        intensidade_luz = 1.0

        if callable(metodo_luz):
            intensidade_luz = limitar(
                float(
                    metodo_luz()
                ),
                0.0,
                1.0,
            )

        if (
            intensidade_luz
            < INTENSIDADE_MINIMA_FOTOSSINTESE
        ):
            self.perder_energia(
                CUSTO_NOTURNO_FOTOSSINTETICA
            )

            return 0.0

        metodo_fator = getattr(
            ambiente,
            "fator_fotossintese",
            None,
        )

        if callable(metodo_fator):
            fator = max(
                0.0,
                float(
                    metodo_fator(
                        self.x,
                        self.y,
                    )
                ),
            )

        else:
            fator = intensidade_luz

        ganho_bruto = (
            GANHO_BASE_FOTOSSINTESE
            * self.eficiencia_fotossintese
            * fator
        )

        return self.receber_energia(
            ganho_bruto
        )

    # ========================================================
    # NECROFAGIA
    # ========================================================

    def consumir_carcaca(
        self,
        carcaca: Carcaca,
    ) -> float:
        """
        Consome parte de uma carcaça.

        Retorna a energia efetivamente recebida pela bactéria.
        """

        if (
            self.estrategia_alimentar
            != ESTRATEGIA_NECROFAGIA
        ):
            return 0.0

        if not carcaca.esta_disponivel():
            return 0.0

        if not self.esta_em_contato(
            carcaca,
            margem=2.0,
        ):
            return 0.0

        materia_consumida = carcaca.consumir(
            CONSUMO_MAXIMO_CARCACA_POR_FRAME
        )

        energia_convertida = (
            materia_consumida
            * EFICIENCIA_CONSUMO_CARCACA
        )

        return self.receber_energia(
            energia_convertida
        )

    # ========================================================
    # PREDAÇÃO
    # ========================================================

    def pode_atacar(
        self,
        alvo: Bacteria,
    ) -> bool:
        """
        Verifica se uma bactéria pode tentar atacar outra.
        """

        if (
            self.estrategia_alimentar
            != ESTRATEGIA_PREDACAO
        ):
            return False

        if self.tempo_recuperacao_ataque > 0:
            return False

        if alvo is self:
            return False

        if not alvo.esta_viva():
            return False

        if (
            not PREDADOR_PODE_ATACAR_MESMA_ESPECIE
            and alvo.especie
            == self.especie
        ):
            return False

        if (
            self.especie_alvo is not None
            and alvo.especie
            != self.especie_alvo
        ):
            return False

        return True

    def calcular_chance_predacao(
        self,
        alvo: Bacteria,
    ) -> float:
        """
        Calcula a chance de sucesso do ataque.
        """

        denominador = (
            self.ataque
            + alvo.defesa
        )

        if denominador <= 0.0:
            return 0.0

        chance_base = (
            self.ataque
            / denominador
        )

        proporcao_tamanho = (
            self.tamanho
            / max(
                alvo.tamanho,
                1,
            )
        )

        fator_tamanho = limitar(
            0.75
            + proporcao_tamanho
            * 0.25,
            0.60,
            1.35,
        )

        proporcao_energia = (
            self.energia
            / max(
                alvo.energia,
                1.0,
            )
        )

        fator_energia = limitar(
            0.80
            + proporcao_energia
            * 0.20,
            0.70,
            1.25,
        )

        return limitar(
            chance_base
            * fator_tamanho
            * fator_energia,
            0.02,
            0.98,
        )

    def tentar_predar(
        self,
        alvo: Bacteria,
    ) -> bool:
        """
        Tenta matar outra bactéria.

        Em caso de sucesso, a energia do alvo é zerada. O Mundo deve
        remover a bactéria morta e criar sua carcaça.
        """

        if not self.pode_atacar(
            alvo
        ):
            return False

        if not self.esta_em_contato(
            alvo,
            margem=2.0,
        ):
            return False

        chance_sucesso = (
            self.calcular_chance_predacao(
                alvo
            )
        )

        self.tempo_recuperacao_ataque = (
            TEMPO_RECUPERACAO_ATAQUE
        )

        if (
            random.random()
            >= chance_sucesso
        ):
            self.perder_energia(
                PENALIDADE_FALHA_PREDACAO
            )

            return False

        alvo.energia = 0.0

        self.receber_energia(
            ENERGIA_PREDACAO_BACTERIA
        )

        return True

    # ========================================================
    # ALIMENTAÇÃO E BUSCA
    # ========================================================

    def obter_raio_busca_alimento(
        self,
    ) -> float:
        """
        Retorna o raio de busca apropriado para a estratégia.
        """

        if (
            self.estrategia_alimentar
            == ESTRATEGIA_PREDACAO
        ):
            return min(
                self.raio_deteccao,
                RAIO_CACA_PADRAO,
            )

        if (
            self.estrategia_alimentar
            == ESTRATEGIA_NECROFAGIA
        ):
            return min(
                self.raio_deteccao,
                RAIO_BUSCA_CARCACA_PADRAO,
            )

        return self.raio_deteccao

    def aplicar_penalidade_sem_alimento(
        self,
    ) -> None:
        """
        Aplica uma pequena perda quando a bactéria não encontra recurso.
        """

        if (
            self.estrategia_alimentar
            == ESTRATEGIA_FOTOSSINTESE
        ):
            return

        self.perder_energia(
            PENALIDADE_SEM_ALIMENTO
        )

    # ========================================================
    # REPRODUÇÃO ASSEXUADA
    # ========================================================

    def pode_reproduzir(
        self,
    ) -> bool:
        """
        Verifica se a bactéria possui condições para divisão.
        """

        return (
            self.esta_viva()
            and self.energia
            >= ENERGIA_REPRODUCAO_BACTERIA
        )

    def reproduzir(
        self,
    ) -> Bacteria | None:
        """
        Realiza divisão assexuada.

        O descendente recebe uma cópia do genoma, que pode sofrer
        mutações. O método não adiciona o filho diretamente ao Mundo.
        """

        if not self.pode_reproduzir():
            return None

        if (
            random.random()
            > PROBABILIDADE_REPRODUCAO_POR_FRAME
        ):
            return None

        energia_total = self.energia

        fracao_filho = limitar(
            min(
                CUSTO_REPRODUCAO_BACTERIA,
                DIVISAO_ENERGIA_REPRODUCAO,
            ),
            0.10,
            0.90,
        )

        energia_filho = (
            energia_total
            * fracao_filho
        )

        energia_restante = (
            energia_total
            - energia_filho
        )

        self.energia = max(
            0.0,
            energia_restante,
        )

        angulo = random.uniform(
            0.0,
            2.0 * math.pi,
        )

        distancia = random.uniform(
            2.0,
            DISTANCIA_MAXIMA_DESCENDENTE,
        )

        novo_x = self.limitar_x(
            self.x
            + math.cos(angulo)
            * distancia
        )

        novo_y = self.limitar_y(
            self.y
            + math.sin(angulo)
            * distancia
        )

        genes_filho = self.genes.copy()

        filho = Bacteria(
            x=novo_x,
            y=novo_y,
            estrategia_alimentar=(
                self.estrategia_alimentar
            ),
            genes=genes_filho,
            especie_alvo=self.especie_alvo,
            geracao=self.geracao + 1,
        )

        filho.energia = limitar(
            energia_filho,
            0.0,
            ENERGIA_MAXIMA_BACTERIA,
        )

        filho.mutar()

        return filho

    # ========================================================
    # MUTAÇÕES
    # ========================================================

    def mutar(
        self,
    ) -> None:
        """
        Aplica mutações ao genoma.

        Alterações acumuladas suficientemente grandes criam uma nova
        espécie. A estratégia alimentar pode mudar, mas isso é raro.
        """

        genes_antes = self.genes.copy()

        taxa = self.taxa_mutacao

        if random.random() < taxa:
            self.genes[
                "velocidade"
            ] = limitar(
                float(
                    self.genes[
                        "velocidade"
                    ]
                )
                + random.gauss(
                    0.0,
                    MUTACAO_VELOCIDADE_DESVIO,
                ),
                VELOCIDADE_MINIMA,
                VELOCIDADE_MAXIMA,
            )

        if random.random() < taxa:
            variacao_tamanho = random.randint(
                -MUTACAO_TAMANHO_MAXIMA,
                MUTACAO_TAMANHO_MAXIMA,
            )

            self.genes[
                "tamanho"
            ] = int(
                limitar(
                    float(
                        self.genes[
                            "tamanho"
                        ]
                    )
                    + variacao_tamanho,
                    float(
                        TAMANHO_MINIMO_BACTERIA
                    ),
                    float(
                        TAMANHO_MAXIMO_BACTERIA
                    ),
                )
            )

        if random.random() < taxa:
            self.genes[
                "esperanca_vida"
            ] = max(
                ESPERANCA_VIDA_MINIMA,
                int(
                    self.genes[
                        "esperanca_vida"
                    ]
                )
                + random.randint(
                    -MUTACAO_ESPERANCA_VIDA_MAXIMA,
                    MUTACAO_ESPERANCA_VIDA_MAXIMA,
                ),
            )

        if random.random() < taxa:
            self.genes[
                "defesa"
            ] = limitar(
                float(
                    self.genes[
                        "defesa"
                    ]
                )
                + random.gauss(
                    0.0,
                    MUTACAO_DEFESA_DESVIO,
                ),
                DEFESA_MINIMA,
                DEFESA_MAXIMA,
            )

        if random.random() < taxa:
            self.genes[
                "ataque"
            ] = limitar(
                float(
                    self.genes[
                        "ataque"
                    ]
                )
                + random.gauss(
                    0.0,
                    MUTACAO_ATAQUE_DESVIO,
                ),
                ATAQUE_MINIMO,
                ATAQUE_MAXIMO,
            )

        if random.random() < taxa:
            self.genes[
                "eficiencia_metabolica"
            ] = limitar(
                float(
                    self.genes[
                        "eficiencia_metabolica"
                    ]
                )
                + random.gauss(
                    0.0,
                    MUTACAO_EFICIENCIA_METABOLICA_DESVIO,
                ),
                EFICIENCIA_METABOLICA_MINIMA,
                EFICIENCIA_METABOLICA_MAXIMA,
            )

        if random.random() < taxa:
            self.genes[
                "eficiencia_fotossintese"
            ] = limitar(
                float(
                    self.genes[
                        "eficiencia_fotossintese"
                    ]
                )
                + random.gauss(
                    0.0,
                    MUTACAO_EFICIENCIA_FOTOSSINTESE_DESVIO,
                ),
                EFICIENCIA_FOTOSSINTESE_MINIMA,
                EFICIENCIA_FOTOSSINTESE_MAXIMA,
            )

        if random.random() < taxa:
            self.genes[
                "raio_deteccao"
            ] = limitar(
                float(
                    self.genes[
                        "raio_deteccao"
                    ]
                )
                + random.gauss(
                    0.0,
                    MUTACAO_RAIO_DETECCAO_DESVIO,
                ),
                RAIO_DETECCAO_MINIMO,
                RAIO_DETECCAO_MAXIMO,
            )

        if random.random() < taxa:
            self.genes[
                "taxa_mutacao"
            ] = limitar(
                float(
                    self.genes[
                        "taxa_mutacao"
                    ]
                )
                + random.gauss(
                    0.0,
                    MUTACAO_TAXA_MUTACAO_DESVIO,
                ),
                TAXA_MUTACAO_MINIMA,
                TAXA_MUTACAO_MAXIMA,
            )

        if (
            random.random()
            < taxa * 0.10
        ):
            self.genes[
                "inteligencia"
            ] = not bool(
                self.genes[
                    "inteligencia"
                ]
            )

        estrategia_mutou = False

        if (
            random.random()
            < PROBABILIDADE_MUTACAO_ESTRATEGIA
        ):
            estrategias_possiveis = [
                estrategia
                for estrategia
                in ESTRATEGIAS_ALIMENTARES
                if estrategia
                != self.genes[
                    "estrategia_alimentar"
                ]
            ]

            self.genes[
                "estrategia_alimentar"
            ] = random.choice(
                estrategias_possiveis
            )

            self.genes[
                "especie_alvo"
            ] = None

            estrategia_mutou = True

        if (
            self.genes[
                "estrategia_alimentar"
            ]
            == ESTRATEGIA_PREDACAO
            and random.random()
            < PROBABILIDADE_MUTACAO_ESPECIE_ALVO
        ):
            # None significa que a bactéria pode atacar qualquer espécie
            # permitida pelas regras do Mundo.
            self.genes[
                "especie_alvo"
            ] = None

        distancia_mutacao = (
            self.calcular_distancia_genetica(
                genes_antes,
                self.genes,
            )
        )

        if estrategia_mutou:
            distancia_mutacao += 1.0

        distancia_acumulada = (
            float(
                self.genes.get(
                    "distancia_acumulada_especie",
                    0.0,
                )
            )
            + distancia_mutacao
        )

        if (
            distancia_acumulada
            >= DISTANCIA_GENETICA_NOVA_ESPECIE
        ):
            estrategia = str(
                self.genes[
                    "estrategia_alimentar"
                ]
            )

            prefixo = (
                obter_prefixo_estrategia(
                    estrategia
                )
            )

            self.genes[
                "especie"
            ] = gerar_identificador_especie(
                prefixo
            )

            distancia_acumulada = 0.0

        self.genes[
            "distancia_acumulada_especie"
        ] = distancia_acumulada

        self.aplicar_genes()

        self.cor = obter_cor_especie(
            self.especie
        )

    @staticmethod
    def calcular_distancia_genetica(
        genes_antes: dict[str, Any],
        genes_depois: dict[str, Any],
    ) -> float:
        """
        Calcula uma distância genética normalizada aproximada.
        """

        comparacoes = (
            (
                "velocidade",
                VELOCIDADE_MINIMA,
                VELOCIDADE_MAXIMA,
            ),
            (
                "tamanho",
                TAMANHO_MINIMO_BACTERIA,
                TAMANHO_MAXIMO_BACTERIA,
            ),
            (
                "esperanca_vida",
                ESPERANCA_VIDA_MINIMA,
                ESPERANCA_VIDA_INICIAL_MAXIMA
                * 2,
            ),
            (
                "defesa",
                DEFESA_MINIMA,
                DEFESA_MAXIMA,
            ),
            (
                "ataque",
                ATAQUE_MINIMO,
                ATAQUE_MAXIMO,
            ),
            (
                "eficiencia_metabolica",
                EFICIENCIA_METABOLICA_MINIMA,
                EFICIENCIA_METABOLICA_MAXIMA,
            ),
            (
                "eficiencia_fotossintese",
                EFICIENCIA_FOTOSSINTESE_MINIMA,
                EFICIENCIA_FOTOSSINTESE_MAXIMA,
            ),
            (
                "raio_deteccao",
                RAIO_DETECCAO_MINIMO,
                RAIO_DETECCAO_MAXIMO,
            ),
            (
                "taxa_mutacao",
                TAXA_MUTACAO_MINIMA,
                TAXA_MUTACAO_MAXIMA,
            ),
        )

        distancias: list[float] = []

        for (
            nome_gene,
            minimo,
            maximo,
        ) in comparacoes:
            valor_antes = float(
                genes_antes.get(
                    nome_gene,
                    minimo,
                )
            )

            valor_depois = float(
                genes_depois.get(
                    nome_gene,
                    minimo,
                )
            )

            amplitude = max(
                float(maximo)
                - float(minimo),
                0.0001,
            )

            distancias.append(
                abs(
                    valor_depois
                    - valor_antes
                )
                / amplitude
            )

        if (
            bool(
                genes_antes.get(
                    "inteligencia",
                    False,
                )
            )
            != bool(
                genes_depois.get(
                    "inteligencia",
                    False,
                )
            )
        ):
            distancias.append(
                0.25
            )

        if not distancias:
            return 0.0

        return sum(
            distancias
        )

    # ========================================================
    # REPRESENTAÇÃO VISUAL
    # ========================================================

    def desenhar(
        self,
        tela: pygame.Surface,
    ) -> None:
        """
        Desenha a bactéria como uma cápsula orientada.

        - a cor do corpo representa a espécie;
        - a borda e o marcador central representam a estratégia.
        """

        centro_x = int(
            self.x
        )

        centro_y = int(
            self.y
        )

        raio = max(
            2,
            int(
                self.tamanho
            ),
        )

        comprimento = max(
            raio * 1.6,
            4.0,
        )

        deslocamento_x = (
            math.cos(
                self.direcao
            )
            * comprimento
            / 2.0
        )

        deslocamento_y = (
            math.sin(
                self.direcao
            )
            * comprimento
            / 2.0
        )

        ponto_inicial = (
            int(
                centro_x
                - deslocamento_x
            ),
            int(
                centro_y
                - deslocamento_y
            ),
        )

        ponto_final = (
            int(
                centro_x
                + deslocamento_x
            ),
            int(
                centro_y
                + deslocamento_y
            ),
        )

        cor_estrategia = (
            CORES_ESTRATEGIAS.get(
                self.estrategia_alimentar,
                (
                    230,
                    230,
                    230,
                ),
            )
        )

        largura_borda = (
            raio * 2
            + 3
        )

        largura_corpo = max(
            2,
            raio * 2,
        )

        pygame.draw.line(
            tela,
            cor_estrategia,
            ponto_inicial,
            ponto_final,
            largura_borda,
        )

        pygame.draw.circle(
            tela,
            cor_estrategia,
            ponto_inicial,
            raio + 1,
        )

        pygame.draw.circle(
            tela,
            cor_estrategia,
            ponto_final,
            raio + 1,
        )

        pygame.draw.line(
            tela,
            self.cor,
            ponto_inicial,
            ponto_final,
            largura_corpo,
        )

        pygame.draw.circle(
            tela,
            self.cor,
            ponto_inicial,
            raio,
        )

        pygame.draw.circle(
            tela,
            self.cor,
            ponto_final,
            raio,
        )

        raio_marcador = max(
            2,
            raio // 3,
        )

        pygame.draw.circle(
            tela,
            cor_estrategia,
            (
                centro_x,
                centro_y,
            ),
            raio_marcador,
        )

        proporcao_energia = limitar(
            self.energia
            / max(
                ENERGIA_MAXIMA_BACTERIA,
                1.0,
            ),
            0.0,
            1.0,
        )

        if proporcao_energia >= 0.75:
            pygame.draw.circle(
                tela,
                (
                    255,
                    255,
                    255,
                ),
                (
                    centro_x - 1,
                    centro_y - 1,
                ),
                1,
            )

    # ========================================================
    # DADOS PARA A INTERFACE
    # ========================================================

    def obter_dados_inspecao(
        self,
    ) -> dict[str, Any]:
        """
        Retorna os principais atributos da bactéria.
        """

        return {
            "tipo": "Bactéria",
            "especie": self.especie,
            "estrategia": self.estrategia_alimentar,
            "especie_alvo": self.especie_alvo,
            "energia": self.energia,
            "idade": self.idade,
            "esperanca_vida": self.esperanca_vida,
            "geracao": self.geracao,
            "velocidade": self.velocidade,
            "tamanho": self.tamanho,
            "ataque": self.ataque,
            "defesa": self.defesa,
            "inteligencia": self.inteligencia,
            "eficiencia_metabolica": (
                self.eficiencia_metabolica
            ),
            "eficiencia_fotossintese": (
                self.eficiencia_fotossintese
            ),
            "raio_deteccao": self.raio_deteccao,
            "taxa_mutacao": self.taxa_mutacao,
            "posicao": (
                self.x,
                self.y,
            ),
        }

    def __repr__(
        self,
    ) -> str:
        return (
            "Bacteria("
            f"especie={self.especie!r}, "
            f"estrategia={self.estrategia_alimentar!r}, "
            f"energia={self.energia:.2f}, "
            f"idade={self.idade}, "
            f"geracao={self.geracao}, "
            f"x={self.x:.1f}, "
            f"y={self.y:.1f}"
            ")"
        )
