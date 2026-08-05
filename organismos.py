# organismos.py
from __future__ import annotations

import math
import random
from typing import Any

import pygame

from ambiente import nivel_nutrientes
from configuracoes import (
    ALTURA,
    AREA_SIMULACAO_LARGURA,
)


# Cores registradas por espécie.
# Todas as bactérias pertencentes à mesma espécie usam a mesma cor.
cores_especies: dict[str, tuple[int, int, int]] = {}


class Organismo:
    """
    Classe-base dos organismos e elementos biológicos da simulação.

    Centraliza:

    - posição;
    - energia;
    - tamanho;
    - cor;
    - direção;
    - desenho;
    - limitação espacial.
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

        self.energia = float(energia)
        self.tamanho = int(tamanho)
        self.cor = cor

        self.direcao = random.uniform(
            0.0,
            2.0 * math.pi,
        )

    def desenhar(
        self,
        tela: pygame.Surface,
    ) -> None:
        """Desenha o organismo como um círculo."""

        pygame.draw.circle(
            tela,
            self.cor,
            (
                int(self.x),
                int(self.y),
            ),
            max(1, int(self.tamanho)),
        )

    def distancia_quadrada_para(
        self,
        outro: Any,
    ) -> float:
        """Calcula a distância quadrática até outro objeto."""

        dx = outro.x - self.x
        dy = outro.y - self.y

        return dx * dx + dy * dy

    def distancia_para(
        self,
        outro: Any,
    ) -> float:
        """Calcula a distância real até outro objeto."""

        return math.sqrt(
            self.distancia_quadrada_para(outro)
        )

    def apontar_para(
        self,
        x: float,
        y: float,
    ) -> None:
        """Altera a direção para apontar em direção a uma coordenada."""

        self.direcao = math.atan2(
            y - self.y,
            x - self.x,
        )

    def manter_dentro_dos_limites(self) -> None:
        """Mantém o organismo dentro da área da simulação."""

        if self.x <= 0:
            self.x = 0
            self.direcao = random.uniform(
                -math.pi / 2,
                math.pi / 2,
            )

        elif self.x >= AREA_SIMULACAO_LARGURA - 1:
            self.x = AREA_SIMULACAO_LARGURA - 1
            self.direcao = random.uniform(
                math.pi / 2,
                3 * math.pi / 2,
            )

        if self.y <= 0:
            self.y = 0
            self.direcao = random.uniform(
                0,
                math.pi,
            )

        elif self.y >= ALTURA - 1:
            self.y = ALTURA - 1
            self.direcao = random.uniform(
                math.pi,
                2 * math.pi,
            )

    @staticmethod
    def limitar_x(
        x: float,
    ) -> float:
        return max(
            0.0,
            min(
                float(x),
                float(AREA_SIMULACAO_LARGURA - 1),
            ),
        )

    @staticmethod
    def limitar_y(
        y: float,
    ) -> float:
        return max(
            0.0,
            min(
                float(y),
                float(ALTURA - 1),
            ),
        )


class Carcaca(Organismo):
    """
    Representa matéria orgânica proveniente da morte de um organismo.

    A redução de energia e a remoção são administradas pelo Mundo.
    """

    def __init__(
        self,
        x: float,
        y: float,
        energia: float = 30.0,
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            energia=energia,
            tamanho=3,
            cor=(139, 69, 19),
        )


class Alga(Organismo):
    """
    Produtor primário da simulação.

    A alga acumula energia por fotossíntese e pode gerar um descendente.
    O descendente é apenas retornado. O Mundo decide se pode adicioná-lo,
    garantindo o respeito ao limite MAX_ALGAS.
    """

    ENERGIA_INICIAL = 100.0
    ENERGIA_REPRODUCAO = 120.0

    GANHO_BASE_FOTOSSINTESE = 2.0
    CUSTO_NOTURNO = 0.1

    DISPERSAO_REPRODUCAO = 8.0

    def __init__(
        self,
        x: float,
        y: float,
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            energia=self.ENERGIA_INICIAL,
            tamanho=3,
            cor=(0, 120, 30),
        )

    def fotossintese(
        self,
        ciclo_luz: str,
    ) -> Alga | None:
        """
        Atualiza a energia da alga.

        Retorna uma nova alga caso ocorra reprodução.
        Não adiciona o descendente diretamente a nenhuma lista.
        """

        if ciclo_luz == "dia":
            nutrientes = nivel_nutrientes(
                self.x,
                self.y,
            )

            ganho_energia = (
                self.GANHO_BASE_FOTOSSINTESE
                * nutrientes
            )

            self.energia += ganho_energia

            if self.energia >= self.ENERGIA_REPRODUCAO:
                return self.reproduzir()

        else:
            self.energia -= self.CUSTO_NOTURNO

        return None

    def reproduzir(
        self,
    ) -> Alga:
        """
        Cria uma nova alga próxima da alga-mãe.

        A energia é dividida entre o indivíduo atual e o descendente.
        """

        energia_disponivel = self.energia
        self.energia = energia_disponivel / 2.0

        novo_x = self.limitar_x(
            self.x
            + random.uniform(
                -self.DISPERSAO_REPRODUCAO,
                self.DISPERSAO_REPRODUCAO,
            )
        )

        novo_y = self.limitar_y(
            self.y
            + random.uniform(
                -self.DISPERSAO_REPRODUCAO,
                self.DISPERSAO_REPRODUCAO,
            )
        )

        filho = Alga(
            novo_x,
            novo_y,
        )

        filho.energia = energia_disponivel / 2.0

        return filho


class Bacteria(Organismo):
    """
    Representa uma bactéria evolutiva.

    Genes suportados:

    - velocidade;
    - tamanho;
    - inteligencia;
    - especie;
    - esperanca_vida;
    - defesa;
    - ataque;
    - eficiencia_metabolica;
    - raio_deteccao;
    - taxa_mutacao.

    A classe não adiciona ou remove indivíduos das listas do Mundo.
    Reprodução, morte e predação são centralizadas em mundo.py.
    """

    ENERGIA_INICIAL = 100.0

    CUSTO_MOVIMENTO_BASE = 0.02
    CUSTO_METABOLICO_BASE = 0.008

    ENERGIA_REPRODUCAO = 200.0

    def __init__(
        self,
        x: float,
        y: float,
        genes: dict[str, Any] | None = None,
        presa: str | None = None,
    ) -> None:
        self.idade = 0

        self.presa = presa or "alga"

        if genes is None:
            self.genes = self.gerar_genes_iniciais()
        else:
            self.genes = genes.copy()
            self.completar_genes_ausentes()

        self.aplicar_genes()

        cor = obter_cor_especie(
            self.especie
        )

        super().__init__(
            x=x,
            y=y,
            energia=self.ENERGIA_INICIAL,
            tamanho=self.tamanho,
            cor=cor,
        )

        # Organismo.__init__ redefine alguns atributos.
        # Reaplicamos os genes para manter consistência.
        self.aplicar_genes()

        self.cor = obter_cor_especie(
            self.especie
        )

    @staticmethod
    def gerar_genes_iniciais() -> dict[str, Any]:
        """Gera o genoma inicial de uma bactéria."""

        return {
            "velocidade": random.uniform(
                0.5,
                1.5,
            ),
            "tamanho": random.randint(
                4,
                6,
            ),
            "inteligencia": False,
            "especie": "bacteria_base",
            "esperanca_vida": random.randint(
                1000,
                2000,
            ),
            "defesa": random.uniform(
                0.1,
                1.0,
            ),
            "ataque": random.uniform(
                0.1,
                1.0,
            ),
            "eficiencia_metabolica": random.uniform(
                0.75,
                1.25,
            ),
            "raio_deteccao": random.uniform(
                70.0,
                130.0,
            ),
            "taxa_mutacao": random.uniform(
                0.05,
                0.20,
            ),
        }

    def completar_genes_ausentes(
        self,
    ) -> None:
        """
        Adiciona genes que possam não existir em genomas antigos.

        Isso mantém compatibilidade com versões anteriores do projeto.
        """

        valores_padrao = self.gerar_genes_iniciais()

        for gene, valor in valores_padrao.items():
            self.genes.setdefault(
                gene,
                valor,
            )

    def aplicar_genes(
        self,
    ) -> None:
        """Aplica o genoma aos atributos usados pela simulação."""

        self.velocidade = limitar(
            float(self.genes["velocidade"]),
            0.1,
            5.0,
        )

        self.tamanho = int(
            limitar(
                float(self.genes["tamanho"]),
                2.0,
                16.0,
            )
        )

        self.inteligencia = bool(
            self.genes["inteligencia"]
        )

        self.especie = str(
            self.genes["especie"]
        )

        self.esperanca_vida = max(
            100,
            int(self.genes["esperanca_vida"]),
        )

        self.defesa = limitar(
            float(self.genes["defesa"]),
            0.05,
            10.0,
        )

        self.ataque = limitar(
            float(self.genes["ataque"]),
            0.05,
            10.0,
        )

        self.eficiencia_metabolica = limitar(
            float(
                self.genes["eficiencia_metabolica"]
            ),
            0.25,
            2.5,
        )

        self.raio_deteccao = limitar(
            float(self.genes["raio_deteccao"]),
            20.0,
            300.0,
        )

        self.taxa_mutacao = limitar(
            float(self.genes["taxa_mutacao"]),
            0.001,
            0.75,
        )

        self.genes["velocidade"] = self.velocidade
        self.genes["tamanho"] = self.tamanho
        self.genes["inteligencia"] = self.inteligencia
        self.genes["especie"] = self.especie
        self.genes["esperanca_vida"] = self.esperanca_vida
        self.genes["defesa"] = self.defesa
        self.genes["ataque"] = self.ataque
        self.genes[
            "eficiencia_metabolica"
        ] = self.eficiencia_metabolica
        self.genes[
            "raio_deteccao"
        ] = self.raio_deteccao
        self.genes[
            "taxa_mutacao"
        ] = self.taxa_mutacao

    def mover(
        self,
        quadtree: Any,
    ) -> None:
        """
        Atualiza a posição da bactéria.

        Inclui:

        - movimento direcional;
        - ruído browniano;
        - quimiotaxia leve;
        - repulsão entre organismos;
        - custo energético;
        - envelhecimento.
        """

        if self.energia <= 0:
            return

        self.aplicar_movimento_browniano()

        if self.presa == "alga":
            self.aplicar_quimiotaxia()

        self.x += (
            math.cos(self.direcao)
            * self.velocidade
        )

        self.y += (
            math.sin(self.direcao)
            * self.velocidade
        )

        self.manter_dentro_dos_limites()

        self.verificar_colisao_repelir(
            quadtree
        )

        custo_movimento = (
            self.CUSTO_MOVIMENTO_BASE
            * self.velocidade
            * max(self.tamanho / 5.0, 0.5)
        )

        custo_metabolico = (
            self.CUSTO_METABOLICO_BASE
            / self.eficiencia_metabolica
        )

        self.energia -= (
            custo_movimento
            + custo_metabolico
        )

        self.idade += 1

        if self.idade >= self.esperanca_vida:
            self.energia = 0.0

    def aplicar_movimento_browniano(
        self,
    ) -> None:
        """
        Adiciona uma pequena mudança aleatória à direção.

        Bactérias inteligentes sofrem menos ruído direcional.
        """

        intensidade = (
            0.08
            if self.inteligencia
            else 0.18
        )

        self.direcao += random.uniform(
            -intensidade,
            intensidade,
        )

        self.direcao %= 2.0 * math.pi

    def aplicar_quimiotaxia(
        self,
    ) -> None:
        """
        Direciona levemente a bactéria para regiões mais nutritivas.

        A quimiotaxia não substitui a busca por alimento realizada pelo Mundo.
        Ela apenas influencia o deslocamento.
        """

        distancia_amostra = 14.0

        angulos = (
            self.direcao - math.pi / 4,
            self.direcao,
            self.direcao + math.pi / 4,
        )

        melhor_angulo = self.direcao
        melhor_valor = -1.0

        for angulo in angulos:
            amostra_x = self.limitar_x(
                self.x
                + math.cos(angulo)
                * distancia_amostra
            )

            amostra_y = self.limitar_y(
                self.y
                + math.sin(angulo)
                * distancia_amostra
            )

            valor = nivel_nutrientes(
                amostra_x,
                amostra_y,
            )

            if valor > melhor_valor:
                melhor_valor = valor
                melhor_angulo = angulo

        intensidade = (
            0.45
            if self.inteligencia
            else 0.15
        )

        diferenca = normalizar_angulo(
            melhor_angulo
            - self.direcao
        )

        self.direcao += (
            diferenca
            * intensidade
        )

    def verificar_colisao_repelir(
        self,
        quadtree: Any,
    ) -> None:
        """
        Aplica repulsão suave contra organismos próximos.

        O método aceita qualquer implementação de quadtree que exponha:

            query(retangulo, lista_resultado)
        """

        if quadtree is None:
            return

        raio_busca = max(
            self.tamanho * 2.5,
            12.0,
        )

        area_busca = (
            self.x - raio_busca,
            self.y - raio_busca,
            raio_busca * 2,
            raio_busca * 2,
        )

        proximos: list[Any] = []

        try:
            quadtree.query(
                area_busca,
                proximos,
            )
        except (AttributeError, TypeError):
            return

        deslocamento_x = 0.0
        deslocamento_y = 0.0

        quantidade_colisoes = 0

        for organismo in proximos:
            if organismo is self:
                continue

            dx = self.x - organismo.x
            dy = self.y - organismo.y

            distancia_quadrada = (
                dx * dx
                + dy * dy
            )

            tamanho_outro = float(
                getattr(
                    organismo,
                    "tamanho",
                    3,
                )
            )

            raio_total = (
                self.tamanho
                + tamanho_outro
            )

            if distancia_quadrada >= raio_total * raio_total:
                continue

            if distancia_quadrada <= 0.000001:
                angulo = random.uniform(
                    0.0,
                    2.0 * math.pi,
                )

                dx = math.cos(angulo)
                dy = math.sin(angulo)
                distancia = 1.0

            else:
                distancia = math.sqrt(
                    distancia_quadrada
                )

            sobreposicao = (
                raio_total
                - distancia
            )

            deslocamento_x += (
                dx / distancia
            ) * sobreposicao

            deslocamento_y += (
                dy / distancia
            ) * sobreposicao

            quantidade_colisoes += 1

        if quantidade_colisoes == 0:
            return

        fator_repulsao = 0.10

        self.x += (
            deslocamento_x
            / quantidade_colisoes
        ) * fator_repulsao

        self.y += (
            deslocamento_y
            / quantidade_colisoes
        ) * fator_repulsao

        self.x = self.limitar_x(
            self.x
        )

        self.y = self.limitar_y(
            self.y
        )

    def combinar_genes(
        self,
        parceiro: Bacteria,
    ) -> dict[str, Any]:
        """
        Combina genes entre duas bactérias.

        Genes numéricos podem ser herdados diretamente ou combinados por média.
        """

        genes_resultantes: dict[str, Any] = {}

        todos_os_genes = set(
            self.genes
        ) | set(
            parceiro.genes
        )

        for gene in todos_os_genes:
            valor_a = self.genes.get(
                gene
            )

            valor_b = parceiro.genes.get(
                gene,
                valor_a,
            )

            if gene == "especie":
                genes_resultantes[gene] = (
                    valor_a
                    if random.random() < 0.5
                    else valor_b
                )

                continue

            if gene == "inteligencia":
                genes_resultantes[gene] = (
                    bool(valor_a)
                    if random.random() < 0.5
                    else bool(valor_b)
                )

                continue

            if isinstance(
                valor_a,
                (int, float),
            ) and isinstance(
                valor_b,
                (int, float),
            ):
                estrategia = random.random()

                if estrategia < 0.4:
                    valor = valor_a

                elif estrategia < 0.8:
                    valor = valor_b

                else:
                    valor = (
                        float(valor_a)
                        + float(valor_b)
                    ) / 2.0

                if gene in {
                    "tamanho",
                    "esperanca_vida",
                }:
                    valor = int(
                        round(valor)
                    )

                genes_resultantes[gene] = valor

            else:
                genes_resultantes[gene] = (
                    valor_a
                    if random.random() < 0.5
                    else valor_b
                )

        return genes_resultantes

    def mutar(
        self,
    ) -> bool:
        """
        Aplica mutação a um gene.

        Retorna True quando uma mutação ocorre.
        """

        if random.random() >= self.taxa_mutacao:
            return False

        genes_mutaveis = [
            "velocidade",
            "tamanho",
            "inteligencia",
            "especie",
            "esperanca_vida",
            "defesa",
            "ataque",
            "eficiencia_metabolica",
            "raio_deteccao",
            "taxa_mutacao",
        ]

        gene = random.choice(
            genes_mutaveis
        )

        if gene == "velocidade":
            self.genes[gene] += random.gauss(
                0.0,
                0.15,
            )

        elif gene == "tamanho":
            self.genes[gene] += random.choice(
                (-1, 1)
            )

        elif gene == "inteligencia":
            self.genes[gene] = not bool(
                self.genes[gene]
            )

        elif gene == "especie":
            especie_anterior = str(
                self.genes["especie"]
            )

            self.genes[gene] = gerar_nome_especie(
                especie_anterior
            )

        elif gene == "esperanca_vida":
            self.genes[gene] += random.randint(
                -150,
                150,
            )

        elif gene == "defesa":
            self.genes[gene] += random.gauss(
                0.0,
                0.12,
            )

        elif gene == "ataque":
            self.genes[gene] += random.gauss(
                0.0,
                0.12,
            )

        elif gene == "eficiencia_metabolica":
            self.genes[gene] += random.gauss(
                0.0,
                0.08,
            )

        elif gene == "raio_deteccao":
            self.genes[gene] += random.gauss(
                0.0,
                8.0,
            )

        elif gene == "taxa_mutacao":
            self.genes[gene] += random.gauss(
                0.0,
                0.015,
            )

        self.aplicar_genes()

        self.tamanho = int(
            self.genes["tamanho"]
        )

        self.cor = obter_cor_especie(
            self.especie
        )

        return True


class Protozoario(Organismo):
    """
    Predador superior que se alimenta de bactérias.

    A procura e o consumo da presa são controlados pelo Mundo.
    Esta classe controla apenas o movimento e o metabolismo.
    """

    ENERGIA_INICIAL = 200.0

    def __init__(
        self,
        x: float,
        y: float,
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            energia=self.ENERGIA_INICIAL,
            tamanho=8,
            cor=(220, 50, 50),
        )

        self.velocidade = 1.0
        self.idade = 0
        self.esperanca_vida = random.randint(
            2500,
            4500,
        )

    def mover(
        self,
    ) -> None:
        """
        Move o protozoário mantendo a direção definida pelo Mundo.

        Quando não há alvo, uma variação aleatória produz movimento exploratório.
        """

        self.direcao += random.uniform(
            -0.12,
            0.12,
        )

        self.direcao %= 2.0 * math.pi

        self.x += (
            math.cos(self.direcao)
            * self.velocidade
        )

        self.y += (
            math.sin(self.direcao)
            * self.velocidade
        )

        self.manter_dentro_dos_limites()

        custo_movimento = (
            0.025
            * self.velocidade
        )

        self.energia -= custo_movimento

        self.idade += 1

        if self.idade >= self.esperanca_vida:
            self.energia = 0.0


def obter_cor_especie(
    especie: str,
) -> tuple[int, int, int]:
    """
    Retorna a cor de uma espécie, criando-a quando necessário.
    """

    if especie not in cores_especies:
        cores_especies[especie] = gerar_cor_unica()

    return cores_especies[especie]


def gerar_cor_unica() -> tuple[int, int, int]:
    """Gera uma cor ainda não registrada."""

    cores_existentes = set(
        cores_especies.values()
    )

    for _ in range(1000):
        cor = (
            random.randint(60, 255),
            random.randint(60, 255),
            random.randint(60, 255),
        )

        if cor not in cores_existentes:
            return cor

    # Alternativa determinística caso muitas cores já tenham sido usadas.
    indice = len(
        cores_existentes
    )

    return (
        60 + (indice * 47) % 196,
        60 + (indice * 83) % 196,
        60 + (indice * 131) % 196,
    )


def gerar_nome_especie(
    especie_anterior: str,
) -> str:
    """
    Gera um identificador para uma nova espécie.

    O prefixo permite rastrear aproximadamente a linhagem.
    """

    prefixo = especie_anterior[:18]

    sufixo = random.randint(
        1,
        999999,
    )

    return f"{prefixo}_m{sufixo}"


def normalizar_angulo(
    angulo: float,
) -> float:
    """Normaliza um ângulo para o intervalo entre -π e π."""

    return (
        angulo + math.pi
    ) % (
        2.0 * math.pi
    ) - math.pi


def limitar(
    valor: float,
    minimo: float,
    maximo: float,
) -> float:
    """Limita um número ao intervalo informado."""

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
