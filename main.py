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
    CINZA_ESCURO,
    FPS,
    LARGURA,
    PRETO,
)
from mundo import Mundo


# ============================================================
# CORES DA INTERFACE
# ============================================================

COR_PAINEL = (25, 31, 38)
COR_PAINEL_SECUNDARIA = (34, 42, 51)

COR_BOTAO = (48, 58, 69)
COR_BOTAO_HOVER = (61, 73, 86)
COR_BOTAO_ATIVO = (34, 139, 94)
COR_BOTAO_BORDA = (88, 101, 114)

COR_TEXTO_SECUNDARIO = (175, 185, 195)
COR_DESTAQUE = (255, 215, 70)
COR_ERRO = (190, 55, 55)

COR_GRAFICO_BACTERIAS = (0, 255, 100)
COR_GRAFICO_ALGAS = (0, 160, 40)
COR_GRAFICO_PROTOZOARIOS = (255, 90, 90)


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
        return self.retangulo.collidepoint(posicao)


# ============================================================
# APLICAÇÃO
# ============================================================

class Aplicacao:
    """
    Controla a janela, os eventos, a interface e a renderização.

    A lógica ecológica continua centralizada em Mundo.
    """

    def __init__(self) -> None:
        pygame.init()

        self.tela = pygame.display.set_mode(
            (LARGURA, ALTURA)
        )

        pygame.display.set_caption(
            "SimLife — Evolução Microbiana"
        )

        self.relogio = pygame.time.Clock()

        # Fontes internas são mais seguras no WebAssembly.
        self.fonte_pequena = pygame.font.Font(
            None,
            18,
        )

        self.fonte = pygame.font.Font(
            None,
            21,
        )

        self.fonte_media = pygame.font.Font(
            None,
            24,
        )

        self.fonte_titulo = pygame.font.Font(
            None,
            30,
        )

        self.fonte_grande = pygame.font.Font(
            None,
            38,
        )

        # Inicializado após o primeiro frame para o Pygbag.
        self.mundo: Mundo | None = None

        self.rodando = True
        self.pausado = False
        self.exibir_ajuda = False

        self.velocidade_simulacao = 1
        self.frame = 0

        # Ferramentas disponíveis:
        # - inspecionar
        # - adicionar_alga
        # - adicionar_bacteria
        self.ferramenta_atual = "inspecionar"

        self.organismo_selecionado: Any | None = None

        self.mensagem_temporaria = ""
        self.tempo_mensagem_temporaria = 0

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
            "Inicializando SimLife..."
        )

        pygame.display.flip()

        # Libera o navegador antes da inicialização do mundo.
        await asyncio.sleep(0)

        try:
            self.mundo = Mundo()

        except Exception as erro:
            print("ERRO AO CRIAR O MUNDO:")
            print(repr(erro))

            await self.manter_tela_de_erro(
                titulo="Erro ao inicializar a simulação.",
                detalhe=repr(erro),
            )

            return

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
                    print("ERRO DURANTE A SIMULAÇÃO:")
                    print(repr(erro))

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
                self.relogio.tick(FPS)

            # Obrigatório para execução no Pygbag.
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
        Cria os botões clicáveis do painel lateral.
        """

        self.botoes.clear()

        painel_x = AREA_SIMULACAO_LARGURA
        margem = 16

        x = painel_x + margem
        largura_disponivel = (
            LARGURA
            - painel_x
            - margem * 2
        )

        # Linha principal.
        espacamento = 8
        largura_principal = (
            largura_disponivel - espacamento * 2
        ) // 3

        y = 52

        self.botoes.extend(
            [
                Botao(
                    identificador="pausar",
                    rotulo="Pausar",
                    retangulo=pygame.Rect(
                        x,
                        y,
                        largura_principal,
                        34,
                    ),
                    acao=self.alternar_pausa,
                ),
                Botao(
                    identificador="reiniciar",
                    rotulo="Reiniciar",
                    retangulo=pygame.Rect(
                        x
                        + largura_principal
                        + espacamento,
                        y,
                        largura_principal,
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
                            largura_principal
                            + espacamento
                        )
                        * 2,
                        y,
                        largura_principal,
                        34,
                    ),
                    acao=self.alternar_ajuda,
                ),
            ]
        )

        # Velocidades.
        y = 116

        largura_velocidade = (
            largura_disponivel - espacamento * 3
        ) // 4

        for indice, velocidade in enumerate(
            (1, 2, 4, 8)
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
                        31,
                    ),
                    acao=(
                        lambda valor=velocidade:
                        self.definir_velocidade(valor)
                    ),
                    grupo="velocidade",
                )
            )

        # Ferramentas.
        y = 178

        largura_ferramenta = (
            largura_disponivel - espacamento * 2
        ) // 3

        ferramentas = [
            (
                "inspecionar",
                "Inspecionar",
            ),
            (
                "adicionar_alga",
                "+ Alga",
            ),
            (
                "adicionar_bacteria",
                "+ Bactéria",
            ),
        ]

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
                        31,
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
                "Simulação pausada."
            )
        else:
            self.definir_mensagem(
                "Simulação retomada."
            )

    def alternar_ajuda(self) -> None:
        self.exibir_ajuda = (
            not self.exibir_ajuda
        )

    def definir_velocidade(
        self,
        velocidade: int,
    ) -> None:
        self.velocidade_simulacao = velocidade

        self.definir_mensagem(
            f"Velocidade alterada para {velocidade}x."
        )

    def definir_ferramenta(
        self,
        ferramenta: str,
    ) -> None:
        self.ferramenta_atual = ferramenta

        mensagens = {
            "inspecionar": (
                "Clique em um organismo para inspecioná-lo."
            ),
            "adicionar_alga": (
                "Clique na simulação para adicionar uma alga."
            ),
            "adicionar_bacteria": (
                "Clique na simulação para adicionar uma bactéria."
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
                    int(evento.x * LARGURA),
                    int(evento.y * ALTURA),
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
            else:
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

        elif tecla == pygame.K_a:
            self.definir_ferramenta(
                "adicionar_alga"
            )

        elif tecla == pygame.K_b:
            self.definir_ferramenta(
                "adicionar_bacteria"
            )

        elif tecla in (
            pygame.K_PLUS,
            pygame.K_KP_PLUS,
            pygame.K_EQUALS,
        ):
            velocidades = [
                1,
                2,
                4,
                8,
            ]

            atual = (
                self.velocidade_simulacao
            )

            proxima = next(
                (
                    valor
                    for valor in velocidades
                    if valor > atual
                ),
                8,
            )

            self.definir_velocidade(
                proxima
            )

        elif tecla in (
            pygame.K_MINUS,
            pygame.K_KP_MINUS,
        ):
            velocidades = [
                8,
                4,
                2,
                1,
            ]

            atual = (
                self.velocidade_simulacao
            )

            proxima = next(
                (
                    valor
                    for valor in velocidades
                    if valor < atual
                ),
                1,
            )

            self.definir_velocidade(
                proxima
            )

        elif tecla == pygame.K_1:
            self.definir_velocidade(1)

        elif tecla == pygame.K_2:
            self.definir_velocidade(2)

        elif tecla == pygame.K_3:
            self.definir_velocidade(4)

        elif tecla == pygame.K_4:
            self.definir_velocidade(8)

    def processar_clique(
        self,
        posicao: tuple[int, int],
        botao_mouse: int,
    ) -> None:
        """
        Processa cliques nos controles ou na simulação.
        """

        if self.exibir_ajuda:
            self.exibir_ajuda = False
            return

        # Primeiro tenta acionar um botão do painel.
        for botao in self.botoes:
            if botao.contem(posicao):
                botao.acao()
                return

        if not self.posicao_dentro_da_simulacao(
            posicao
        ):
            return

        if self.mundo is None:
            return

        x, y = posicao

        # Clique direito mantém o atalho tradicional.
        if botao_mouse == 3:
            adicionado = (
                self.mundo.adicionar_bacteria_na_posicao(
                    x,
                    y,
                )
            )

            self.informar_resultado_adicao(
                adicionado=adicionado,
                nome="Bactéria",
            )

            return

        if self.ferramenta_atual == "adicionar_alga":
            adicionado = (
                self.mundo.adicionar_alga_na_posicao(
                    x,
                    y,
                )
            )

            self.informar_resultado_adicao(
                adicionado=adicionado,
                nome="Alga",
            )

            return

        if (
            self.ferramenta_atual
            == "adicionar_bacteria"
        ):
            adicionado = (
                self.mundo.adicionar_bacteria_na_posicao(
                    x,
                    y,
                )
            )

            self.informar_resultado_adicao(
                adicionado=adicionado,
                nome="Bactéria",
            )

            return

        self.selecionar_organismo(
            x,
            y,
        )

    def informar_resultado_adicao(
        self,
        adicionado: bool,
        nome: str,
    ) -> None:
        if adicionado:
            self.definir_mensagem(
                f"{nome} adicionada com sucesso."
            )
        else:
            self.definir_mensagem(
                f"Limite de {nome.lower()}s atingido."
            )

    def posicao_dentro_da_simulacao(
        self,
        posicao: tuple[int, int],
    ) -> bool:
        x, y = posicao

        return (
            0 <= x < AREA_SIMULACAO_LARGURA
            and 0 <= y < ALTURA
        )

    # ========================================================
    # SELEÇÃO E INSPEÇÃO
    # ========================================================

    def selecionar_organismo(
        self,
        x: float,
        y: float,
    ) -> None:
        """
        Seleciona o organismo mais próximo do clique.
        """

        if self.mundo is None:
            return

        organismos = (
            list(self.mundo.bacterias)
            + list(self.mundo.protozoarios)
            + list(self.mundo.algas)
            + list(self.mundo.carcacas)
        )

        melhor_organismo = None
        menor_distancia = float("inf")

        for organismo in organismos:
            dx = organismo.x - x
            dy = organismo.y - y

            distancia = math.sqrt(
                dx * dx + dy * dy
            )

            raio_selecao = max(
                12.0,
                float(
                    getattr(
                        organismo,
                        "tamanho",
                        3,
                    )
                )
                + 8.0,
            )

            if (
                distancia <= raio_selecao
                and distancia < menor_distancia
            ):
                melhor_organismo = organismo
                menor_distancia = distancia

        self.organismo_selecionado = (
            melhor_organismo
        )

        if melhor_organismo is None:
            self.definir_mensagem(
                "Nenhum organismo encontrado."
            )
        else:
            nome = self.obter_nome_organismo(
                melhor_organismo
            )

            self.definir_mensagem(
                f"{nome} selecionado."
            )

    def validar_selecao(self) -> None:
        """
        Remove a seleção quando o organismo deixa de existir.
        """

        if (
            self.organismo_selecionado is None
            or self.mundo is None
        ):
            return

        organismo = self.organismo_selecionado

        organismos_ativos = (
            list(self.mundo.bacterias)
            + list(self.mundo.algas)
            + list(self.mundo.protozoarios)
            + list(self.mundo.carcacas)
        )

        if organismo not in organismos_ativos:
            self.organismo_selecionado = None

            self.definir_mensagem(
                "O organismo selecionado deixou de existir."
            )

    @staticmethod
    def obter_nome_organismo(
        organismo: Any,
    ) -> str:
        nomes = {
            "Bacteria": "Bactéria",
            "Alga": "Alga",
            "Protozoario": "Protozoário",
            "Carcaca": "Carcaça",
        }

        return nomes.get(
            organismo.__class__.__name__,
            organismo.__class__.__name__,
        )

    # ========================================================
    # CONTROLE DO MUNDO
    # ========================================================

    def reiniciar(self) -> None:
        """
        Recria completamente o mundo da simulação.
        """

        try:
            self.mundo = Mundo()

        except Exception as erro:
            print("ERRO AO REINICIAR O MUNDO:")
            print(repr(erro))

            self.definir_mensagem(
                "Não foi possível reiniciar."
            )

            return

        self.frame = 0
        self.pausado = False
        self.organismo_selecionado = None

        self.historico_bacterias.clear()
        self.historico_algas.clear()
        self.historico_protozoarios.clear()

        self.definir_mensagem(
            "Simulação reiniciada."
        )

    def registrar_historico(self) -> None:
        """
        Registra populações para o gráfico lateral.
        """

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

    # ========================================================
    # MENSAGENS
    # ========================================================

    def definir_mensagem(
        self,
        mensagem: str,
        duracao_frames: int = 100,
    ) -> None:
        self.mensagem_temporaria = mensagem
        self.tempo_mensagem_temporaria = (
            duracao_frames
        )

    def atualizar_mensagem_temporaria(
        self,
    ) -> None:
        if self.tempo_mensagem_temporaria <= 0:
            self.mensagem_temporaria = ""
            return

        self.tempo_mensagem_temporaria -= 1

    # ========================================================
    # RENDERIZAÇÃO PRINCIPAL
    # ========================================================

    def desenhar(self) -> None:
        """
        Desenha todos os elementos da interface.
        """

        self.tela.fill(PRETO)

        if self.mundo is None:
            self.desenhar_tela_inicial(
                "Inicializando SimLife..."
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
            (8, 18, 24)
        )

        titulo = self.fonte_grande.render(
            "SimLife",
            True,
            BRANCO,
        )

        titulo_rect = titulo.get_rect(
            center=(
                LARGURA // 2,
                ALTURA // 2 - 30,
            )
        )

        self.tela.blit(
            titulo,
            titulo_rect,
        )

        texto = self.fonte_media.render(
            mensagem,
            True,
            COR_TEXTO_SECUNDARIO,
        )

        texto_rect = texto.get_rect(
            center=(
                LARGURA // 2,
                ALTURA // 2 + 20,
            )
        )

        self.tela.blit(
            texto,
            texto_rect,
        )

    def desenhar_separador(self) -> None:
        pygame.draw.line(
            self.tela,
            (80, 94, 108),
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
            LARGURA - AREA_SIMULACAO_LARGURA,
            ALTURA,
        )

        pygame.draw.rect(
            self.tela,
            COR_PAINEL,
            painel,
        )

        painel_x = AREA_SIMULACAO_LARGURA
        margem = 16
        x = painel_x + margem

        titulo = self.fonte_titulo.render(
            "SimLife",
            True,
            BRANCO,
        )

        self.tela.blit(
            titulo,
            (x, 14),
        )

        subtitulo = self.fonte_pequena.render(
            "Ecossistema microbiano evolutivo",
            True,
            COR_TEXTO_SECUNDARIO,
        )

        subtitulo_x = (
            LARGURA
            - margem
            - subtitulo.get_width()
        )

        self.tela.blit(
            subtitulo,
            (
                subtitulo_x,
                22,
            ),
        )

        self.desenhar_botoes()
        self.desenhar_rotulos_secoes()
        self.desenhar_estatisticas()
        self.desenhar_grafico()
        self.desenhar_inspecao()

    def desenhar_rotulos_secoes(self) -> None:
        x = AREA_SIMULACAO_LARGURA + 16

        secoes = [
            (
                "VELOCIDADE",
                96,
            ),
            (
                "FERRAMENTAS",
                158,
            ),
            (
                "ECOSSISTEMA",
                226,
            ),
        ]

        for titulo, y in secoes:
            texto = self.fonte_pequena.render(
                titulo,
                True,
                COR_TEXTO_SECUNDARIO,
            )

            self.tela.blit(
                texto,
                (x, y),
            )

    def desenhar_botoes(self) -> None:
        posicao_mouse = pygame.mouse.get_pos()

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

            if botao.identificador == "pausar":
                if self.pausado:
                    rotulo = "Continuar"
                else:
                    rotulo = "Pausar"

            texto = self.fonte.render(
                rotulo,
                True,
                BRANCO,
            )

            texto_rect = texto.get_rect(
                center=botao.retangulo.center
            )

            self.tela.blit(
                texto,
                texto_rect,
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

        if botao.identificador == "pausar":
            return self.pausado

        if botao.identificador == "ajuda":
            return self.exibir_ajuda

        return False

    # ========================================================
    # ESTATÍSTICAS
    # ========================================================

    def desenhar_estatisticas(self) -> None:
        if self.mundo is None:
            return

        painel_x = AREA_SIMULACAO_LARGURA
        margem = 16

        x = painel_x + margem
        y = 246

        largura = (
            LARGURA
            - painel_x
            - margem * 2
        )

        area = pygame.Rect(
            x,
            y,
            largura,
            96,
        )

        pygame.draw.rect(
            self.tela,
            COR_PAINEL_SECUNDARIA,
            area,
            border_radius=7,
        )

        estatisticas = (
            self.mundo.obter_estatisticas()
        )

        indicadores = [
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
                "Espécies",
                estatisticas["especies"],
            ),
            (
                "Carcaças",
                estatisticas["carcacas"],
            ),
            (
                "Ciclo",
                estatisticas[
                    "ciclo_luz"
                ].capitalize(),
            ),
        ]

        colunas = 3
        largura_coluna = largura // colunas

        for indice, (
            rotulo,
            valor,
        ) in enumerate(indicadores):
            coluna = indice % colunas
            linha = indice // colunas

            item_x = (
                x
                + coluna * largura_coluna
                + 10
            )

            item_y = (
                y
                + linha * 43
                + 10
            )

            texto_rotulo = (
                self.fonte_pequena.render(
                    rotulo,
                    True,
                    COR_TEXTO_SECUNDARIO,
                )
            )

            texto_valor = self.fonte_media.render(
                str(valor),
                True,
                BRANCO,
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
                    item_y + 15,
                ),
            )

    # ========================================================
    # GRÁFICO
    # ========================================================

    def desenhar_grafico(self) -> None:
        painel_x = AREA_SIMULACAO_LARGURA
        margem = 16

        x = painel_x + margem
        y = 354

        largura = (
            LARGURA
            - painel_x
            - margem * 2
        )

        titulo = self.fonte_pequena.render(
            "HISTÓRICO POPULACIONAL",
            True,
            COR_TEXTO_SECUNDARIO,
        )

        self.tela.blit(
            titulo,
            (x, y),
        )

        area = pygame.Rect(
            x,
            y + 20,
            largura,
            126,
        )

        self.desenhar_grafico_populacao(
            area
        )

        legenda_y = area.bottom + 5

        legendas = [
            (
                "Bactérias",
                COR_GRAFICO_BACTERIAS,
            ),
            (
                "Algas",
                COR_GRAFICO_ALGAS,
            ),
            (
                "Protozoários",
                COR_GRAFICO_PROTOZOARIOS,
            ),
        ]

        legenda_x = x

        for nome, cor in legendas:
            pygame.draw.circle(
                self.tela,
                cor,
                (
                    legenda_x + 5,
                    legenda_y + 7,
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

            legenda_x += 105

    def desenhar_grafico_populacao(
        self,
        area: pygame.Rect,
    ) -> None:
        pygame.draw.rect(
            self.tela,
            (17, 22, 28),
            area,
            border_radius=6,
        )

        pygame.draw.rect(
            self.tela,
            (65, 76, 88),
            area,
            width=1,
            border_radius=6,
        )

        # Linhas horizontais de referência.
        for indice in range(1, 4):
            y = (
                area.top
                + indice * area.height // 4
            )

            pygame.draw.line(
                self.tela,
                (40, 49, 58),
                (
                    area.left + 1,
                    y,
                ),
                (
                    area.right - 1,
                    y,
                ),
                1,
            )

        historicos = [
            (
                self.historico_bacterias,
                COR_GRAFICO_BACTERIAS,
            ),
            (
                self.historico_algas,
                COR_GRAFICO_ALGAS,
            ),
            (
                self.historico_protozoarios,
                COR_GRAFICO_PROTOZOARIOS,
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

            pygame.draw.lines(
                self.tela,
                cor,
                False,
                pontos,
                2,
            )

    # ========================================================
    # INSPEÇÃO
    # ========================================================

    def desenhar_inspecao(self) -> None:
        painel_x = AREA_SIMULACAO_LARGURA
        margem = 16

        x = painel_x + margem
        y = 518

        largura = (
            LARGURA
            - painel_x
            - margem * 2
        )

        titulo = self.fonte_pequena.render(
            "ORGANISMO SELECIONADO",
            True,
            COR_TEXTO_SECUNDARIO,
        )

        self.tela.blit(
            titulo,
            (x, y),
        )

        area = pygame.Rect(
            x,
            y + 20,
            largura,
            max(
                100,
                ALTURA - y - 36,
            ),
        )

        pygame.draw.rect(
            self.tela,
            COR_PAINEL_SECUNDARIA,
            area,
            border_radius=7,
        )

        organismo = self.organismo_selecionado

        if organismo is None:
            mensagem = self.fonte.render(
                "Use a ferramenta Inspecionar",
                True,
                COR_TEXTO_SECUNDARIO,
            )

            mensagem_2 = self.fonte_pequena.render(
                "e clique em um organismo.",
                True,
                COR_TEXTO_SECUNDARIO,
            )

            self.tela.blit(
                mensagem,
                (
                    area.left + 12,
                    area.top + 18,
                ),
            )

            self.tela.blit(
                mensagem_2,
                (
                    area.left + 12,
                    area.top + 43,
                ),
            )

            return

        self.desenhar_dados_organismo(
            organismo,
            area,
        )

    def desenhar_dados_organismo(
        self,
        organismo: Any,
        area: pygame.Rect,
    ) -> None:
        nome = self.obter_nome_organismo(
            organismo
        )

        cor = getattr(
            organismo,
            "cor",
            BRANCO,
        )

        pygame.draw.circle(
            self.tela,
            cor,
            (
                area.left + 18,
                area.top + 19,
            ),
            7,
        )

        titulo = self.fonte_media.render(
            nome,
            True,
            BRANCO,
        )

        self.tela.blit(
            titulo,
            (
                area.left + 34,
                area.top + 8,
            ),
        )

        energia = float(
            getattr(
                organismo,
                "energia",
                0.0,
            )
        )

        dados: list[
            tuple[str, str]
        ] = [
            (
                "Energia",
                f"{energia:.1f}",
            ),
            (
                "Posição",
                (
                    f"{int(organismo.x)}, "
                    f"{int(organismo.y)}"
                ),
            ),
            (
                "Tamanho",
                str(
                    getattr(
                        organismo,
                        "tamanho",
                        "-",
                    )
                ),
            ),
        ]

        classe = (
            organismo.__class__.__name__
        )

        if classe == "Bacteria":
            dados.extend(
                [
                    (
                        "Espécie",
                        str(
                            getattr(
                                organismo,
                                "especie",
                                "-",
                            )
                        ),
                    ),
                    (
                        "Alimentação",
                        str(
                            getattr(
                                organismo,
                                "presa",
                                "-",
                            )
                        ),
                    ),
                    (
                        "Idade",
                        (
                            f"{getattr(organismo, 'idade', 0)}"
                            "/"
                            f"{getattr(organismo, 'esperanca_vida', '-')}"
                        ),
                    ),
                    (
                        "Velocidade",
                        self.formatar_numero(
                            getattr(
                                organismo,
                                "velocidade",
                                0,
                            )
                        ),
                    ),
                    (
                        "Ataque",
                        self.formatar_numero(
                            getattr(
                                organismo,
                                "ataque",
                                0,
                            )
                        ),
                    ),
                    (
                        "Defesa",
                        self.formatar_numero(
                            getattr(
                                organismo,
                                "defesa",
                                0,
                            )
                        ),
                    ),
                    (
                        "Mutação",
                        self.formatar_percentual(
                            getattr(
                                organismo,
                                "taxa_mutacao",
                                0,
                            )
                        ),
                    ),
                ]
            )

        elif classe == "Protozoario":
            dados.extend(
                [
                    (
                        "Idade",
                        str(
                            getattr(
                                organismo,
                                "idade",
                                "-",
                            )
                        ),
                    ),
                    (
                        "Velocidade",
                        self.formatar_numero(
                            getattr(
                                organismo,
                                "velocidade",
                                0,
                            )
                        ),
                    ),
                ]
            )

        coluna_esquerda_x = (
            area.left + 12
        )

        coluna_direita_x = (
            area.left
            + area.width // 2
            + 4
        )

        inicio_y = area.top + 42
        altura_linha = 27

        for indice, (
            rotulo,
            valor,
        ) in enumerate(dados):
            coluna = indice % 2
            linha = indice // 2

            item_x = (
                coluna_esquerda_x
                if coluna == 0
                else coluna_direita_x
            )

            item_y = (
                inicio_y
                + linha * altura_linha
            )

            if (
                item_y
                + altura_linha
                > area.bottom
            ):
                break

            texto_rotulo = (
                self.fonte_pequena.render(
                    rotulo,
                    True,
                    COR_TEXTO_SECUNDARIO,
                )
            )

            valor_limitado = (
                str(valor)[:22]
            )

            texto_valor = self.fonte.render(
                valor_limitado,
                True,
                BRANCO,
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
                    item_y + 12,
                ),
            )

    @staticmethod
    def formatar_numero(
        valor: Any,
    ) -> str:
        try:
            return f"{float(valor):.2f}"
        except (
            TypeError,
            ValueError,
        ):
            return str(valor)

    @staticmethod
    def formatar_percentual(
        valor: Any,
    ) -> str:
        try:
            return f"{float(valor) * 100:.1f}%"
        except (
            TypeError,
            ValueError,
        ):
            return str(valor)

    def desenhar_organismo_selecionado(
        self,
    ) -> None:
        organismo = self.organismo_selecionado

        if organismo is None:
            return

        x = int(organismo.x)
        y = int(organismo.y)

        tamanho = int(
            getattr(
                organismo,
                "tamanho",
                3,
            )
        )

        raio = max(
            11,
            tamanho + 7,
        )

        pygame.draw.circle(
            self.tela,
            COR_DESTAQUE,
            (
                x,
                y,
            ),
            raio,
            2,
        )

        direcao = getattr(
            organismo,
            "direcao",
            None,
        )

        if direcao is not None:
            comprimento = raio + 10

            destino_x = (
                x
                + int(
                    math.cos(direcao)
                    * comprimento
                )
            )

            destino_y = (
                y
                + int(
                    math.sin(direcao)
                    * comprimento
                )
            )

            pygame.draw.line(
                self.tela,
                COR_DESTAQUE,
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

        raio_deteccao = getattr(
            organismo,
            "raio_deteccao",
            None,
        )

        if raio_deteccao is not None:
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
                    COR_DESTAQUE[0],
                    COR_DESTAQUE[1],
                    COR_DESTAQUE[2],
                    45,
                ),
                (
                    x,
                    y,
                ),
                int(raio_deteccao),
                1,
            )

            self.tela.blit(
                superficie,
                (0, 0),
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
            BRANCO,
        )

        largura = texto.get_width() + 28
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
            (10, 15, 20, 210)
        )

        self.tela.blit(
            superficie,
            area.topleft,
        )

        pygame.draw.rect(
            self.tela,
            (80, 95, 110),
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

        largura = texto.get_width() + 30
        altura = 38

        area = pygame.Rect(
            AREA_SIMULACAO_LARGURA
            - largura
            - 14,
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
            (20, 20, 20, 210)
        )

        self.tela.blit(
            superficie,
            area.topleft,
        )

        pygame.draw.rect(
            self.tela,
            COR_DESTAQUE,
            area,
            width=2,
            border_radius=7,
        )

        texto_rect = texto.get_rect(
            center=area.center
        )

        self.tela.blit(
            texto,
            texto_rect,
        )

    # ========================================================
    # AJUDA
    # ========================================================

    def desenhar_ajuda(self) -> None:
        largura_ajuda = min(
            620,
            AREA_SIMULACAO_LARGURA - 60,
        )

        altura_ajuda = min(
            470,
            ALTURA - 60,
        )

        x = (
            AREA_SIMULACAO_LARGURA
            - largura_ajuda
        ) // 2

        y = (
            ALTURA
            - altura_ajuda
        ) // 2

        sombra = pygame.Surface(
            (
                AREA_SIMULACAO_LARGURA,
                ALTURA,
            ),
            pygame.SRCALPHA,
        )

        sombra.fill(
            (0, 0, 0, 145)
        )

        self.tela.blit(
            sombra,
            (0, 0),
        )

        area = pygame.Rect(
            x,
            y,
            largura_ajuda,
            altura_ajuda,
        )

        pygame.draw.rect(
            self.tela,
            (22, 28, 34),
            area,
            border_radius=10,
        )

        pygame.draw.rect(
            self.tela,
            (100, 116, 132),
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

        descricao = (
            "Observe, interfira e acompanhe a evolução "
            "do ecossistema microbiano."
        )

        texto_descricao = (
            self.fonte.render(
                descricao,
                True,
                COR_TEXTO_SECUNDARIO,
            )
        )

        self.tela.blit(
            texto_descricao,
            (
                x + 24,
                y + 54,
            ),
        )

        comandos = [
            (
                "Inspecionar",
                "Clique em um organismo para visualizar seus atributos.",
            ),
            (
                "+ Alga",
                "Selecione a ferramenta e clique na área da simulação.",
            ),
            (
                "+ Bactéria",
                "Adiciona uma nova bactéria herbívora.",
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
                "Altera a velocidade para 1x, 2x, 4x e 8x.",
            ),
            (
                "I, A e B",
                "Seleciona inspeção, alga ou bactéria.",
            ),
            (
                "Clique direito",
                "Adiciona rapidamente uma bactéria.",
            ),
            (
                "Esc",
                "Fecha esta ajuda ou limpa a seleção.",
            ),
        ]

        linha_y = y + 95

        for atalho, explicacao in comandos:
            texto_atalho = (
                self.fonte.render(
                    atalho,
                    True,
                    COR_DESTAQUE,
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
                    x + 155,
                    linha_y,
                ),
            )

            linha_y += 34

        rodape = self.fonte_pequena.render(
            "Clique em qualquer lugar para fechar.",
            True,
            COR_TEXTO_SECUNDARIO,
        )

        rodape_rect = rodape.get_rect(
            center=(
                area.centerx,
                area.bottom - 22,
            )
        )

        self.tela.blit(
            rodape,
            rodape_rect,
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
            (34, 10, 14)
        )

        texto_titulo = self.fonte_grande.render(
            titulo,
            True,
            BRANCO,
        )

        self.tela.blit(
            texto_titulo,
            (
                35,
                35,
            ),
        )

        linhas = self.quebrar_texto(
            detalhe[:500],
            limite=85,
        )

        y = 100

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
