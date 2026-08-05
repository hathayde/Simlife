# mundo.py
from __future__ import annotations

import random
from collections import Counter
from typing import Any

import pygame

from configuracoes import (
    ALTURA,
    AREA_SIMULACAO_LARGURA,
    DURACAO_CICLO,
    MAX_ALGAS,
    MAX_BACTERIAS,
    MAX_PROTOZOARIOS,
)
from organismos import (
    Alga,
    Bacteria,
    Carcaca,
    Protozoario,
    cores_especies,
)
from quadtree import Quadtree


class Mundo:
    """
    Gerencia o estado completo da simulação.

    Esta classe é a única responsável por:

    - armazenar organismos;
    - adicionar e remover organismos;
    - aplicar os limites populacionais;
    - atualizar o ciclo de luz;
    - reconstruir a estrutura espacial;
    - processar reprodução, alimentação e morte;
    - desenhar os organismos.
    """

    def __init__(self) -> None:
        self.tempo = 0
        self.ciclo_luz = "dia"

        self.bacterias: list[Bacteria] = []
        self.algas: list[Alga] = []
        self.carcacas: list[Carcaca] = []
        self.protozoarios: list[Protozoario] = []

        self.quadtree = self.criar_quadtree()

        self.inicializar_populacoes()

    def inicializar_populacoes(self) -> None:
        """Cria as populações iniciais respeitando os limites."""

        quantidade_inicial_bacterias = min(10, MAX_BACTERIAS)
        quantidade_inicial_algas = min(500, MAX_ALGAS)
        quantidade_inicial_protozoarios = min(
            5,
            MAX_PROTOZOARIOS,
        )

        for _ in range(quantidade_inicial_bacterias):
            self.adicionar_bacteria(
                Bacteria(
                    random.uniform(0, AREA_SIMULACAO_LARGURA),
                    random.uniform(0, ALTURA),
                    presa="alga",
                )
            )

        for _ in range(quantidade_inicial_algas):
            self.adicionar_alga(
                Alga(
                    random.uniform(0, AREA_SIMULACAO_LARGURA),
                    random.uniform(0, ALTURA),
                )
            )

        for _ in range(quantidade_inicial_protozoarios):
            self.adicionar_protozoario(
                Protozoario(
                    random.uniform(0, AREA_SIMULACAO_LARGURA),
                    random.uniform(0, ALTURA),
                )
            )

    def criar_quadtree(self) -> Quadtree:
        """Cria uma nova árvore espacial cobrindo toda a simulação."""

        limites = (
            0,
            0,
            AREA_SIMULACAO_LARGURA,
            ALTURA,
        )

        return Quadtree(
            limites,
            capacity=8,
        )

    def reconstruir_quadtree(self) -> None:
        """
        Recria a árvore espacial com as posições atuais.

        A quadtree precisa ser reconstruída porque os organismos se movem.
        """

        self.quadtree = self.criar_quadtree()

        for bacteria in self.bacterias:
            self.quadtree.insert(bacteria)

        for alga in self.algas:
            self.quadtree.insert(alga)

        for carcaca in self.carcacas:
            self.quadtree.insert(carcaca)

        for protozoario in self.protozoarios:
            self.quadtree.insert(protozoario)

    def atualizar(self) -> None:
        """Executa um passo completo da simulação."""

        self.tempo += 1

        self.atualizar_ciclo_luz()
        self.reconstruir_quadtree()

        self.atualizar_algas()
        self.atualizar_bacterias()
        self.atualizar_protozoarios()
        self.atualizar_carcacas()

        self.garantir_limites_populacionais()

    def atualizar_ciclo_luz(self) -> None:
        """Alterna entre dia e noite."""

        if self.tempo % DURACAO_CICLO != 0:
            return

        if self.ciclo_luz == "dia":
            self.ciclo_luz = "noite"
        else:
            self.ciclo_luz = "dia"
            self.reintroduzir_algas_se_necessario()

    def reintroduzir_algas_se_necessario(self) -> None:
        """
        Reintroduz uma pequena população quando as algas são extintas.

        A reposição também respeita MAX_ALGAS.
        """

        if self.algas:
            return

        quantidade = min(
            100,
            MAX_ALGAS,
        )

        for _ in range(quantidade):
            adicionada = self.adicionar_alga(
                Alga(
                    random.uniform(0, AREA_SIMULACAO_LARGURA),
                    random.uniform(0, ALTURA),
                )
            )

            if not adicionada:
                break

    def atualizar_algas(self) -> None:
        """Atualiza fotossíntese, reprodução e morte das algas."""

        sobreviventes: list[Alga] = []
        novos_individuos: list[Alga] = []

        vagas_disponiveis = max(
            0,
            MAX_ALGAS - len(self.algas),
        )

        for alga in tuple(self.algas):
            filho = alga.fotossintese(self.ciclo_luz)

            if alga.energia > 0:
                sobreviventes.append(alga)

            if filho is not None and vagas_disponiveis > 0:
                novos_individuos.append(filho)
                vagas_disponiveis -= 1

        self.algas = sobreviventes

        for filho in novos_individuos:
            self.adicionar_alga(filho)

    def atualizar_bacterias(self) -> None:
        """
        Atualiza alimentação, movimento, reprodução e morte das bactérias.

        A lista original não é modificada enquanto está sendo percorrida.
        """

        sobreviventes: list[Bacteria] = []
        novos_individuos: list[Bacteria] = []
        novas_carcacas: list[Carcaca] = []

        bacterias_inicio_frame = tuple(self.bacterias)

        vagas_disponiveis = max(
            0,
            MAX_BACTERIAS - len(bacterias_inicio_frame),
        )

        bacterias_mortas: set[int] = set()

        for bacteria in bacterias_inicio_frame:
            if id(bacteria) in bacterias_mortas:
                continue

            resultado = self.atualizar_bacteria_individual(
                bacteria=bacteria,
                bacterias_referencia=bacterias_inicio_frame,
                bacterias_mortas=bacterias_mortas,
            )

            viva = resultado["viva"]
            filho = resultado["filho"]

            if viva:
                sobreviventes.append(bacteria)
            else:
                novas_carcacas.append(
                    Carcaca(
                        bacteria.x,
                        bacteria.y,
                        energia=30,
                    )
                )

            if filho is not None and vagas_disponiveis > 0:
                novos_individuos.append(filho)
                vagas_disponiveis -= 1

        self.bacterias = [
            bacteria
            for bacteria in sobreviventes
            if id(bacteria) not in bacterias_mortas
        ]

        for filho in novos_individuos:
            self.adicionar_bacteria(filho)

        for carcaca in novas_carcacas:
            self.adicionar_carcaca(carcaca)

    def atualizar_bacteria_individual(
        self,
        bacteria: Bacteria,
        bacterias_referencia: tuple[Bacteria, ...],
        bacterias_mortas: set[int],
    ) -> dict[str, Any]:
        """
        Atualiza uma bactéria sem permitir alteração direta das listas do mundo.

        A alimentação é processada pelo Mundo para evitar remoções concorrentes.
        """

        self.processar_alimentacao_bacteria(
            bacteria=bacteria,
            bacterias_referencia=bacterias_referencia,
            bacterias_mortas=bacterias_mortas,
        )

        bacteria.mover(self.quadtree)

        filho = None

        if bacteria.energia > 200:
            filho = self.criar_filho_bacteria(
                bacteria,
                bacterias_referencia,
            )

        return {
            "viva": bacteria.energia > 0,
            "filho": filho,
        }

    def processar_alimentacao_bacteria(
        self,
        bacteria: Bacteria,
        bacterias_referencia: tuple[Bacteria, ...],
        bacterias_mortas: set[int],
    ) -> None:
        """Processa a estratégia alimentar da bactéria."""

        if bacteria.presa == "alga":
            self.processar_consumo_de_alga(bacteria)
            return

        if bacteria.presa == "carcaca":
            self.processar_consumo_de_carcaca(bacteria)
            return

        self.processar_predacao_bacteriana(
            predador=bacteria,
            bacterias_referencia=bacterias_referencia,
            bacterias_mortas=bacterias_mortas,
        )

    def processar_consumo_de_alga(
        self,
        bacteria: Bacteria,
    ) -> None:
        """Permite que uma bactéria herbívora procure e consuma uma alga."""

        alvo = self.encontrar_alga_mais_proxima(
            bacteria.x,
            bacteria.y,
            raio=100,
        )

        if alvo is None:
            bacteria.energia -= 0.1
            return

        bacteria.direcao = self.calcular_direcao(
            bacteria.x,
            bacteria.y,
            alvo.x,
            alvo.y,
        )

        if not self.estao_em_contato(bacteria, alvo):
            return

        try:
            self.algas.remove(alvo)
            bacteria.energia += 30
        except ValueError:
            pass

    def processar_consumo_de_carcaca(
        self,
        bacteria: Bacteria,
    ) -> None:
        """Permite que uma bactéria carniceira consuma uma carcaça."""

        alvo = self.encontrar_carcaca_mais_proxima(
            bacteria.x,
            bacteria.y,
            raio=100,
        )

        if alvo is None:
            bacteria.energia -= 0.1
            return

        bacteria.direcao = self.calcular_direcao(
            bacteria.x,
            bacteria.y,
            alvo.x,
            alvo.y,
        )

        if not self.estao_em_contato(bacteria, alvo):
            return

        try:
            bacteria.energia += alvo.energia
            self.carcacas.remove(alvo)
        except ValueError:
            pass

    def processar_predacao_bacteriana(
        self,
        predador: Bacteria,
        bacterias_referencia: tuple[Bacteria, ...],
        bacterias_mortas: set[int],
    ) -> None:
        """Processa a caça de uma espécie bacteriana por outra."""

        alvo = self.encontrar_bacteria_presa_mais_proxima(
            predador=predador,
            bacterias_referencia=bacterias_referencia,
            bacterias_mortas=bacterias_mortas,
            raio=100,
        )

        if alvo is None:
            predador.energia -= 0.1
            return

        predador.direcao = self.calcular_direcao(
            predador.x,
            predador.y,
            alvo.x,
            alvo.y,
        )

        if not self.estao_em_contato(predador, alvo):
            return

        denominador = predador.ataque + alvo.defesa

        if denominador <= 0:
            chance_sucesso = 0
        else:
            chance_sucesso = predador.ataque / denominador

        if random.random() < chance_sucesso:
            bacterias_mortas.add(id(alvo))

            self.adicionar_carcaca(
                Carcaca(
                    alvo.x,
                    alvo.y,
                    energia=30,
                )
            )

            predador.energia += 50
        else:
            predador.energia -= 10

    def criar_filho_bacteria(
        self,
        bacteria: Bacteria,
        bacterias_referencia: tuple[Bacteria, ...],
    ) -> Bacteria | None:
        """Cria um descendente sem inseri-lo diretamente no mundo."""

        parceiros = [
            parceiro
            for parceiro in bacterias_referencia
            if parceiro is not bacteria
            and parceiro.energia > 0
        ]

        if not parceiros:
            return None

        parceiro = random.choice(parceiros)

        bacteria.energia /= 2

        genes = bacteria.combinar_genes(parceiro)

        novo_x = self.limitar_x(
            bacteria.x + random.uniform(-5, 5)
        )

        novo_y = self.limitar_y(
            bacteria.y + random.uniform(-5, 5)
        )

        filho = Bacteria(
            novo_x,
            novo_y,
            genes=genes,
            presa=bacteria.presa,
        )

        filho.mutar()

        return filho

    def atualizar_protozoarios(self) -> None:
        """Atualiza os protozoários e sua predação sobre bactérias."""

        sobreviventes: list[Protozoario] = []

        for protozoario in tuple(self.protozoarios):
            self.processar_protozoario(protozoario)

            if protozoario.energia > 0:
                sobreviventes.append(protozoario)

        self.protozoarios = sobreviventes

    def processar_protozoario(
        self,
        protozoario: Protozoario,
    ) -> None:
        """Atualiza movimento e alimentação de um protozoário."""

        alvo = self.encontrar_bacteria_mais_proxima(
            protozoario.x,
            protozoario.y,
            raio=150,
        )

        if alvo is not None:
            protozoario.direcao = self.calcular_direcao(
                protozoario.x,
                protozoario.y,
                alvo.x,
                alvo.y,
            )

        protozoario.mover()

        if alvo is not None and self.estao_em_contato(
            protozoario,
            alvo,
        ):
            try:
                self.bacterias.remove(alvo)

                self.adicionar_carcaca(
                    Carcaca(
                        alvo.x,
                        alvo.y,
                        energia=20,
                    )
                )

                protozoario.energia += 50
            except ValueError:
                pass

        protozoario.energia -= 0.1

    def atualizar_carcacas(self) -> None:
        """Degrada carcaças ao longo do tempo."""

        sobreviventes: list[Carcaca] = []

        for carcaca in self.carcacas:
            carcaca.energia -= 0.05

            if carcaca.energia > 0:
                sobreviventes.append(carcaca)

        self.carcacas = sobreviventes

    def adicionar_bacteria(
        self,
        bacteria: Bacteria,
    ) -> bool:
        """Adiciona uma bactéria somente se houver capacidade."""

        if len(self.bacterias) >= MAX_BACTERIAS:
            return False

        bacteria.x = self.limitar_x(bacteria.x)
        bacteria.y = self.limitar_y(bacteria.y)

        self.bacterias.append(bacteria)

        return True

    def adicionar_alga(
        self,
        alga: Alga,
    ) -> bool:
        """Adiciona uma alga somente se houver capacidade."""

        if len(self.algas) >= MAX_ALGAS:
            return False

        alga.x = self.limitar_x(alga.x)
        alga.y = self.limitar_y(alga.y)

        self.algas.append(alga)

        return True

    def adicionar_protozoario(
        self,
        protozoario: Protozoario,
    ) -> bool:
        """Adiciona um protozoário somente se houver capacidade."""

        if len(self.protozoarios) >= MAX_PROTOZOARIOS:
            return False

        protozoario.x = self.limitar_x(protozoario.x)
        protozoario.y = self.limitar_y(protozoario.y)

        self.protozoarios.append(protozoario)

        return True

    def adicionar_carcaca(
        self,
        carcaca: Carcaca,
    ) -> bool:
        """Adiciona uma carcaça ao mundo."""

        carcaca.x = self.limitar_x(carcaca.x)
        carcaca.y = self.limitar_y(carcaca.y)

        self.carcacas.append(carcaca)

        return True

    def adicionar_alga_na_posicao(
        self,
        x: float,
        y: float,
    ) -> bool:
        """Cria uma alga na posição informada."""

        return self.adicionar_alga(
            Alga(
                self.limitar_x(x),
                self.limitar_y(y),
            )
        )

    def adicionar_bacteria_na_posicao(
        self,
        x: float,
        y: float,
    ) -> bool:
        """Cria uma bactéria herbívora na posição informada."""

        return self.adicionar_bacteria(
            Bacteria(
                self.limitar_x(x),
                self.limitar_y(y),
                presa="alga",
            )
        )

    def garantir_limites_populacionais(self) -> None:
        """
        Aplica uma última barreira de segurança.

        Mesmo que algum método externo altere diretamente uma lista, o mundo
        volta aos limites definidos ao fim do frame.
        """

        if len(self.bacterias) > MAX_BACTERIAS:
            self.bacterias = self.bacterias[:MAX_BACTERIAS]

        if len(self.algas) > MAX_ALGAS:
            self.algas = self.algas[:MAX_ALGAS]

        if len(self.protozoarios) > MAX_PROTOZOARIOS:
            self.protozoarios = self.protozoarios[
                :MAX_PROTOZOARIOS
            ]

    def desenhar(
        self,
        tela: pygame.Surface,
    ) -> None:
        """Desenha todos os organismos na superfície recebida."""

        area_simulacao = pygame.Rect(
            0,
            0,
            AREA_SIMULACAO_LARGURA,
            ALTURA,
        )

        cor_fundo = self.obter_cor_de_fundo()

        pygame.draw.rect(
            tela,
            cor_fundo,
            area_simulacao,
        )

        for alga in self.algas:
            alga.desenhar(tela)

        for carcaca in self.carcacas:
            carcaca.desenhar(tela)

        for bacteria in self.bacterias:
            bacteria.desenhar(tela)

        for protozoario in self.protozoarios:
            protozoario.desenhar(tela)

    def obter_cor_de_fundo(self) -> tuple[int, int, int]:
        """Retorna uma cor diferente para dia e noite."""

        if self.ciclo_luz == "dia":
            return 8, 18, 24

        return 2, 5, 12

    def obter_estatisticas(self) -> dict[str, Any]:
        """Retorna os indicadores consumidos pelo painel lateral."""

        especies = {
            bacteria.especie
            for bacteria in self.bacterias
        }

        return {
            "bacterias": len(self.bacterias),
            "algas": len(self.algas),
            "protozoarios": len(self.protozoarios),
            "carcacas": len(self.carcacas),
            "especies": len(especies),
            "ciclo_luz": self.ciclo_luz,
            "tempo": self.tempo,
        }

    def obter_especies_mais_abundantes(
        self,
        limite: int = 10,
    ) -> list[dict[str, Any]]:
        """Retorna as espécies ordenadas por quantidade."""

        contagem = Counter(
            bacteria.especie
            for bacteria in self.bacterias
        )

        resultado: list[dict[str, Any]] = []

        for especie, quantidade in contagem.most_common(limite):
            representante = next(
                (
                    bacteria
                    for bacteria in self.bacterias
                    if bacteria.especie == especie
                ),
                None,
            )

            if representante is None:
                continue

            resultado.append(
                {
                    "nome": especie,
                    "quantidade": quantidade,
                    "cor": cores_especies.get(
                        especie,
                        representante.cor,
                    ),
                    "presa": representante.presa,
                }
            )

        return resultado

    def encontrar_alga_mais_proxima(
        self,
        x: float,
        y: float,
        raio: float,
    ) -> Alga | None:
        """Retorna a alga mais próxima dentro do raio."""

        return self.encontrar_organismo_mais_proximo(
            organismos=self.algas,
            x=x,
            y=y,
            raio=raio,
        )

    def encontrar_carcaca_mais_proxima(
        self,
        x: float,
        y: float,
        raio: float,
    ) -> Carcaca | None:
        """Retorna a carcaça mais próxima dentro do raio."""

        return self.encontrar_organismo_mais_proximo(
            organismos=self.carcacas,
            x=x,
            y=y,
            raio=raio,
        )

    def encontrar_bacteria_mais_proxima(
        self,
        x: float,
        y: float,
        raio: float,
    ) -> Bacteria | None:
        """Retorna a bactéria mais próxima dentro do raio."""

        return self.encontrar_organismo_mais_proximo(
            organismos=self.bacterias,
            x=x,
            y=y,
            raio=raio,
        )

    def encontrar_bacteria_presa_mais_proxima(
        self,
        predador: Bacteria,
        bacterias_referencia: tuple[Bacteria, ...],
        bacterias_mortas: set[int],
        raio: float,
    ) -> Bacteria | None:
        """Localiza uma bactéria pertencente à espécie-alvo."""

        candidatos = [
            bacteria
            for bacteria in bacterias_referencia
            if bacteria is not predador
            and id(bacteria) not in bacterias_mortas
            and bacteria.especie == predador.presa
            and bacteria.energia > 0
        ]

        return self.encontrar_organismo_mais_proximo(
            organismos=candidatos,
            x=predador.x,
            y=predador.y,
            raio=raio,
        )

    @staticmethod
    def encontrar_organismo_mais_proximo(
        organismos: list[Any] | tuple[Any, ...],
        x: float,
        y: float,
        raio: float,
    ) -> Any | None:
        """Busca o organismo mais próximo usando distância quadrática."""

        melhor = None
        menor_distancia_quadrada = raio * raio

        for organismo in organismos:
            dx = organismo.x - x
            dy = organismo.y - y

            distancia_quadrada = dx * dx + dy * dy

            if distancia_quadrada < menor_distancia_quadrada:
                menor_distancia_quadrada = distancia_quadrada
                melhor = organismo

        return melhor

    @staticmethod
    def calcular_direcao(
        origem_x: float,
        origem_y: float,
        destino_x: float,
        destino_y: float,
    ) -> float:
        """Calcula o ângulo entre dois pontos."""

        import math

        return math.atan2(
            destino_y - origem_y,
            destino_x - origem_x,
        )

    @staticmethod
    def estao_em_contato(
        primeiro: Any,
        segundo: Any,
    ) -> bool:
        """Verifica sobreposição entre dois organismos."""

        dx = primeiro.x - segundo.x
        dy = primeiro.y - segundo.y

        distancia_quadrada = dx * dx + dy * dy
        raio_total = primeiro.tamanho + segundo.tamanho

        return distancia_quadrada <= raio_total * raio_total

    @staticmethod
    def limitar_x(x: float) -> float:
        """Mantém a coordenada X dentro da área válida."""

        return max(
            0,
            min(float(x), AREA_SIMULACAO_LARGURA - 1),
        )

    @staticmethod
    def limitar_y(y: float) -> float:
        """Mantém a coordenada Y dentro da área válida."""

        return max(
            0,
            min(float(y), ALTURA - 1),
        )
