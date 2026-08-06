# main.py
from __future__ import annotations

import asyncio
import math
import sys
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable

import pygame

from configuracoes import (
    ALTURA,
    AREA_SIMULACAO_LARGURA,
    BRANCO,
    CORES_ESTRATEGIAS,
    COR_DESTAQUE_SELECAO,
    COR_GRAFICO_FOTOSSINTETICAS,
    COR_GRAFICO_NECROFAGAS,
    COR_GRAFICO_PREDADORAS,
    DURACAO_MENSAGEM_INTERFACE,
    ESTRATEGIA_FOTOSSINTESE,
    ESTRATEGIA_NECROFAGIA,
    ESTRATEGIA_PREDACAO,
    FPS,
    LARGURA,
    MARGEM_SELECAO_ORGANISMO,
    NOMES_ESTRATEGIAS,
    PRETO,
    RAIO_MINIMO_SELECAO,
    TAMANHO_HISTORICO,
    TITULO_JANELA,
)
from mundo import Mundo
from organismos import Bacteria, Carcaca


# ============================================================
# CORES DA INTERFACE
# ============================================================

COR_PAINEL = (24, 30, 37)
COR_PAINEL_SECUNDARIO = (34, 42, 51)
COR_PAINEL_TERCIARIO = (20, 26, 32)

COR_BOTAO = (48, 58, 69)
COR_BOTAO_HOVER = (61, 73, 86)
COR_BOTAO_ATIVO = (34, 139, 94)
COR_BOTAO_BORDA = (88, 101, 114)

COR_TEXTO_SECUNDARIO = (170, 182, 194)
COR_TEXTO_DISCRETO = (125, 138, 151)

COR_BORDA = (72, 84, 96)
COR_GRADE_GRAFICO = (42, 51, 61)

COR_ERRO = (200, 65, 70)
COR_SUCESSO = (65, 190, 120)
COR_ALERTA = (245, 190, 70)


# ============================================================
# BOTÃO
# ============================================================

@dataclass
class Botao:
    """
    Representa um botão clicável da interface.
    """

    identificador: str
    rotulo: str
    retangulo: pygame.Rect
    acao: Callable[[], None]
    grupo: str | None = None

    def contem(
        self,
        posicao: tuple[int, int],
    ) -> bool:
        return self.retangulo.collidepoint(
            posicao
        )


# ============================================================
# APLICAÇÃO
# ============================================================

class Aplicacao:
    """
    Controla a janela, os eventos e a interface da simulação.

    A lógica ecológica permanece centralizada em Mundo.
    """

    def __init__(self) -> None:
        pygame.init()

        self.tela = pygame.display.set_mode(
            (
                LARGURA,
                ALTURA,
            )
        )

        pygame.display.set_caption(
            TITULO_JANELA
        )

        self.relogio = pygame.time.Clock()

        # Fontes internas do Pygame são mais compatíveis com Pygbag.
        self.fonte_pequena = pygame.font.Font(
            None,
            17,
        )

        self.fonte = pygame.font.Font(
            None,
            20,
        )

        self.fonte_media = pygame.font.Font(
            None,
            23,
        )

        self.fonte_titulo = pygame.font.Font(
            None,
            29,
        )

        self.fonte_grande = pygame.font.Font(
            None,
            40,
        )

        self.mundo: Mundo | None = None

        self.rodando = True
        self.pausado = False
        self.exibir_ajuda = False

        self.velocidade_simulacao = 1
        self.frame = 0

        # Ferramentas:
        # - inspecionar
        # - adicionar_fotossintetica
        # - adicionar_predadora
        # - adicionar_necrofaga
        self.ferramenta_atual = (
            "inspecionar"
        )

        self.organismo_selecionado: (
            Bacteria
            | Carcaca
            | None
        ) = None

        self.mensagem_temporaria = ""
        self.cor_mensagem_temporaria = BRANCO
        self.tempo_mensagem_temporaria = 0

        self.historico_fotossinteticas: deque[
            int
        ] = deque(
            maxlen=TAMANHO_HISTORICO
        )

        self.historico_predadoras: deque[
            int
        ] = deque(
            maxlen=TAMANHO_HISTORICO
        )

        self.historico_necrofagas: deque[
            int
        ] = deque(
            maxlen=TAMANHO_HISTORICO
        )

        self.botoes: list[Botao] = []

        self.criar_botoes()

    # ========================================================
    # EXECUÇÃO
    # ========================================================

    async def executar(self) -> None:
        """
        Executa o loop principal no desktop e no navegador.
        """

        self.desenhar_tela_inicial(
            "Inicializando ecossistema..."
        )

        pygame.display.flip()

        # Libera o navegador antes de construir o mundo.
        await asyncio.sleep(0)

        try:
            self.mundo = Mundo()

        except Exception as erro:
            print(
                "ERRO AO CRIAR O MUNDO:"
            )
            print(
                repr(erro)
            )

            await self.manter_tela_de_erro(
                titulo=(
                    "Erro ao inicializar a simulação."
                ),
                detalhe=repr(erro),
            )

            return

        self.registrar_historico()

        while self.rodando:
            self.processar_eventos()
            self.validar_selecao()

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
                    print(
                        "ERRO DURANTE A SIMULAÇÃO:"
                    )
                    print(
                        repr(erro)
                    )

                    await self.manter_tela_de_erro(
                        titulo=(
                            "A simulação encontrou um erro."
                        ),
                        detalhe=repr(erro),
                    )

                    return

            self.atualizar_mensagem_temporaria()
            self.desenhar()

            pygame.display.flip()

            if sys.platform != "emscripten":
                self.relogio.tick(
                    FPS
                )

            # Obrigatório para o Pygbag.
            await asyncio.sleep(0)

        if sys.platform != "emscripten":
            pygame.quit()

    async def manter_tela_de_erro(
        self,
        titulo: str,
        detalhe: str,
    ) -> None:
        """
        Mantém uma tela de erro ativa sem bloquear o navegador.
        """

        self.pausado = True

        while self.rodando:
            self.processar_eventos()

            self.desenhar_tela_de_erro(
                titulo=titulo,
                detalhe=detalhe,
            )

            pygame.display.flip()

            await asyncio.sleep(0)

    # ========================================================
    # BOTÕES
    # ========================================================

    def criar_botoes(self) -> None:
        """
        Cria todos os botões do painel lateral.
        """

        self.botoes.clear()

        painel_x = AREA_SIMULACAO_LARGURA
        margem = 14

        x = painel_x + margem

        largura_disponivel = (
            LARGURA
            - painel_x
            - margem * 2
        )

        espacamento = 8

        # ----------------------------------------------------
        # CONTROLES PRINCIPAIS
        # ----------------------------------------------------

        y = 48

        largura_controle = (
            largura_disponivel
            - espacamento * 2
        ) // 3

        self.botoes.extend(
            [
                Botao(
                    identificador="pausar",
                    rotulo="Pausar",
                    retangulo=pygame.Rect(
                        x,
                        y,
                        largura_controle,
                        34,
                    ),
                    acao=self.alternar_pausa,
                ),
                Botao(
                    identificador="reiniciar",
                    rotulo="Reiniciar",
                    retangulo=pygame.Rect(
                        x
                        + largura_controle
                        + espacamento,
                        y,
                        largura_controle,
                        34,
                    ),
                    acao=self.reiniciar,
                ),
                Botao(
                    identificador="ajuda",
                    rotulo="Ajuda",
                    retangulo=pygame.Rect(
                        x
                        + (
                            largura_controle
                            + espacamento
                        )
                        * 2,
                        y,
                        largura_controle,
                        34,
                    ),
                    acao=self.alternar_ajuda,
                ),
            ]
        )

        # ----------------------------------------------------
        # VELOCIDADES
        # ----------------------------------------------------

        y = 108

        largura_velocidade = (
            largura_disponivel
            - espacamento * 3
        ) // 4

        for indice, velocidade in enumerate(
            (
                1,
                2,
                4,
                8,
            )
        ):
            self.botoes.append(
                Botao(
                    identificador=(
                        f"velocidade_{velocidade}"
                    ),
                    rotulo=f"{velocidade}x",
                    retangulo=pygame.Rect(
                        x
                        + indice
                        * (
                            largura_velocidade
                            + espacamento
                        ),
                        y,
                        largura_velocidade,
                        30,
                    ),
                    acao=(
                        lambda valor=velocidade:
                        self.definir_velocidade(
                            valor
                        )
                    ),
                    grupo="velocidade",
                )
            )

        # ----------------------------------------------------
        # FERRAMENTAS
        # ----------------------------------------------------

        y = 162

        largura_ferramenta = (
            largura_disponivel
            - espacamento * 3
        ) // 4

        ferramentas = (
            (
                "inspecionar",
                "Inspec.",
            ),
            (
                "adicionar_fotossintetica",
                "Foto",
            ),
            (
                "adicionar_predadora",
                "Pred.",
            ),
            (
                "adicionar_necrofaga",
                "Necróf.",
            ),
        )

        for indice, (
            identificador,
            rotulo,
        ) in enumerate(ferramentas):
            self.botoes.append(
                Botao(
                    identificador=identificador,
                    rotulo=rotulo,
                    retangulo=pygame.Rect(
                        x
                        + indice
                        * (
                            largura_ferramenta
                            + espacamento
                        ),
                        y,
                        largura_ferramenta,
                        30,
                    ),
                    acao=(
                        lambda ferramenta=identificador:
                        self.definir_ferramenta(
                            ferramenta
                        )
                    ),
                    grupo="ferramenta",
                )
            )

    def alternar_pausa(self) -> None:
        self.pausado = not self.pausado

        if self.pausado:
            self.definir_mensagem(
                "Simulação pausada.",
                COR_ALERTA,
            )

        else:
            self.definir_mensagem(
                "Simulação retomada.",
                COR_SUCESSO,
            )

    def alternar_ajuda(self) -> None:
        self.exibir_ajuda = (
            not self.exibir_ajuda
        )

    def definir_velocidade(
        self,
        velocidade: int,
    ) -> None:
        self.velocidade_simulacao = (
            velocidade
        )

        self.definir_mensagem(
            (
                "Velocidade alterada para "
                f"{velocidade}x."
            ),
            COR_SUCESSO,
        )

    def definir_ferramenta(
        self,
        ferramenta: str,
    ) -> None:
        self.ferramenta_atual = ferramenta

        mensagens = {
            "inspecionar": (
                "Clique em uma bactéria ou carcaça."
            ),
            "adicionar_fotossintetica": (
                "Clique no mapa para adicionar "
                "uma bactéria fotossintética."
            ),
            "adicionar_predadora": (
                "Clique no mapa para adicionar "
                "uma bactéria predadora."
            ),
            "adicionar_necrofaga": (
                "Clique no mapa para adicionar "
                "uma bactéria necrófaga."
            ),
        }

        self.definir_mensagem(
            mensagens.get(
                ferramenta,
                "",
            )
        )

    # ========================================================
    # EVENTOS
    # ========================================================

    def processar_eventos(self) -> None:
        """
        Processa teclado, mouse, toque e encerramento.
        """

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False

            elif evento.type == pygame.KEYDOWN:
                self.processar_tecla(
                    evento.key
                )

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                self.processar_clique(
                    evento.pos,
                    evento.button,
                )

            elif evento.type == pygame.FINGERDOWN:
                posicao = (
                    int(
                        evento.x
                        * LARGURA
                    ),
                    int(
                        evento.y
                        * ALTURA
                    ),
                )

                self.processar_clique(
                    posicao,
                    1,
                )

    def processar_tecla(
        self,
        tecla: int,
    ) -> None:
        """
        Executa comandos associados ao teclado.
        """

        if tecla == pygame.K_ESCAPE:
            if self.exibir_ajuda:
                self.exibir_ajuda = False

            elif (
                self.organismo_selecionado
                is not None
            ):
                self.organismo_selecionado = None

        elif tecla == pygame.K_SPACE:
            self.alternar_pausa()

        elif tecla == pygame.K_r:
            self.reiniciar()

        elif tecla == pygame.K_h:
            self.alternar_ajuda()

        elif tecla == pygame.K_i:
            self.definir_ferramenta(
                "inspecionar"
            )

        elif tecla == pygame.K_f:
            self.definir_ferramenta(
                "adicionar_fotossintetica"
            )

        elif tecla == pygame.K_p:
            self.definir_ferramenta(
                "adicionar_predadora"
            )

        elif tecla == pygame.K_n:
            self.definir_ferramenta(
                "adicionar_necrofaga"
            )

        elif tecla == pygame.K_1:
            self.definir_velocidade(
                1
            )

        elif tecla == pygame.K_2:
            self.definir_velocidade(
                2
            )

        elif tecla == pygame.K_3:
            self.definir_velocidade(
                4
            )

        elif tecla == pygame.K_4:
            self.definir_velocidade(
                8
            )

        elif tecla in (
            pygame.K_PLUS,
            pygame.K_KP_PLUS,
            pygame.K_EQUALS,
        ):
            self.aumentar_velocidade()

        elif tecla in (
            pygame.K_MINUS,
            pygame.K_KP_MINUS,
        ):
            self.reduzir_velocidade()

    def aumentar_velocidade(self) -> None:
        velocidades = (
            1,
            2,
            4,
            8,
        )

        for velocidade in velocidades:
            if (
                velocidade
                > self.velocidade_simulacao
            ):
                self.definir_velocidade(
                    velocidade
                )

                return

        self.definir_velocidade(
            8
        )

    def reduzir_velocidade(self) -> None:
        velocidades = (
            8,
            4,
            2,
            1,
        )

        for velocidade in velocidades:
            if (
                velocidade
                < self.velocidade_simulacao
            ):
                self.definir_velocidade(
                    velocidade
                )

                return

        self.definir_velocidade(
            1
        )

    def processar_clique(
        self,
        posicao: tuple[int, int],
        botao_mouse: int,
    ) -> None:
        """
        Processa cliques nos controles e no ecossistema.
        """

        if self.exibir_ajuda:
            self.exibir_ajuda = False
            return

        for botao in self.botoes:
            if botao.contem(
                posicao
            ):
                botao.acao()
                return

        if not self.posicao_dentro_da_simulacao(
            posicao
        ):
            return

        if self.mundo is None:
            return

        x, y = posicao

        # Clique direito sempre funciona como inspeção rápida.
        if botao_mouse == 3:
            self.selecionar_organismo(
                x,
                y,
            )

            return

        if (
            self.ferramenta_atual
            == "inspecionar"
        ):
            self.selecionar_organismo(
                x,
                y,
            )

            return

        if (
            self.ferramenta_atual
            == "adicionar_fotossintetica"
        ):
            adicionado = (
                self.mundo
                .adicionar_fotossintetica_na_posicao(
                    x,
                    y,
                )
            )

            self.informar_resultado_adicao(
                adicionado=adicionado,
                nome=(
                    "Bactéria fotossintética"
                ),
            )

            return

        if (
            self.ferramenta_atual
            == "adicionar_predadora"
        ):
            adicionado = (
                self.mundo
                .adicionar_predadora_na_posicao(
                    x,
                    y,
                )
            )

            self.informar_resultado_adicao(
                adicionado=adicionado,
                nome=(
                    "Bactéria predadora"
                ),
            )

            return

        if (
            self.ferramenta_atual
            == "adicionar_necrofaga"
        ):
            adicionado = (
                self.mundo
                .adicionar_necrofaga_na_posicao(
                    x,
                    y,
                )
            )

            self.informar_resultado_adicao(
                adicionado=adicionado,
                nome=(
                    "Bactéria necrófaga"
                ),
            )

    def informar_resultado_adicao(
        self,
        adicionado: bool,
        nome: str,
    ) -> None:
        if adicionado:
            self.definir_mensagem(
                f"{nome} adicionada.",
                COR_SUCESSO,
            )

        else:
            self.definir_mensagem(
                (
                    "Limite populacional "
                    "atingido."
                ),
                COR_ERRO,
            )

    def posicao_dentro_da_simulacao(
        self,
        posicao: tuple[int, int],
    ) -> bool:
        x, y = posicao

        return (
            0 <= x
            < AREA_SIMULACAO_LARGURA
            and 0 <= y < ALTURA
        )

    # ========================================================
    # SELEÇÃO
    # ========================================================

    def selecionar_organismo(
        self,
        x: float,
        y: float,
    ) -> None:
        """
        Seleciona a entidade mais próxima do clique.
        """

        if self.mundo is None:
            return

        organismos = (
            self.mundo.obter_organismos()
        )

        melhor_organismo: (
            Bacteria
            | Carcaca
            | None
        ) = None

        menor_distancia_quadrada = (
            float("inf")
        )

        for organismo in organismos:
            dx = organismo.x - x
            dy = organismo.y - y

            distancia_quadrada = (
                dx * dx
                + dy * dy
            )

            tamanho = float(
                getattr(
                    organismo,
                    "tamanho",
                    3,
                )
            )

            raio_selecao = max(
                RAIO_MINIMO_SELECAO,
                tamanho
                + MARGEM_SELECAO_ORGANISMO,
            )

            if (
                distancia_quadrada
                <= raio_selecao
                * raio_selecao
                and distancia_quadrada
                < menor_distancia_quadrada
            ):
                melhor_organismo = organismo
                menor_distancia_quadrada = (
                    distancia_quadrada
                )

        self.organismo_selecionado = (
            melhor_organismo
        )

        if melhor_organismo is None:
            self.definir_mensagem(
                "Nenhuma entidade encontrada."
            )

            return

        nome = self.obter_nome_organismo(
            melhor_organismo
        )

        self.definir_mensagem(
            f"{nome} selecionada.",
            COR_SUCESSO,
        )

    def validar_selecao(self) -> None:
        """
        Remove a seleção quando a entidade deixa de existir.
        """

        if (
            self.organismo_selecionado
            is None
            or self.mundo is None
        ):
            return

        entidades_ativas = (
            self.mundo.obter_organismos()
        )

        if (
            self.organismo_selecionado
            not in entidades_ativas
        ):
            self.organismo_selecionado = None

            self.definir_mensagem(
                (
                    "A entidade selecionada "
                    "deixou de existir."
                ),
                COR_ALERTA,
            )

    @staticmethod
    def obter_nome_organismo(
        organismo: Any,
    ) -> str:
        if isinstance(
            organismo,
            Bacteria,
        ):
            return "Bactéria"

        if isinstance(
            organismo,
            Carcaca,
        ):
            return "Carcaça"

        return organismo.__class__.__name__

    # ========================================================
    # CONTROLE DO MUNDO
    # ========================================================

    def reiniciar(self) -> None:
        """
        Recria completamente o ecossistema.
        """

        try:
            self.mundo = Mundo()

        except Exception as erro:
            print(
                "ERRO AO REINICIAR:"
            )
            print(
                repr(erro)
            )

            self.definir_mensagem(
                "Não foi possível reiniciar.",
                COR_ERRO,
            )

            return

        self.frame = 0
        self.pausado = False
        self.organismo_selecionado = None

        self.historico_fotossinteticas.clear()
        self.historico_predadoras.clear()
        self.historico_necrofagas.clear()

        self.registrar_historico()

        self.definir_mensagem(
            "Ecossistema reiniciado.",
            COR_SUCESSO,
        )

    def registrar_historico(self) -> None:
        """
        Registra a população de cada estratégia.
        """

        if self.mundo is None:
            return

        estatisticas = (
            self.mundo.obter_estatisticas()
        )

        self.historico_fotossinteticas.append(
            estatisticas[
                "fotossinteticas"
            ]
        )

        self.historico_predadoras.append(
            estatisticas[
                "predadoras"
            ]
        )

        self.historico_necrofagas.append(
            estatisticas[
                "necrofagas"
            ]
        )

    # ========================================================
    # MENSAGENS
    # ========================================================

    def definir_mensagem(
        self,
        mensagem: str,
        cor: tuple[int, int, int] = BRANCO,
        duracao_frames: int = (
            DURACAO_MENSAGEM_INTERFACE
        ),
    ) -> None:
        self.mensagem_temporaria = mensagem
        self.cor_mensagem_temporaria = cor

        self.tempo_mensagem_temporaria = max(
            0,
            int(
                duracao_frames
            ),
        )

    def atualizar_mensagem_temporaria(
        self,
    ) -> None:
        if (
            self.tempo_mensagem_temporaria
            <= 0
        ):
            self.mensagem_temporaria = ""
            return

        self.tempo_mensagem_temporaria -= 1

    # ========================================================
    # RENDERIZAÇÃO PRINCIPAL
    # ========================================================

    def desenhar(self) -> None:
        """
        Desenha todos os elementos da aplicação.
        """

        self.tela.fill(
            PRETO
        )

        if self.mundo is None:
            self.desenhar_tela_inicial(
                "Inicializando ecossistema..."
            )

            return

        self.mundo.desenhar(
            self.tela
        )

        self.desenhar_organismo_selecionado()
        self.desenhar_painel()
        self.desenhar_separador()
        self.desenhar_mensagem_temporaria()

        if self.pausado:
            self.desenhar_indicador_pausa()

        if self.exibir_ajuda:
            self.desenhar_ajuda()

    def desenhar_tela_inicial(
        self,
        mensagem: str,
    ) -> None:
        self.tela.fill(
            (
                8,
                18,
                24,
            )
        )

        titulo = self.fonte_grande.render(
            "SimLife",
            True,
            BRANCO,
        )

        titulo_retangulo = titulo.get_rect(
            center=(
                LARGURA // 2,
                ALTURA // 2 - 28,
            )
        )

        self.tela.blit(
            titulo,
            titulo_retangulo,
        )

        subtitulo = self.fonte_media.render(
            mensagem,
            True,
            COR_TEXTO_SECUNDARIO,
        )

        subtitulo_retangulo = (
            subtitulo.get_rect(
                center=(
                    LARGURA // 2,
                    ALTURA // 2 + 22,
                )
            )
        )

        self.tela.blit(
            subtitulo,
            subtitulo_retangulo,
        )

    def desenhar_separador(self) -> None:
        pygame.draw.line(
            self.tela,
            COR_BORDA,
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

    # ========================================================
    # PAINEL
    # ========================================================

    def desenhar_painel(self) -> None:
        if self.mundo is None:
            return

        painel = pygame.Rect(
            AREA_SIMULACAO_LARGURA,
            0,
            (
                LARGURA
                - AREA_SIMULACAO_LARGURA
            ),
            ALTURA,
        )

        pygame.draw.rect(
            self.tela,
            COR_PAINEL,
            painel,
        )

        self.desenhar_cabecalho_painel()
        self.desenhar_rotulos_secoes()
        self.desenhar_botoes()
        self.desenhar_estatisticas()
        self.desenhar_grafico()
        self.desenhar_inspecao_ou_eventos()

    def desenhar_cabecalho_painel(
        self,
    ) -> None:
        x = (
            AREA_SIMULACAO_LARGURA
            + 14
        )

        titulo = self.fonte_titulo.render(
            "SimLife",
            True,
            BRANCO,
        )

        self.tela.blit(
            titulo,
            (
                x,
                10,
            ),
        )

        subtitulo = self.fonte_pequena.render(
            "Ecossistema bacteriano",
            True,
            COR_TEXTO_SECUNDARIO,
        )

        subtitulo_x = (
            LARGURA
            - 14
            - subtitulo.get_width()
        )

        self.tela.blit(
            subtitulo,
            (
                subtitulo_x,
                19,
            ),
        )

    def desenhar_rotulos_secoes(
        self,
    ) -> None:
        x = (
            AREA_SIMULACAO_LARGURA
            + 14
        )

        secoes = (
            (
                "VELOCIDADE",
                91,
            ),
            (
                "INTERVENÇÃO",
                145,
            ),
            (
                "ECOSSISTEMA",
                202,
            ),
            (
                "POPULAÇÃO POR ESTRATÉGIA",
                338,
            ),
        )

        for titulo, y in secoes:
            texto = self.fonte_pequena.render(
                titulo,
                True,
                COR_TEXTO_SECUNDARIO,
            )

            self.tela.blit(
                texto,
                (
                    x,
                    y,
                ),
            )

    def desenhar_botoes(self) -> None:
        posicao_mouse = (
            pygame.mouse.get_pos()
        )

        for botao in self.botoes:
            ativo = self.botao_esta_ativo(
                botao
            )

            hover = botao.contem(
                posicao_mouse
            )

            if ativo:
                cor = COR_BOTAO_ATIVO

            elif hover:
                cor = COR_BOTAO_HOVER

            else:
                cor = COR_BOTAO

            pygame.draw.rect(
                self.tela,
                cor,
                botao.retangulo,
                border_radius=6,
            )

            pygame.draw.rect(
                self.tela,
                COR_BOTAO_BORDA,
                botao.retangulo,
                width=1,
                border_radius=6,
            )

            rotulo = botao.rotulo

            if (
                botao.identificador
                == "pausar"
            ):
                rotulo = (
                    "Continuar"
                    if self.pausado
                    else "Pausar"
                )

            texto = self.fonte.render(
                rotulo,
                True,
                BRANCO,
            )

            texto_retangulo = (
                texto.get_rect(
                    center=(
                        botao.retangulo.center
                    )
                )
            )

            self.tela.blit(
                texto,
                texto_retangulo,
            )

    def botao_esta_ativo(
        self,
        botao: Botao,
    ) -> bool:
        if botao.grupo == "velocidade":
            return (
                botao.identificador
                == (
                    "velocidade_"
                    f"{self.velocidade_simulacao}"
                )
            )

        if botao.grupo == "ferramenta":
            return (
                botao.identificador
                == self.ferramenta_atual
            )

        if (
            botao.identificador
            == "pausar"
        ):
            return self.pausado

        if (
            botao.identificador
            == "ajuda"
        ):
            return self.exibir_ajuda

        return False

    # ========================================================
    # ESTATÍSTICAS
    # ========================================================

    def desenhar_estatisticas(self) -> None:
        if self.mundo is None:
            return

        estatisticas = (
            self.mundo.obter_estatisticas()
        )

        x = (
            AREA_SIMULACAO_LARGURA
            + 14
        )

        y = 220

        largura = (
            LARGURA
            - AREA_SIMULACAO_LARGURA
            - 28
        )

        area = pygame.Rect(
            x,
            y,
            largura,
            108,
        )

        pygame.draw.rect(
            self.tela,
            COR_PAINEL_SECUNDARIO,
            area,
            border_radius=7,
        )

        indicadores = (
            (
                "Total",
                estatisticas[
                    "bacterias"
                ],
            ),
            (
                "Fotossintéticas",
                estatisticas[
                    "fotossinteticas"
                ],
            ),
            (
                "Predadoras",
                estatisticas[
                    "predadoras"
                ],
            ),
            (
                "Necrófagas",
                estatisticas[
                    "necrofagas"
                ],
            ),
            (
                "Carcaças",
                estatisticas[
                    "carcacas"
                ],
            ),
            (
                "Espécies",
                estatisticas[
                    "especies"
                ],
            ),
        )

        colunas = 3
        largura_coluna = (
            largura // colunas
        )

        for indice, (
            rotulo,
            valor,
        ) in enumerate(indicadores):
            coluna = (
                indice % colunas
            )

            linha = (
                indice // colunas
            )

            item_x = (
                area.left
                + coluna
                * largura_coluna
                + 9
            )

            item_y = (
                area.top
                + linha * 35
                + 7
            )

            texto_rotulo = (
                self.fonte_pequena.render(
                    rotulo,
                    True,
                    COR_TEXTO_SECUNDARIO,
                )
            )

            texto_valor = (
                self.fonte_media.render(
                    str(valor),
                    True,
                    BRANCO,
                )
            )

            self.tela.blit(
                texto_rotulo,
                (
                    item_x,
                    item_y,
                ),
            )

            self.tela.blit(
                texto_valor,
                (
                    item_x,
                    item_y + 14,
                ),
            )

        ciclo = str(
            estatisticas[
                "ciclo_luz"
            ]
        ).capitalize()

        luz = float(
            estatisticas[
                "intensidade_luz"
            ]
        )

        temperatura = float(
            estatisticas[
                "temperatura"
            ]
        )

        umidade = float(
            estatisticas[
                "umidade"
            ]
        )

        texto_ambiente = (
            f"{ciclo}  •  "
            f"Luz {luz:.0%}  •  "
            f"{temperatura:.1f} °C  •  "
            f"Umidade {umidade:.0%}"
        )

        texto = self.fonte_pequena.render(
            texto_ambiente,
            True,
            COR_TEXTO_DISCRETO,
        )

        self.tela.blit(
            texto,
            (
                area.left + 9,
                area.bottom - 18,
            ),
        )

    # ========================================================
    # GRÁFICO
    # ========================================================

    def desenhar_grafico(self) -> None:
        x = (
            AREA_SIMULACAO_LARGURA
            + 14
        )

        y = 356

        largura = (
            LARGURA
            - AREA_SIMULACAO_LARGURA
            - 28
        )

        area = pygame.Rect(
            x,
            y,
            largura,
            100,
        )

        self.desenhar_grafico_populacao(
            area
        )

        legenda_y = area.bottom + 7
        legenda_x = area.left

        legendas = (
            (
                "Foto",
                COR_GRAFICO_FOTOSSINTETICAS,
            ),
            (
                "Predadoras",
                COR_GRAFICO_PREDADORAS,
            ),
            (
                "Necrófagas",
                COR_GRAFICO_NECROFAGAS,
            ),
        )

        avancos = (
            75,
            112,
            0,
        )

        for indice, (
            nome,
            cor,
        ) in enumerate(legendas):
            pygame.draw.circle(
                self.tela,
                cor,
                (
                    legenda_x + 5,
                    legenda_y + 6,
                ),
                4,
            )

            texto = self.fonte_pequena.render(
                nome,
                True,
                COR_TEXTO_SECUNDARIO,
            )

            self.tela.blit(
                texto,
                (
                    legenda_x + 14,
                    legenda_y,
                ),
            )

            legenda_x += avancos[
                indice
            ]

    def desenhar_grafico_populacao(
        self,
        area: pygame.Rect,
    ) -> None:
        pygame.draw.rect(
            self.tela,
            COR_PAINEL_TERCIARIO,
            area,
            border_radius=6,
        )

        pygame.draw.rect(
            self.tela,
            COR_BORDA,
            area,
            width=1,
            border_radius=6,
        )

        for indice in range(
            1,
            4,
        ):
            linha_y = (
                area.top
                + indice
                * area.height
                // 4
            )

            pygame.draw.line(
                self.tela,
                COR_GRADE_GRAFICO,
                (
                    area.left + 1,
                    linha_y,
                ),
                (
                    area.right - 1,
                    linha_y,
                ),
                1,
            )

        historicos = (
            (
                self.historico_fotossinteticas,
                COR_GRAFICO_FOTOSSINTETICAS,
            ),
            (
                self.historico_predadoras,
                COR_GRAFICO_PREDADORAS,
            ),
            (
                self.historico_necrofagas,
                COR_GRAFICO_NECROFAGAS,
            ),
        )

        maior_valor = max(
            (
                max(
                    historico,
                    default=1,
                )
                for historico, _ in historicos
            ),
            default=1,
        )

        maior_valor = max(
            maior_valor,
            1,
        )

        for historico, cor in historicos:
            if len(historico) < 2:
                continue

            valores = list(
                historico
            )

            pontos: list[
                tuple[int, int]
            ] = []

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
                    valor
                    / maior_valor
                )

                ponto_x = (
                    area.left
                    + int(
                        proporcao_x
                        * (
                            area.width - 2
                        )
                    )
                )

                ponto_y = (
                    area.bottom
                    - 1
                    - int(
                        proporcao_y
                        * (
                            area.height - 2
                        )
                    )
                )

                pontos.append(
                    (
                        ponto_x,
                        ponto_y,
                    )
                )

            pygame.draw.lines(
                self.tela,
                cor,
                False,
                pontos,
                2,
            )

    # ========================================================
    # INSPEÇÃO E EVENTOS
    # ========================================================

    def desenhar_inspecao_ou_eventos(
        self,
    ) -> None:
        x = (
            AREA_SIMULACAO_LARGURA
            + 14
        )

        y = 486

        largura = (
            LARGURA
            - AREA_SIMULACAO_LARGURA
            - 28
        )

        altura = (
            ALTURA
            - y
            - 14
        )

        titulo = (
            "ORGANISMO SELECIONADO"
            if self.organismo_selecionado
            is not None
            else "EVENTOS RECENTES"
        )

        texto_titulo = (
            self.fonte_pequena.render(
                titulo,
                True,
                COR_TEXTO_SECUNDARIO,
            )
        )

        self.tela.blit(
            texto_titulo,
            (
                x,
                y,
            ),
        )

        area = pygame.Rect(
            x,
            y + 19,
            largura,
            altura - 19,
        )

        pygame.draw.rect(
            self.tela,
            COR_PAINEL_SECUNDARIO,
            area,
            border_radius=7,
        )

        if (
            self.organismo_selecionado
            is None
        ):
            self.desenhar_eventos(
                area
            )

        else:
            self.desenhar_dados_organismo(
                self.organismo_selecionado,
                area,
            )

    def desenhar_eventos(
        self,
        area: pygame.Rect,
    ) -> None:
        if self.mundo is None:
            return

        eventos = (
            self.mundo.obter_eventos(
                limite=6
            )
        )

        if not eventos:
            texto = self.fonte.render(
                "Nenhum evento registrado.",
                True,
                COR_TEXTO_SECUNDARIO,
            )

            self.tela.blit(
                texto,
                (
                    area.left + 12,
                    area.top + 14,
                ),
            )

            return

        y = area.top + 10

        for evento in eventos:
            tempo = evento.get(
                "tempo",
                0,
            )

            mensagem = str(
                evento.get(
                    "mensagem",
                    "",
                )
            )

            linhas = self.quebrar_texto(
                mensagem,
                limite=44,
            )

            texto_tempo = (
                self.fonte_pequena.render(
                    f"T{tempo}",
                    True,
                    COR_TEXTO_DISCRETO,
                )
            )

            self.tela.blit(
                texto_tempo,
                (
                    area.left + 10,
                    y,
                ),
            )

            texto_mensagem = (
                self.fonte_pequena.render(
                    linhas[0]
                    if linhas
                    else mensagem,
                    True,
                    BRANCO,
                )
            )

            self.tela.blit(
                texto_mensagem,
                (
                    area.left + 50,
                    y,
                ),
            )

            y += 26

            if (
                y + 20
                > area.bottom
            ):
                break

    def desenhar_dados_organismo(
        self,
        organismo: Bacteria | Carcaca,
        area: pygame.Rect,
    ) -> None:
        if isinstance(
            organismo,
            Bacteria,
        ):
            self.desenhar_dados_bacteria(
                organismo,
                area,
            )

        else:
            self.desenhar_dados_carcaca(
                organismo,
                area,
            )

    def desenhar_dados_bacteria(
        self,
        bacteria: Bacteria,
        area: pygame.Rect,
    ) -> None:
        cor_estrategia = (
            CORES_ESTRATEGIAS.get(
                bacteria.estrategia_alimentar,
                BRANCO,
            )
        )

        pygame.draw.circle(
            self.tela,
            bacteria.cor,
            (
                area.left + 18,
                area.top + 18,
            ),
            8,
        )

        pygame.draw.circle(
            self.tela,
            cor_estrategia,
            (
                area.left + 18,
                area.top + 18,
            ),
            10,
            2,
        )

        estrategia_nome = (
            NOMES_ESTRATEGIAS.get(
                bacteria.estrategia_alimentar,
                bacteria.estrategia_alimentar,
            )
        )

        titulo = self.fonte_media.render(
            estrategia_nome,
            True,
            BRANCO,
        )

        self.tela.blit(
            titulo,
            (
                area.left + 36,
                area.top + 7,
            ),
        )

        dados = (
            (
                "Espécie",
                bacteria.especie,
            ),
            (
                "Energia",
                f"{bacteria.energia:.1f}",
            ),
            (
                "Idade",
                (
                    f"{bacteria.idade}/"
                    f"{bacteria.esperanca_vida}"
                ),
            ),
            (
                "Geração",
                bacteria.geracao,
            ),
            (
                "Velocidade",
                f"{bacteria.velocidade:.2f}",
            ),
            (
                "Tamanho",
                bacteria.tamanho,
            ),
            (
                "Ataque",
                f"{bacteria.ataque:.2f}",
            ),
            (
                "Defesa",
                f"{bacteria.defesa:.2f}",
            ),
            (
                "Metabolismo",
                (
                    f"{bacteria.eficiencia_metabolica:.2f}"
                ),
            ),
            (
                "Mutação",
                (
                    f"{bacteria.taxa_mutacao:.1%}"
                ),
            ),
        )

        self.desenhar_grade_dados(
            dados=dados,
            area=area,
            inicio_y=area.top + 40,
        )

    def desenhar_dados_carcaca(
        self,
        carcaca: Carcaca,
        area: pygame.Rect,
    ) -> None:
        pygame.draw.circle(
            self.tela,
            carcaca.cor,
            (
                area.left + 18,
                area.top + 18,
            ),
            8,
        )

        titulo = self.fonte_media.render(
            "Carcaça",
            True,
            BRANCO,
        )

        self.tela.blit(
            titulo,
            (
                area.left + 36,
                area.top + 7,
            ),
        )

        estrategia_origem = (
            NOMES_ESTRATEGIAS.get(
                carcaca.origem_estrategia,
                carcaca.origem_estrategia
                or "-",
            )
        )

        dados = (
            (
                "Energia",
                f"{carcaca.energia:.1f}",
            ),
            (
                "Idade",
                carcaca.idade,
            ),
            (
                "Espécie origem",
                (
                    carcaca.origem_especie
                    or "-"
                ),
            ),
            (
                "Estratégia origem",
                estrategia_origem,
            ),
            (
                "Posição",
                (
                    f"{int(carcaca.x)}, "
                    f"{int(carcaca.y)}"
                ),
            ),
            (
                "Disponível",
                (
                    "Sim"
                    if carcaca.esta_disponivel()
                    else "Não"
                ),
            ),
        )

        self.desenhar_grade_dados(
            dados=dados,
            area=area,
            inicio_y=area.top + 40,
        )

    def desenhar_grade_dados(
        self,
        dados: tuple[
            tuple[str, Any],
            ...,
        ],
        area: pygame.Rect,
        inicio_y: int,
    ) -> None:
        coluna_esquerda = (
            area.left + 11
        )

        coluna_direita = (
            area.left
            + area.width // 2
            + 3
        )

        altura_linha = 31

        for indice, (
            rotulo,
            valor,
        ) in enumerate(dados):
            coluna = indice % 2
            linha = indice // 2

            x = (
                coluna_esquerda
                if coluna == 0
                else coluna_direita
            )

            y = (
                inicio_y
                + linha
                * altura_linha
            )

            if (
                y + altura_linha
                > area.bottom
            ):
                break

            texto_rotulo = (
                self.fonte_pequena.render(
                    str(rotulo),
                    True,
                    COR_TEXTO_SECUNDARIO,
                )
            )

            valor_limitado = str(
                valor
            )[:22]

            texto_valor = self.fonte.render(
                valor_limitado,
                True,
                BRANCO,
            )

            self.tela.blit(
                texto_rotulo,
                (
                    x,
                    y,
                ),
            )

            self.tela.blit(
                texto_valor,
                (
                    x,
                    y + 13,
                ),
            )

    # ========================================================
    # DESTAQUE DO ORGANISMO
    # ========================================================

    def desenhar_organismo_selecionado(
        self,
    ) -> None:
        organismo = (
            self.organismo_selecionado
        )

        if organismo is None:
            return

        x = int(
            organismo.x
        )

        y = int(
            organismo.y
        )

        tamanho = int(
            getattr(
                organismo,
                "tamanho",
                3,
            )
        )

        raio = max(
            12,
            tamanho + 8,
        )

        pygame.draw.circle(
            self.tela,
            COR_DESTAQUE_SELECAO,
            (
                x,
                y,
            ),
            raio,
            2,
        )

        if not isinstance(
            organismo,
            Bacteria,
        ):
            return

        comprimento = (
            raio + 12
        )

        destino_x = (
            x
            + int(
                math.cos(
                    organismo.direcao
                )
                * comprimento
            )
        )

        destino_y = (
            y
            + int(
                math.sin(
                    organismo.direcao
                )
                * comprimento
            )
        )

        pygame.draw.line(
            self.tela,
            COR_DESTAQUE_SELECAO,
            (
                x,
                y,
            ),
            (
                destino_x,
                destino_y,
            ),
            2,
        )

        superficie = pygame.Surface(
            (
                AREA_SIMULACAO_LARGURA,
                ALTURA,
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            superficie,
            (
                COR_DESTAQUE_SELECAO[0],
                COR_DESTAQUE_SELECAO[1],
                COR_DESTAQUE_SELECAO[2],
                45,
            ),
            (
                x,
                y,
            ),
            int(
                organismo.raio_deteccao
            ),
            1,
        )

        self.tela.blit(
            superficie,
            (
                0,
                0,
            ),
        )

        alvo = getattr(
            organismo,
            "alvo_atual",
            None,
        )

        if alvo is not None:
            pygame.draw.line(
                self.tela,
                (
                    255,
                    130,
                    80,
                ),
                (
                    x,
                    y,
                ),
                (
                    int(alvo.x),
                    int(alvo.y),
                ),
                1,
            )

    # ========================================================
    # MENSAGENS E PAUSA
    # ========================================================

    def desenhar_mensagem_temporaria(
        self,
    ) -> None:
        if not self.mensagem_temporaria:
            return

        texto = self.fonte.render(
            self.mensagem_temporaria,
            True,
            self.cor_mensagem_temporaria,
        )

        largura = min(
            texto.get_width() + 28,
            AREA_SIMULACAO_LARGURA - 28,
        )

        altura = 36

        area = pygame.Rect(
            14,
            ALTURA - altura - 14,
            largura,
            altura,
        )

        superficie = pygame.Surface(
            (
                area.width,
                area.height,
            ),
            pygame.SRCALPHA,
        )

        superficie.fill(
            (
                10,
                15,
                20,
                220,
            )
        )

        self.tela.blit(
            superficie,
            area.topleft,
        )

        pygame.draw.rect(
            self.tela,
            COR_BORDA,
            area,
            width=1,
            border_radius=6,
        )

        self.tela.blit(
            texto,
            (
                area.left + 14,
                area.top + 9,
            ),
        )

    def desenhar_indicador_pausa(
        self,
    ) -> None:
        texto = self.fonte_media.render(
            "PAUSADO",
            True,
            BRANCO,
        )

        largura = (
            texto.get_width()
            + 30
        )

        altura = 38

        area = pygame.Rect(
            (
                AREA_SIMULACAO_LARGURA
                - largura
                - 14
            ),
            14,
            largura,
            altura,
        )

        superficie = pygame.Surface(
            (
                largura,
                altura,
            ),
            pygame.SRCALPHA,
        )

        superficie.fill(
            (
                20,
                20,
                20,
                215,
            )
        )

        self.tela.blit(
            superficie,
            area.topleft,
        )

        pygame.draw.rect(
            self.tela,
            COR_DESTAQUE_SELECAO,
            area,
            width=2,
            border_radius=7,
        )

        texto_retangulo = (
            texto.get_rect(
                center=area.center
            )
        )

        self.tela.blit(
            texto,
            texto_retangulo,
        )

    # ========================================================
    # AJUDA
    # ========================================================

    def desenhar_ajuda(self) -> None:
        superficie_escura = pygame.Surface(
            (
                LARGURA,
                ALTURA,
            ),
            pygame.SRCALPHA,
        )

        superficie_escura.fill(
            (
                0,
                0,
                0,
                165,
            )
        )

        self.tela.blit(
            superficie_escura,
            (
                0,
                0,
            ),
        )

        largura_ajuda = 690
        altura_ajuda = 500

        x = (
            LARGURA
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
            (
                22,
                28,
                34,
            ),
            area,
            border_radius=10,
        )

        pygame.draw.rect(
            self.tela,
            (
                100,
                116,
                132,
            ),
            area,
            width=2,
            border_radius=10,
        )

        titulo = self.fonte_titulo.render(
            "Como usar o SimLife",
            True,
            BRANCO,
        )

        self.tela.blit(
            titulo,
            (
                x + 24,
                y + 20,
            ),
        )

        descricao = self.fonte.render(
            (
                "Todas as entidades vivas são bactérias. "
                "O metabolismo define sua estratégia ecológica."
            ),
            True,
            COR_TEXTO_SECUNDARIO,
        )

        self.tela.blit(
            descricao,
            (
                x + 24,
                y + 55,
            ),
        )

        comandos = (
            (
                "Inspecionar / I",
                (
                    "Clique em uma bactéria ou carcaça "
                    "para ver seus atributos."
                ),
            ),
            (
                "Fotossintética / F",
                (
                    "Adiciona uma bactéria que obtém "
                    "energia por fotossíntese."
                ),
            ),
            (
                "Predadora / P",
                (
                    "Adiciona uma bactéria que caça "
                    "outras bactérias."
                ),
            ),
            (
                "Necrófaga / N",
                (
                    "Adiciona uma bactéria que consome "
                    "carcaças."
                ),
            ),
            (
                "Espaço",
                "Pausa ou continua a simulação.",
            ),
            (
                "R",
                "Reinicia completamente o ecossistema.",
            ),
            (
                "1, 2, 3 e 4",
                (
                    "Altera a velocidade para "
                    "1x, 2x, 4x e 8x."
                ),
            ),
            (
                "Clique direito",
                "Inspeciona rapidamente uma entidade.",
            ),
            (
                "Esc",
                "Fecha a ajuda ou limpa a seleção.",
            ),
        )

        linha_y = (
            y + 100
        )

        for atalho, explicacao in comandos:
            texto_atalho = (
                self.fonte.render(
                    atalho,
                    True,
                    COR_DESTAQUE_SELECAO,
                )
            )

            texto_explicacao = (
                self.fonte.render(
                    explicacao,
                    True,
                    BRANCO,
                )
            )

            self.tela.blit(
                texto_atalho,
                (
                    x + 24,
                    linha_y,
                ),
            )

            self.tela.blit(
                texto_explicacao,
                (
                    x + 185,
                    linha_y,
                ),
            )

            linha_y += 37

        rodape = self.fonte_pequena.render(
            "Clique em qualquer lugar para fechar.",
            True,
            COR_TEXTO_SECUNDARIO,
        )

        rodape_retangulo = (
            rodape.get_rect(
                center=(
                    area.centerx,
                    area.bottom - 22,
                )
            )
        )

        self.tela.blit(
            rodape,
            rodape_retangulo,
        )

    # ========================================================
    # ERROS
    # ========================================================

    def desenhar_tela_de_erro(
        self,
        titulo: str,
        detalhe: str,
    ) -> None:
        self.tela.fill(
            (
                34,
                10,
                14,
            )
        )

        texto_titulo = (
            self.fonte_grande.render(
                titulo,
                True,
                BRANCO,
            )
        )

        self.tela.blit(
            texto_titulo,
            (
                35,
                35,
            ),
        )

        linhas = self.quebrar_texto(
            detalhe[:600],
            limite=88,
        )

        y = 105

        for linha in linhas:
            texto = self.fonte.render(
                linha,
                True,
                (
                    255,
                    180,
                    180,
                ),
            )

            self.tela.blit(
                texto,
                (
                    35,
                    y,
                ),
            )

            y += 25

        instrucao = self.fonte.render(
            (
                "Abra o Console do navegador para "
                "consultar o traceback completo."
            ),
            True,
            COR_TEXTO_SECUNDARIO,
        )

        self.tela.blit(
            instrucao,
            (
                35,
                y + 25,
            ),
        )

    @staticmethod
    def quebrar_texto(
        texto: str,
        limite: int,
    ) -> list[str]:
        palavras = texto.split()

        linhas: list[str] = []
        linha_atual = ""

        for palavra in palavras:
            candidato = (
                f"{linha_atual} {palavra}".strip()
            )

            if len(candidato) <= limite:
                linha_atual = candidato
                continue

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


# ============================================================
# ENTRADA
# ============================================================

async def main() -> None:
    aplicacao = Aplicacao()
    await aplicacao.executar()


if __name__ == "__main__":
    asyncio.run(main())
