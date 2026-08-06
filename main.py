# main.py
from __future__ import annotations

import asyncio
import sys
from collections import deque

import pygame

from configuracoes import (
    ALTURA,
    AREA_SIMULACAO_LARGURA,
    BRANCO,
    CINZA_ESCURO,
    FPS,
    LARGURA,
    PRETO,
)
from mundo import Mundo


class Aplicacao:
    """Controla a janela, os eventos e a renderização da simulação."""

    def __init__(self) -> None:
        pygame.init()

        self.tela = pygame.display.set_mode(
            (LARGURA, ALTURA)
        )

        pygame.display.set_caption(
            "Simulação de Evolução Bacteriana"
        )

        self.relogio = pygame.time.Clock()

        # Fontes internas do Pygame são mais compatíveis
        # com navegador/WebAssembly do que SysFont.
        self.fonte = pygame.font.Font(
            None,
            24,
        )

        self.fonte_pequena = pygame.font.Font(
            None,
            20,
        )

        self.fonte_titulo = pygame.font.Font(
            None,
            30,
        )

        # O mundo será inicializado depois que o navegador
        # receber o primeiro frame.
        self.mundo: Mundo | None = None

        self.rodando = True
        self.pausado = False
        self.exibir_ajuda = False

        self.velocidade_simulacao = 1
        self.frame = 0

        tamanho_historico = 300

        self.historico_bacterias: deque[int] = deque(
            maxlen=tamanho_historico
        )

        self.historico_algas: deque[int] = deque(
            maxlen=tamanho_historico
        )

        self.historico_protozoarios: deque[int] = deque(
            maxlen=tamanho_historico
        )

    async def executar(self) -> None:
        """
        Executa o loop principal no desktop e no navegador.
        """

        # Mostra um primeiro frame imediatamente.
        self.desenhar_tela_inicial(
            "Inicializando simulação..."
        )

        pygame.display.flip()

        # Entrega o controle ao navegador.
        await asyncio.sleep(0)

        try:
            self.mundo = Mundo()

        except Exception as erro:
            print("ERRO AO CRIAR O MUNDO:")
            print(repr(erro))

            self.desenhar_tela_de_erro(
                titulo="Erro ao inicializar a simulação.",
                detalhe=repr(erro),
            )

            pygame.display.flip()

            while self.rodando:
                self.processar_eventos()
                await asyncio.sleep(0)

            return

        while self.rodando:
            self.processar_eventos()

            if (
                not self.pausado
                and self.mundo is not None
            ):
                try:
                    for _ in range(
                        self.velocidade_simulacao
                    ):
                        self.mundo.atualizar()
                        self.frame += 1

                    self.registrar_historico()

                except Exception as erro:
                    print("ERRO DURANTE A SIMULAÇÃO:")
                    print(repr(erro))

                    self.pausado = True

                    self.desenhar_tela_de_erro(
                        titulo=(
                            "A simulação encontrou um erro."
                        ),
                        detalhe=repr(erro),
                    )

                    pygame.display.flip()

                    while self.rodando:
                        self.processar_eventos()
                        await asyncio.sleep(0)

                    return

            self.desenhar()

            pygame.display.flip()

            # Clock.tick pode bloquear ou produzir comportamento
            # inadequado dentro do WebAssembly.
            if sys.platform != "emscripten":
                self.relogio.tick(FPS)

            # Obrigatório para o Pygbag.
            await asyncio.sleep(0)

        if sys.platform != "emscripten":
            pygame.quit()

    def processar_eventos(self) -> None:
        """Processa teclado, mouse e encerramento."""

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False

            elif evento.type == pygame.KEYDOWN:
                self.processar_tecla(
                    evento.key
                )

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                self.processar_clique(
                    evento
                )

    def processar_tecla(
        self,
        tecla: int,
    ) -> None:
        """Executa comandos associados ao teclado."""

        if tecla == pygame.K_ESCAPE:
            self.rodando = False

        elif tecla == pygame.K_SPACE:
            self.pausado = not self.pausado

        elif tecla == pygame.K_r:
            self.reiniciar()

        elif tecla == pygame.K_h:
            self.exibir_ajuda = (
                not self.exibir_ajuda
            )

        elif tecla in (
            pygame.K_PLUS,
            pygame.K_KP_PLUS,
            pygame.K_EQUALS,
        ):
            self.velocidade_simulacao = min(
                self.velocidade_simulacao + 1,
                10,
            )

        elif tecla in (
            pygame.K_MINUS,
            pygame.K_KP_MINUS,
        ):
            self.velocidade_simulacao = max(
                self.velocidade_simulacao - 1,
                1,
            )

        elif tecla == pygame.K_1:
            self.velocidade_simulacao = 1

        elif tecla == pygame.K_2:
            self.velocidade_simulacao = 2

        elif tecla == pygame.K_3:
            self.velocidade_simulacao = 4

        elif tecla == pygame.K_4:
            self.velocidade_simulacao = 8

        elif tecla == pygame.K_b:
            if self.mundo is None:
                return

            posicao = pygame.mouse.get_pos()

            if self.posicao_dentro_da_simulacao(
                posicao
            ):
                self.mundo.adicionar_bacteria_na_posicao(
                    *posicao
                )

        elif tecla == pygame.K_a:
            if self.mundo is None:
                return

            posicao = pygame.mouse.get_pos()

            if self.posicao_dentro_da_simulacao(
                posicao
            ):
                self.mundo.adicionar_alga_na_posicao(
                    *posicao
                )

    def processar_clique(
        self,
        evento: pygame.event.Event,
    ) -> None:
        """Permite inserir organismos usando o mouse."""

        if self.mundo is None:
            return

        x, y = evento.pos

        if not self.posicao_dentro_da_simulacao(
            (x, y)
        ):
            return

        if evento.button == 1:
            self.mundo.adicionar_alga_na_posicao(
                x,
                y,
            )

        elif evento.button == 3:
            self.mundo.adicionar_bacteria_na_posicao(
                x,
                y,
            )

    def posicao_dentro_da_simulacao(
        self,
        posicao: tuple[int, int],
    ) -> bool:
        """Verifica se uma posição pertence à área da simulação."""

        x, y = posicao

        return (
            0 <= x < AREA_SIMULACAO_LARGURA
            and 0 <= y < ALTURA
        )

    def reiniciar(self) -> None:
        """Recria completamente o mundo da simulação."""

        try:
            self.mundo = Mundo()

        except Exception as erro:
            print("ERRO AO REINICIAR O MUNDO:")
            print(repr(erro))

            self.desenhar_tela_de_erro(
                titulo="Erro ao reiniciar a simulação.",
                detalhe=repr(erro),
            )

            pygame.display.flip()

            self.pausado = True

            return

        self.frame = 0
        self.pausado = False

        self.historico_bacterias.clear()
        self.historico_algas.clear()
        self.historico_protozoarios.clear()

    def registrar_historico(self) -> None:
        """Registra populações para o gráfico lateral."""

        if self.mundo is None:
            return

        estatisticas = (
            self.mundo.obter_estatisticas()
        )

        self.historico_bacterias.append(
            estatisticas["bacterias"]
        )

        self.historico_algas.append(
            estatisticas["algas"]
        )

        self.historico_protozoarios.append(
            estatisticas["protozoarios"]
        )

    def desenhar(self) -> None:
        """Desenha todos os elementos da interface."""

        self.tela.fill(PRETO)

        if self.mundo is None:
            self.desenhar_tela_inicial(
                "Inicializando simulação..."
            )
            return

        self.mundo.desenhar(
            self.tela
        )

        # O painel é desenhado antes do separador
        # para não cobrir a linha.
        self.desenhar_painel()
        self.desenhar_separador()
        self.desenhar_status()

        if self.exibir_ajuda:
            self.desenhar_ajuda()

    def desenhar_tela_inicial(
        self,
        mensagem: str,
    ) -> None:
        """Desenha a tela de inicialização."""

        self.tela.fill(
            (8, 18, 24)
        )

        texto = self.fonte_titulo.render(
            mensagem,
            True,
            BRANCO,
        )

        retangulo = texto.get_rect(
            center=(
                LARGURA // 2,
                ALTURA // 2,
            )
        )

        self.tela.blit(
            texto,
            retangulo,
        )

    def desenhar_tela_de_erro(
        self,
        titulo: str,
        detalhe: str,
    ) -> None:
        """Exibe erros de inicialização na própria tela."""

        self.tela.fill(
            (35, 8, 8)
        )

        texto_titulo = self.fonte_titulo.render(
            titulo,
            True,
            BRANCO,
        )

        self.tela.blit(
            texto_titulo,
            (30, 30),
        )

        detalhe_limitado = detalhe[:180]

        linhas = self.quebrar_texto(
            detalhe_limitado,
            limite=70,
        )

        y = 80

        for linha in linhas:
            texto_detalhe = (
                self.fonte_pequena.render(
                    linha,
                    True,
                    BRANCO,
                )
            )

            self.tela.blit(
                texto_detalhe,
                (30, y),
            )

            y += 24

        instrucao = self.fonte_pequena.render(
            "Abra o Console do navegador para ver o traceback completo.",
            True,
            BRANCO,
        )

        self.tela.blit(
            instrucao,
            (30, y + 20),
        )

    @staticmethod
    def quebrar_texto(
        texto: str,
        limite: int,
    ) -> list[str]:
        """Divide texto longo em linhas menores."""

        palavras = texto.split()

        linhas: list[str] = []
        linha_atual = ""

        for palavra in palavras:
            candidato = (
                f"{linha_atual} {palavra}".strip()
            )

            if len(candidato) <= limite:
                linha_atual = candidato

            else:
                if linha_atual:
                    linhas.append(
                        linha_atual
                    )

                linha_atual = palavra

        if linha_atual:
            linhas.append(
                linha_atual
            )

        return linhas

    def desenhar_separador(self) -> None:
        """Desenha a separação entre simulação e painel."""

        pygame.draw.line(
            self.tela,
            BRANCO,
            (
                AREA_SIMULACAO_LARGURA,
                0,
            ),
            (
                AREA_SIMULACAO_LARGURA,
                ALTURA,
            ),
            2,
        )

    def desenhar_painel(self) -> None:
        """Desenha informações e gráficos no painel lateral."""

        if self.mundo is None:
            return

        painel = pygame.Rect(
            AREA_SIMULACAO_LARGURA,
            0,
            LARGURA - AREA_SIMULACAO_LARGURA,
            ALTURA,
        )

        pygame.draw.rect(
            self.tela,
            CINZA_ESCURO,
            painel,
        )

        x = AREA_SIMULACAO_LARGURA + 20
        y = 20

        titulo = self.fonte_titulo.render(
            "Simulação microbiana",
            True,
            BRANCO,
        )

        self.tela.blit(
            titulo,
            (x, y),
        )

        y += 40

        estatisticas = (
            self.mundo.obter_estatisticas()
        )

        informacoes = [
            (
                "Bactérias",
                estatisticas["bacterias"],
            ),
            (
                "Algas",
                estatisticas["algas"],
            ),
            (
                "Protozoários",
                estatisticas["protozoarios"],
            ),
            (
                "Carcaças",
                estatisticas["carcacas"],
            ),
            (
                "Espécies",
                estatisticas["especies"],
            ),
            (
                "Ciclo",
                estatisticas[
                    "ciclo_luz"
                ].capitalize(),
            ),
            (
                "Tempo",
                estatisticas["tempo"],
            ),
            (
                "Velocidade",
                f"{self.velocidade_simulacao}x",
            ),
            (
                "FPS",
                int(
                    self.relogio.get_fps()
                ),
            ),
        ]

        for rotulo, valor in informacoes:
            texto = self.fonte.render(
                f"{rotulo}: {valor}",
                True,
                BRANCO,
            )

            self.tela.blit(
                texto,
                (x, y),
            )

            y += 24

        y += 10

        pygame.draw.line(
            self.tela,
            (100, 100, 100),
            (x, y),
            (LARGURA - 20, y),
        )

        y += 20

        titulo_grafico = self.fonte.render(
            "Histórico populacional",
            True,
            BRANCO,
        )

        self.tela.blit(
            titulo_grafico,
            (x, y),
        )

        y += 30

        area_grafico = pygame.Rect(
            x,
            y,
            LARGURA - x - 20,
            220,
        )

        self.desenhar_grafico_populacao(
            area_grafico
        )

        y += 250

        titulo_especies = self.fonte.render(
            "Espécies dominantes",
            True,
            BRANCO,
        )

        self.tela.blit(
            titulo_especies,
            (x, y),
        )

        y += 28

        especies = (
            self.mundo.obter_especies_mais_abundantes(
                limite=10
            )
        )

        if not especies:
            texto = self.fonte_pequena.render(
                "Nenhuma bactéria viva.",
                True,
                BRANCO,
            )

            self.tela.blit(
                texto,
                (x, y),
            )

            return

        for especie in especies:
            nome = especie["nome"]
            quantidade = especie["quantidade"]
            cor = especie["cor"]
            presa = especie["presa"]

            pygame.draw.rect(
                self.tela,
                cor,
                (
                    x,
                    y + 3,
                    12,
                    12,
                ),
            )

            texto = self.fonte_pequena.render(
                (
                    f"{nome}: {quantidade} "
                    f"| presa: {presa}"
                ),
                True,
                BRANCO,
            )

            self.tela.blit(
                texto,
                (x + 20, y),
            )

            y += 20

    def desenhar_grafico_populacao(
        self,
        area: pygame.Rect,
    ) -> None:
        """Desenha gráfico populacional sem Matplotlib."""

        pygame.draw.rect(
            self.tela,
            (25, 25, 25),
            area,
        )

        pygame.draw.rect(
            self.tela,
            (100, 100, 100),
            area,
            1,
        )

        historicos = [
            (
                self.historico_bacterias,
                (0, 255, 100),
            ),
            (
                self.historico_algas,
                (0, 150, 0),
            ),
            (
                self.historico_protozoarios,
                (255, 80, 80),
            ),
        ]

        maior_valor = max(
            [
                max(
                    historico,
                    default=1,
                )
                for historico, _ in historicos
            ],
            default=1,
        )

        maior_valor = max(
            maior_valor,
            1,
        )

        for historico, cor in historicos:
            if len(historico) < 2:
                continue

            pontos: list[
                tuple[int, int]
            ] = []

            valores = list(
                historico
            )

            for indice, valor in enumerate(
                valores
            ):
                proporcao_x = (
                    indice
                    / max(
                        len(valores) - 1,
                        1,
                    )
                )

                proporcao_y = (
                    valor / maior_valor
                )

                ponto_x = (
                    area.left
                    + int(
                        proporcao_x
                        * area.width
                    )
                )

                ponto_y = (
                    area.bottom
                    - int(
                        proporcao_y
                        * area.height
                    )
                )

                pontos.append(
                    (
                        ponto_x,
                        ponto_y,
                    )
                )

            if len(pontos) >= 2:
                pygame.draw.lines(
                    self.tela,
                    cor,
                    False,
                    pontos,
                    2,
                )

        legenda_y = area.bottom + 8

        legendas = [
            (
                "Bactérias",
                (0, 255, 100),
            ),
            (
                "Algas",
                (0, 150, 0),
            ),
            (
                "Protozoários",
                (255, 80, 80),
            ),
        ]

        legenda_x = area.left

        for nome, cor in legendas:
            pygame.draw.rect(
                self.tela,
                cor,
                (
                    legenda_x,
                    legenda_y + 3,
                    10,
                    10,
                ),
            )

            texto = self.fonte_pequena.render(
                nome,
                True,
                BRANCO,
            )

            self.tela.blit(
                texto,
                (
                    legenda_x + 15,
                    legenda_y,
                ),
            )

            legenda_x += 100

    def desenhar_status(self) -> None:
        """Mostra o estado de pausa."""

        if not self.pausado:
            return

        superficie = pygame.Surface(
            (
                AREA_SIMULACAO_LARGURA,
                ALTURA,
            ),
            pygame.SRCALPHA,
        )

        superficie.fill(
            (0, 0, 0, 100)
        )

        self.tela.blit(
            superficie,
            (0, 0),
        )

        texto = self.fonte_titulo.render(
            "SIMULAÇÃO PAUSADA",
            True,
            BRANCO,
        )

        retangulo = texto.get_rect(
            center=(
                AREA_SIMULACAO_LARGURA // 2,
                ALTURA // 2,
            )
        )

        self.tela.blit(
            texto,
            retangulo,
        )

    def desenhar_ajuda(self) -> None:
        """Desenha uma janela de ajuda."""

        largura_ajuda = 520
        altura_ajuda = 360

        x = (
            AREA_SIMULACAO_LARGURA
            - largura_ajuda
        ) // 2

        y = (
            ALTURA
            - altura_ajuda
        ) // 2

        area = pygame.Rect(
            x,
            y,
            largura_ajuda,
            altura_ajuda,
        )

        pygame.draw.rect(
            self.tela,
            (20, 20, 20),
            area,
            border_radius=8,
        )

        pygame.draw.rect(
            self.tela,
            BRANCO,
            area,
            width=2,
            border_radius=8,
        )

        titulo = self.fonte_titulo.render(
            "Controles",
            True,
            BRANCO,
        )

        self.tela.blit(
            titulo,
            (
                x + 20,
                y + 20,
            ),
        )

        comandos = [
            "Espaço: pausar ou continuar",
            "R: reiniciar a simulação",
            "H: mostrar ou ocultar esta ajuda",
            "+ / -: alterar velocidade",
            "1, 2, 3 e 4: atalhos de velocidade",
            "A: adicionar alga na posição do mouse",
            "B: adicionar bactéria na posição do mouse",
            "Clique esquerdo: adicionar alga",
            "Clique direito: adicionar bactéria",
            "Esc: fechar a simulação",
        ]

        linha_y = y + 65

        for comando in comandos:
            texto = self.fonte.render(
                comando,
                True,
                BRANCO,
            )

            self.tela.blit(
                texto,
                (
                    x + 20,
                    linha_y,
                ),
            )

            linha_y += 27


async def main() -> None:
    aplicacao = Aplicacao()
    await aplicacao.executar()


if __name__ == "__main__":
    asyncio.run(main())
