# mundo.py
from __future__ import annotations

import random
from collections import Counter, deque
from typing import Any, Iterable

import pygame

from ambiente import Ambiente
from configuracoes import (
    ALTURA,
    AREA_SIMULACAO_LARGURA,
    BACTERIAS_FOTOSSINTETICAS_INICIAIS,
    BACTERIAS_NECROFAGAS_INICIAIS,
    BACTERIAS_PREDADORAS_INICIAIS,
    CONSUMO_NUTRIENTES_FOTOSSINTESE,
    DURACAO_CICLO,
    DURACAO_ESTACAO,
    ENERGIA_INICIAL_CARCACA,
    ESTRATEGIA_FOTOSSINTESE,
    ESTRATEGIA_NECROFAGIA,
    ESTRATEGIA_PREDACAO,
    ESTRATEGIAS_ALIMENTARES,
    FUNDO_DIA,
    FUNDO_NOITE,
    MAX_BACTERIAS,
    MAX_CARCACAS,
    MAX_EVENTOS_REGISTRADOS,
    NOMES_ESTRATEGIAS,
    QUADTREE_CAPACIDADE,
    QUADTREE_PROFUNDIDADE_MAXIMA,
    RAIO_DISTRIBUICAO_NUTRIENTES,
    RETORNO_NUTRIENTES_DECOMPOSICAO,
    TEMPERATURA_MEDIA,
    UMIDADE_MEDIA,
)
from organismos import (
    Bacteria,
    Carcaca,
    cores_especies,
)
from quadtree import Quadtree


class Mundo:
    """
    Gerencia o ecossistema bacteriano completo.

    Todas as entidades vivas são bactérias. A diferença ecológica está
    na estratégia alimentar:

    - fotossíntese;
    - predação;
    - necrofagia.

    Carcaças são recursos orgânicos sem vida.
    """

    def __init__(
        self,
        *,
        semente: int | None = None,
    ) -> None:
        self.semente = semente
        self.gerador = random.Random(
            semente
        )

        self.tempo = 0

        self.ambiente = Ambiente(
            duracao_ciclo=DURACAO_CICLO,
            duracao_estacao=DURACAO_ESTACAO,
            temperatura_media=TEMPERATURA_MEDIA,
            umidade_media=UMIDADE_MEDIA,
            semente=semente,
        )

        self.bacterias: list[
            Bacteria
        ] = []

        self.carcacas: list[
            Carcaca
        ] = []

        self.quadtree = (
            self.criar_quadtree()
        )

        self.eventos: deque[
            dict[str, Any]
        ] = deque(
            maxlen=MAX_EVENTOS_REGISTRADOS
        )

        self.especies_conhecidas: set[
            str
        ] = set()

        self.nascimentos = 0
        self.mortes = 0
        self.predacoes = 0
        self.carcacas_consumidas = 0

        self.inicializar_populacoes()
        self.reconstruir_quadtree()

        self.registrar_evento(
            "inicio",
            (
                "Ecossistema iniciado com "
                f"{len(self.bacterias)} bactérias."
            ),
        )

    # ========================================================
    # COMPATIBILIDADE TEMPORÁRIA
    # ========================================================

    @property
    def ciclo_luz(self) -> str:
        """
        Mantém compatibilidade com versões anteriores da interface.
        """

        return self.ambiente.ciclo_luz()

    @property
    def algas(
        self,
    ) -> list[Bacteria]:
        """
        Compatibilidade temporária.

        Antigas algas agora são bactérias fotossintéticas.
        """

        return (
            self.obter_bacterias_por_estrategia(
                ESTRATEGIA_FOTOSSINTESE
            )
        )

    @property
    def protozoarios(
        self,
    ) -> list[Bacteria]:
        """
        Compatibilidade temporária.

        Antigos protozoários agora são bactérias predadoras.
        """

        return (
            self.obter_bacterias_por_estrategia(
                ESTRATEGIA_PREDACAO
            )
        )

    # ========================================================
    # INICIALIZAÇÃO
    # ========================================================

    def inicializar_populacoes(
        self,
    ) -> None:
        """
        Cria as populações iniciais das três estratégias.
        """

        configuracoes = (
            (
                ESTRATEGIA_FOTOSSINTESE,
                BACTERIAS_FOTOSSINTETICAS_INICIAIS,
            ),
            (
                ESTRATEGIA_PREDACAO,
                BACTERIAS_PREDADORAS_INICIAIS,
            ),
            (
                ESTRATEGIA_NECROFAGIA,
                BACTERIAS_NECROFAGAS_INICIAIS,
            ),
        )

        for (
            estrategia,
            quantidade,
        ) in configuracoes:
            for _ in range(
                quantidade
            ):
                if (
                    len(self.bacterias)
                    >= MAX_BACTERIAS
                ):
                    return

                bacteria = Bacteria(
                    x=self.gerador.uniform(
                        0,
                        AREA_SIMULACAO_LARGURA
                        - 1,
                    ),
                    y=self.gerador.uniform(
                        0,
                        ALTURA - 1,
                    ),
                    estrategia_alimentar=(
                        estrategia
                    ),
                )

                self.adicionar_bacteria(
                    bacteria,
                    registrar_nascimento=False,
                )

    # ========================================================
    # QUADTREE
    # ========================================================

    def criar_quadtree(
        self,
    ) -> Quadtree:
        """
        Cria a estrutura espacial usada nas buscas de proximidade.
        """

        return Quadtree(
            (
                0.0,
                0.0,
                float(
                    AREA_SIMULACAO_LARGURA
                ),
                float(
                    ALTURA
                ),
            ),
            capacity=QUADTREE_CAPACIDADE,
            max_depth=(
                QUADTREE_PROFUNDIDADE_MAXIMA
            ),
        )

    def reconstruir_quadtree(
        self,
    ) -> None:
        """
        Reconstrói a árvore com as posições atuais.
        """

        self.quadtree = (
            self.criar_quadtree()
        )

        for bacteria in self.bacterias:
            if bacteria.esta_viva():
                self.quadtree.insert(
                    bacteria
                )

        for carcaca in self.carcacas:
            if carcaca.esta_disponivel():
                self.quadtree.insert(
                    carcaca
                )

    # ========================================================
    # ATUALIZAÇÃO PRINCIPAL
    # ========================================================

    def atualizar(
        self,
    ) -> None:
        """
        Executa um passo completo da simulação.
        """

        self.tempo += 1

        self.ambiente.atualizar()

        self.reconstruir_quadtree()
        self.atualizar_bacterias()
        self.atualizar_carcacas()
        self.garantir_limites_populacionais()

    def atualizar_bacterias(
        self,
    ) -> None:
        """
        Atualiza todas as bactérias sem modificar a lista durante
        a iteração.
        """

        bacterias_inicio = tuple(
            self.bacterias
        )

        mortes_registradas: dict[
            int,
            Bacteria,
        ] = {}

        novos_individuos: list[
            Bacteria
        ] = []

        vagas_disponiveis = max(
            0,
            MAX_BACTERIAS
            - len(
                bacterias_inicio
            ),
        )

        for bacteria in bacterias_inicio:
            if (
                id(bacteria)
                in mortes_registradas
            ):
                continue

            if not bacteria.esta_viva():
                mortes_registradas[
                    id(bacteria)
                ] = bacteria

                continue

            self.atualizar_bacteria_individual(
                bacteria=bacteria,
                bacterias_referencia=(
                    bacterias_inicio
                ),
                mortes_registradas=(
                    mortes_registradas
                ),
            )

            if not bacteria.esta_viva():
                mortes_registradas[
                    id(bacteria)
                ] = bacteria

                continue

            if vagas_disponiveis <= 0:
                continue

            filho = bacteria.reproduzir()

            if filho is None:
                continue

            novos_individuos.append(
                filho
            )

            vagas_disponiveis -= 1

        sobreviventes = [
            bacteria
            for bacteria in bacterias_inicio
            if (
                id(bacteria)
                not in mortes_registradas
                and bacteria.esta_viva()
            )
        ]

        self.bacterias = (
            sobreviventes
        )

        for bacteria_morta in (
            mortes_registradas.values()
        ):
            self.processar_morte_bacteria(
                bacteria_morta
            )

        for filho in novos_individuos:
            self.adicionar_bacteria(
                filho,
                registrar_nascimento=True,
            )

    def atualizar_bacteria_individual(
        self,
        bacteria: Bacteria,
        bacterias_referencia: tuple[
            Bacteria,
            ...,
        ],
        mortes_registradas: dict[
            int,
            Bacteria,
        ],
    ) -> None:
        """
        Executa alimentação, movimento e envelhecimento de uma bactéria.
        """

        estrategia = (
            bacteria.estrategia_alimentar
        )

        if (
            estrategia
            == ESTRATEGIA_FOTOSSINTESE
        ):
            ganho = (
                bacteria.realizar_fotossintese(
                    self.ambiente
                )
            )

            if ganho > 0:
                self.consumir_nutrientes_fotossintese(
                    bacteria,
                    ganho,
                )

            bacteria.alvo_atual = None

        elif (
            estrategia
            == ESTRATEGIA_PREDACAO
        ):
            alvo = (
                self.encontrar_presa_para_predador(
                    predador=bacteria,
                    bacterias_referencia=(
                        bacterias_referencia
                    ),
                    mortes_registradas=(
                        mortes_registradas
                    ),
                )
            )

            bacteria.alvo_atual = alvo

            if alvo is None:
                bacteria.aplicar_penalidade_sem_alimento()

            else:
                bacteria.apontar_para(
                    alvo.x,
                    alvo.y,
                )

        elif (
            estrategia
            == ESTRATEGIA_NECROFAGIA
        ):
            carcaca = (
                self.encontrar_carcaca_mais_proxima(
                    bacteria
                )
            )

            bacteria.alvo_atual = (
                carcaca
            )

            if carcaca is None:
                bacteria.aplicar_penalidade_sem_alimento()

            else:
                bacteria.apontar_para(
                    carcaca.x,
                    carcaca.y,
                )

        bacteria.mover(
            quadtree=self.quadtree,
            ambiente=self.ambiente,
        )

        if not bacteria.esta_viva():
            return

        if (
            estrategia
            == ESTRATEGIA_PREDACAO
        ):
            alvo = bacteria.alvo_atual

            if (
                isinstance(
                    alvo,
                    Bacteria,
                )
                and id(alvo)
                not in mortes_registradas
                and alvo.esta_viva()
            ):
                energia_antes = max(
                    alvo.energia,
                    ENERGIA_INICIAL_CARCACA,
                )

                sucesso = (
                    bacteria.tentar_predar(
                        alvo
                    )
                )

                if sucesso:
                    mortes_registradas[
                        id(alvo)
                    ] = alvo

                    setattr(
                        alvo,
                        "_energia_carcaca",
                        energia_antes,
                    )

                    self.predacoes += 1

        elif (
            estrategia
            == ESTRATEGIA_NECROFAGIA
        ):
            carcaca = (
                bacteria.alvo_atual
            )

            if isinstance(
                carcaca,
                Carcaca,
            ):
                energia_antes = (
                    carcaca.energia
                )

                energia_recebida = (
                    bacteria.consumir_carcaca(
                        carcaca
                    )
                )

                if (
                    energia_recebida > 0
                    and energia_antes > 0
                    and not carcaca.esta_disponivel()
                ):
                    self.carcacas_consumidas += 1

    # ========================================================
    # BUSCAS DE ALIMENTO
    # ========================================================

    def encontrar_presa_para_predador(
        self,
        predador: Bacteria,
        bacterias_referencia: tuple[
            Bacteria,
            ...,
        ],
        mortes_registradas: dict[
            int,
            Bacteria,
        ],
    ) -> Bacteria | None:
        """
        Retorna a presa válida mais próxima.
        """

        raio = (
            predador.obter_raio_busca_alimento()
        )

        candidatos = (
            self.quadtree.query_circle(
                predador.x,
                predador.y,
                raio,
            )
        )

        melhor: Bacteria | None = None

        menor_distancia = (
            raio * raio
        )

        for candidato in candidatos:
            if not isinstance(
                candidato,
                Bacteria,
            ):
                continue

            if (
                candidato
                not in bacterias_referencia
            ):
                continue

            if (
                id(candidato)
                in mortes_registradas
            ):
                continue

            if not predador.pode_atacar(
                candidato
            ):
                continue

            distancia = (
                predador.distancia_quadrada_para(
                    candidato
                )
            )

            if (
                distancia
                < menor_distancia
            ):
                menor_distancia = (
                    distancia
                )

                melhor = candidato

        return melhor

    def encontrar_carcaca_mais_proxima(
        self,
        bacteria: Bacteria,
    ) -> Carcaca | None:
        """
        Retorna a carcaça disponível mais próxima.
        """

        raio = (
            bacteria.obter_raio_busca_alimento()
        )

        candidatos = (
            self.quadtree.query_circle(
                bacteria.x,
                bacteria.y,
                raio,
            )
        )

        melhor: Carcaca | None = None

        menor_distancia = (
            raio * raio
        )

        for candidato in candidatos:
            if not isinstance(
                candidato,
                Carcaca,
            ):
                continue

            if not candidato.esta_disponivel():
                continue

            distancia = (
                bacteria.distancia_quadrada_para(
                    candidato
                )
            )

            if (
                distancia
                < menor_distancia
            ):
                menor_distancia = (
                    distancia
                )

                melhor = candidato

        return melhor

    # ========================================================
    # CARCAÇAS E NUTRIENTES
    # ========================================================

    def processar_morte_bacteria(
        self,
        bacteria: Bacteria,
    ) -> None:
        """
        Converte uma bactéria morta em carcaça.
        """

        energia_carcaca = float(
            getattr(
                bacteria,
                "_energia_carcaca",
                max(
                    ENERGIA_INICIAL_CARCACA,
                    bacteria.tamanho
                    * 6.0,
                ),
            )
        )

        carcaca = Carcaca(
            x=bacteria.x,
            y=bacteria.y,
            energia=energia_carcaca,
            origem_especie=(
                bacteria.especie
            ),
            origem_estrategia=(
                bacteria.estrategia_alimentar
            ),
        )

        self.adicionar_carcaca(
            carcaca
        )

        self.mortes += 1

    def atualizar_carcacas(
        self,
    ) -> None:
        """
        Degrada carcaças e devolve matéria ao ambiente quando possível.
        """

        sobreviventes: list[
            Carcaca
        ] = []

        metodo_degradacao = getattr(
            self.ambiente,
            "degradacao_carcaca",
            None,
        )

        for carcaca in self.carcacas:
            if callable(
                metodo_degradacao
            ):
                taxa = float(
                    metodo_degradacao()
                )

            else:
                taxa = 0.04

            energia_degradada = (
                carcaca.degradar(
                    taxa
                )
            )

            if energia_degradada > 0:
                self.devolver_nutrientes_ao_ambiente(
                    x=carcaca.x,
                    y=carcaca.y,
                    quantidade=(
                        energia_degradada
                        * RETORNO_NUTRIENTES_DECOMPOSICAO
                    ),
                )

            if carcaca.esta_disponivel():
                sobreviventes.append(
                    carcaca
                )

        self.carcacas = (
            sobreviventes
        )

    def consumir_nutrientes_fotossintese(
        self,
        bacteria: Bacteria,
        energia_obtida: float,
    ) -> None:
        """
        Consome nutrientes locais quando o Ambiente oferecer suporte
        mutável.

        O ambiente atual pode ainda ser somente consultivo. Nesse caso,
        o método não produz efeito.
        """

        quantidade = max(
            0.0,
            energia_obtida
            * CONSUMO_NUTRIENTES_FOTOSSINTESE,
        )

        metodo = getattr(
            self.ambiente,
            "consumir_nutrientes",
            None,
        )

        if not callable(
            metodo
        ):
            return

        try:
            metodo(
                bacteria.x,
                bacteria.y,
                quantidade,
            )

        except TypeError:
            metodo(
                x=bacteria.x,
                y=bacteria.y,
                quantidade=quantidade,
            )

    def devolver_nutrientes_ao_ambiente(
        self,
        x: float,
        y: float,
        quantidade: float,
    ) -> None:
        """
        Adiciona nutrientes ao ambiente quando a API estiver disponível.
        """

        metodo = getattr(
            self.ambiente,
            "adicionar_nutrientes",
            None,
        )

        if not callable(
            metodo
        ):
            return

        try:
            metodo(
                x,
                y,
                quantidade,
                RAIO_DISTRIBUICAO_NUTRIENTES,
            )

        except TypeError:
            try:
                metodo(
                    x=x,
                    y=y,
                    quantidade=quantidade,
                    raio=(
                        RAIO_DISTRIBUICAO_NUTRIENTES
                    ),
                )

            except TypeError:
                metodo(
                    x,
                    y,
                    quantidade,
                )

    # ========================================================
    # ADIÇÃO DE ENTIDADES
    # ========================================================

    def adicionar_bacteria(
        self,
        bacteria: Bacteria,
        *,
        registrar_nascimento: bool = True,
    ) -> bool:
        """
        Adiciona uma bactéria se ainda houver capacidade.
        """

        if (
            len(self.bacterias)
            >= MAX_BACTERIAS
        ):
            return False

        bacteria.x = self.limitar_x(
            bacteria.x
        )

        bacteria.y = self.limitar_y(
            bacteria.y
        )

        self.bacterias.append(
            bacteria
        )

        if registrar_nascimento:
            self.nascimentos += 1

        if (
            bacteria.especie
            not in self.especies_conhecidas
        ):
            self.especies_conhecidas.add(
                bacteria.especie
            )

            if registrar_nascimento:
                nome_estrategia = (
                    NOMES_ESTRATEGIAS.get(
                        bacteria.estrategia_alimentar,
                        bacteria.estrategia_alimentar,
                    )
                )

                self.registrar_evento(
                    "nova_especie",
                    (
                        "Nova espécie detectada: "
                        f"{bacteria.especie} "
                        f"({nome_estrategia})."
                    ),
                )

        return True

    def adicionar_carcaca(
        self,
        carcaca: Carcaca,
    ) -> bool:
        """
        Adiciona uma carcaça respeitando o limite configurado.
        """

        if (
            len(self.carcacas)
            >= MAX_CARCACAS
        ):
            return False

        carcaca.x = self.limitar_x(
            carcaca.x
        )

        carcaca.y = self.limitar_y(
            carcaca.y
        )

        self.carcacas.append(
            carcaca
        )

        return True

    def adicionar_bacteria_na_posicao(
        self,
        x: float,
        y: float,
        estrategia_alimentar: str = (
            ESTRATEGIA_FOTOSSINTESE
        ),
    ) -> bool:
        """
        Adiciona uma bactéria da estratégia informada.
        """

        if (
            estrategia_alimentar
            not in ESTRATEGIAS_ALIMENTARES
        ):
            raise ValueError(
                "Estratégia alimentar inválida."
            )

        return self.adicionar_bacteria(
            Bacteria(
                x=self.limitar_x(
                    x
                ),
                y=self.limitar_y(
                    y
                ),
                estrategia_alimentar=(
                    estrategia_alimentar
                ),
            )
        )

    def adicionar_fotossintetica_na_posicao(
        self,
        x: float,
        y: float,
    ) -> bool:
        return (
            self.adicionar_bacteria_na_posicao(
                x,
                y,
                ESTRATEGIA_FOTOSSINTESE,
            )
        )

    def adicionar_predadora_na_posicao(
        self,
        x: float,
        y: float,
    ) -> bool:
        return (
            self.adicionar_bacteria_na_posicao(
                x,
                y,
                ESTRATEGIA_PREDACAO,
            )
        )

    def adicionar_necrofaga_na_posicao(
        self,
        x: float,
        y: float,
    ) -> bool:
        return (
            self.adicionar_bacteria_na_posicao(
                x,
                y,
                ESTRATEGIA_NECROFAGIA,
            )
        )

    def adicionar_alga_na_posicao(
        self,
        x: float,
        y: float,
    ) -> bool:
        """
        Compatibilidade temporária com o main.py antigo.

        Uma antiga alga passa a ser uma bactéria fotossintética.
        """

        return (
            self.adicionar_fotossintetica_na_posicao(
                x,
                y,
            )
        )

    def adicionar_protozoario_na_posicao(
        self,
        x: float,
        y: float,
    ) -> bool:
        """
        Compatibilidade temporária com versões antigas.
        """

        return (
            self.adicionar_predadora_na_posicao(
                x,
                y,
            )
        )

    # ========================================================
    # LIMITES E CONSULTAS
    # ========================================================

    def garantir_limites_populacionais(
        self,
    ) -> None:
        """
        Aplica uma barreira final contra excesso de entidades.
        """

        if (
            len(self.bacterias)
            > MAX_BACTERIAS
        ):
            excedentes = (
                self.bacterias[
                    MAX_BACTERIAS:
                ]
            )

            self.bacterias = (
                self.bacterias[
                    :MAX_BACTERIAS
                ]
            )

            for bacteria in excedentes:
                self.processar_morte_bacteria(
                    bacteria
                )

        if (
            len(self.carcacas)
            > MAX_CARCACAS
        ):
            self.carcacas = (
                self.carcacas[
                    -MAX_CARCACAS:
                ]
            )

    def obter_bacterias_por_estrategia(
        self,
        estrategia: str,
    ) -> list[Bacteria]:
        """
        Retorna bactérias de uma estratégia alimentar.
        """

        return [
            bacteria
            for bacteria in self.bacterias
            if (
                bacteria.estrategia_alimentar
                == estrategia
            )
        ]

    def obter_organismos(
        self,
    ) -> list[Any]:
        """
        Retorna todas as entidades selecionáveis.
        """

        return [
            *self.bacterias,
            *self.carcacas,
        ]

    def encontrar_organismo_mais_proximo(
        self,
        x: float,
        y: float,
        raio: float,
        *,
        tipos: tuple[
            type,
            ...,
        ] = (
            Bacteria,
            Carcaca,
        ),
    ) -> Any | None:
        """
        Encontra a entidade válida mais próxima.
        """

        candidatos = (
            self.quadtree.query_circle(
                x,
                y,
                raio,
            )
        )

        melhor = None
        menor_distancia = raio * raio

        for organismo in candidatos:
            if not isinstance(
                organismo,
                tipos,
            ):
                continue

            dx = organismo.x - x
            dy = organismo.y - y

            distancia = (
                dx * dx
                + dy * dy
            )

            if (
                distancia
                < menor_distancia
            ):
                menor_distancia = (
                    distancia
                )

                melhor = organismo

        return melhor

    # ========================================================
    # ESTATÍSTICAS
    # ========================================================

    def obter_estatisticas(
        self,
    ) -> dict[str, Any]:
        """
        Retorna indicadores do ecossistema.

        Inclui aliases antigos para permitir a migração gradual
        da interface.
        """

        contagem_estrategias = Counter(
            bacteria.estrategia_alimentar
            for bacteria in self.bacterias
        )

        especies = {
            bacteria.especie
            for bacteria in self.bacterias
        }

        condicoes = (
            self.ambiente.obter_condicoes()
        )

        fotossinteticas = (
            contagem_estrategias[
                ESTRATEGIA_FOTOSSINTESE
            ]
        )

        predadoras = (
            contagem_estrategias[
                ESTRATEGIA_PREDACAO
            ]
        )

        necrofagas = (
            contagem_estrategias[
                ESTRATEGIA_NECROFAGIA
            ]
        )

        energia_media = self.obter_media(
            bacteria.energia
            for bacteria in self.bacterias
        )

        idade_media = self.obter_media(
            bacteria.idade
            for bacteria in self.bacterias
        )

        return {
            "bacterias": len(
                self.bacterias
            ),
            "fotossinteticas": (
                fotossinteticas
            ),
            "predadoras": predadoras,
            "necrofagas": necrofagas,
            "carcacas": len(
                self.carcacas
            ),
            "especies": len(
                especies
            ),
            "ciclo_luz": (
                condicoes.ciclo_luz
            ),
            "intensidade_luz": (
                condicoes.intensidade_luz
            ),
            "temperatura": (
                condicoes.temperatura
            ),
            "umidade": (
                condicoes.umidade
            ),
            "tempo": self.tempo,
            "energia_media": (
                energia_media
            ),
            "idade_media": (
                idade_media
            ),
            "nascimentos": (
                self.nascimentos
            ),
            "mortes": self.mortes,
            "predacoes": (
                self.predacoes
            ),
            "carcacas_consumidas": (
                self.carcacas_consumidas
            ),
            "nutrientes_medios": (
                self.obter_nivel_medio_nutrientes()
            ),

            # Compatibilidade com o painel antigo.
            "algas": fotossinteticas,
            "protozoarios": predadoras,
        }

    def obter_especies_mais_abundantes(
        self,
        limite: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Retorna as espécies mais abundantes.
        """

        contagem = Counter(
            bacteria.especie
            for bacteria in self.bacterias
        )

        resultado: list[
            dict[str, Any]
        ] = []

        for (
            especie,
            quantidade,
        ) in contagem.most_common(
            limite
        ):
            representantes = [
                bacteria
                for bacteria in self.bacterias
                if (
                    bacteria.especie
                    == especie
                )
            ]

            if not representantes:
                continue

            representante = (
                representantes[0]
            )

            estrategias = Counter(
                bacteria.estrategia_alimentar
                for bacteria in representantes
            )

            estrategia_dominante = (
                estrategias.most_common(
                    1
                )[0][0]
            )

            resultado.append(
                {
                    "nome": especie,
                    "quantidade": quantidade,
                    "cor": (
                        cores_especies.get(
                            especie,
                            representante.cor,
                        )
                    ),
                    "estrategia": (
                        estrategia_dominante
                    ),
                    "estrategia_nome": (
                        NOMES_ESTRATEGIAS.get(
                            estrategia_dominante,
                            estrategia_dominante,
                        )
                    ),

                    # Compatibilidade temporária.
                    "presa": (
                        estrategia_dominante
                    ),
                }
            )

        return resultado

    def obter_nivel_medio_nutrientes(
        self,
    ) -> float:
        """
        Estima os nutrientes médios usando uma grade de amostragem.
        """

        amostras_x = 6
        amostras_y = 5

        valores: list[
            float
        ] = []

        for indice_x in range(
            amostras_x
        ):
            x = (
                AREA_SIMULACAO_LARGURA
                * (
                    indice_x
                    + 0.5
                )
                / amostras_x
            )

            for indice_y in range(
                amostras_y
            ):
                y = (
                    ALTURA
                    * (
                        indice_y
                        + 0.5
                    )
                    / amostras_y
                )

                valores.append(
                    float(
                        self.ambiente.nivel_nutrientes(
                            x,
                            y,
                        )
                    )
                )

        return self.obter_media(
            valores
        )

    @staticmethod
    def obter_media(
        valores: Iterable[float],
    ) -> float:
        """
        Calcula uma média segura.
        """

        lista = [
            float(
                valor
            )
            for valor in valores
        ]

        if not lista:
            return 0.0

        return (
            sum(lista)
            / len(lista)
        )

    # ========================================================
    # EVENTOS
    # ========================================================

    def registrar_evento(
        self,
        tipo: str,
        mensagem: str,
    ) -> None:
        """
        Registra um acontecimento relevante.
        """

        self.eventos.appendleft(
            {
                "tempo": self.tempo,
                "tipo": tipo,
                "mensagem": mensagem,
            }
        )

    def obter_eventos(
        self,
        limite: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Retorna os eventos mais recentes.
        """

        limite = max(
            0,
            int(
                limite
            ),
        )

        return list(
            self.eventos
        )[:limite]

    # ========================================================
    # RENDERIZAÇÃO
    # ========================================================

    def desenhar(
        self,
        tela: pygame.Surface,
    ) -> None:
        """
        Desenha o ambiente, carcaças e bactérias.
        """

        area_simulacao = pygame.Rect(
            0,
            0,
            AREA_SIMULACAO_LARGURA,
            ALTURA,
        )

        pygame.draw.rect(
            tela,
            self.obter_cor_de_fundo(),
            area_simulacao,
        )

        for carcaca in self.carcacas:
            carcaca.desenhar(
                tela
            )

        for bacteria in self.bacterias:
            bacteria.desenhar(
                tela
            )

    def obter_cor_de_fundo(
        self,
    ) -> tuple[int, int, int]:
        """
        Interpola suavemente o fundo conforme a intensidade da luz.
        """

        intensidade = max(
            0.0,
            min(
                1.0,
                float(
                    self.ambiente.intensidade_luz()
                ),
            ),
        )

        return tuple(
            int(
                FUNDO_NOITE[indice]
                + (
                    FUNDO_DIA[indice]
                    - FUNDO_NOITE[indice]
                )
                * intensidade
            )
            for indice in range(
                3
            )
        )

    # ========================================================
    # UTILITÁRIOS
    # ========================================================

    @staticmethod
    def limitar_x(
        x: float,
    ) -> float:
        return max(
            0.0,
            min(
                float(x),
                float(
                    AREA_SIMULACAO_LARGURA
                    - 1
                ),
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
                float(
                    ALTURA - 1
                ),
            ),
        )

    def __repr__(
        self,
    ) -> str:
        estatisticas = (
            self.obter_estatisticas()
        )

        return (
            "Mundo("
            f"tempo={self.tempo}, "
            f"bacterias={estatisticas['bacterias']}, "
            f"fotossinteticas="
            f"{estatisticas['fotossinteticas']}, "
            f"predadoras="
            f"{estatisticas['predadoras']}, "
            f"necrofagas="
            f"{estatisticas['necrofagas']}, "
            f"carcacas="
            f"{estatisticas['carcacas']}"
            ")"
        )# mundo.py
from __future__ import annotations

import random
from collections import Counter, deque
from typing import Any, Iterable

import pygame

from ambiente import Ambiente
from configuracoes import (
    ALTURA,
    AREA_SIMULACAO_LARGURA,
    BACTERIAS_FOTOSSINTETICAS_INICIAIS,
    BACTERIAS_NECROFAGAS_INICIAIS,
    BACTERIAS_PREDADORAS_INICIAIS,
    CONSUMO_NUTRIENTES_FOTOSSINTESE,
    DURACAO_CICLO,
    DURACAO_ESTACAO,
    ENERGIA_INICIAL_CARCACA,
    ESTRATEGIA_FOTOSSINTESE,
    ESTRATEGIA_NECROFAGIA,
    ESTRATEGIA_PREDACAO,
    ESTRATEGIAS_ALIMENTARES,
    FUNDO_DIA,
    FUNDO_NOITE,
    MAX_BACTERIAS,
    MAX_CARCACAS,
    MAX_EVENTOS_REGISTRADOS,
    NOMES_ESTRATEGIAS,
    QUADTREE_CAPACIDADE,
    QUADTREE_PROFUNDIDADE_MAXIMA,
    RAIO_DISTRIBUICAO_NUTRIENTES,
    RETORNO_NUTRIENTES_DECOMPOSICAO,
    TEMPERATURA_MEDIA,
    UMIDADE_MEDIA,
)
from organismos import (
    Bacteria,
    Carcaca,
    cores_especies,
)
from quadtree import Quadtree


class Mundo:
    """
    Gerencia o ecossistema bacteriano completo.

    Todas as entidades vivas são bactérias. A diferença ecológica está
    na estratégia alimentar:

    - fotossíntese;
    - predação;
    - necrofagia.

    Carcaças são recursos orgânicos sem vida.
    """

    def __init__(
        self,
        *,
        semente: int | None = None,
    ) -> None:
        self.semente = semente
        self.gerador = random.Random(
            semente
        )

        self.tempo = 0

        self.ambiente = Ambiente(
            duracao_ciclo=DURACAO_CICLO,
            duracao_estacao=DURACAO_ESTACAO,
            temperatura_media=TEMPERATURA_MEDIA,
            umidade_media=UMIDADE_MEDIA,
            semente=semente,
        )

        self.bacterias: list[
            Bacteria
        ] = []

        self.carcacas: list[
            Carcaca
        ] = []

        self.quadtree = (
            self.criar_quadtree()
        )

        self.eventos: deque[
            dict[str, Any]
        ] = deque(
            maxlen=MAX_EVENTOS_REGISTRADOS
        )

        self.especies_conhecidas: set[
            str
        ] = set()

        self.nascimentos = 0
        self.mortes = 0
        self.predacoes = 0
        self.carcacas_consumidas = 0

        self.inicializar_populacoes()
        self.reconstruir_quadtree()

        self.registrar_evento(
            "inicio",
            (
                "Ecossistema iniciado com "
                f"{len(self.bacterias)} bactérias."
            ),
        )

    # ========================================================
    # COMPATIBILIDADE TEMPORÁRIA
    # ========================================================

    @property
    def ciclo_luz(self) -> str:
        """
        Mantém compatibilidade com versões anteriores da interface.
        """

        return self.ambiente.ciclo_luz()

    @property
    def algas(
        self,
    ) -> list[Bacteria]:
        """
        Compatibilidade temporária.

        Antigas algas agora são bactérias fotossintéticas.
        """

        return (
            self.obter_bacterias_por_estrategia(
                ESTRATEGIA_FOTOSSINTESE
            )
        )

    @property
    def protozoarios(
        self,
    ) -> list[Bacteria]:
        """
        Compatibilidade temporária.

        Antigos protozoários agora são bactérias predadoras.
        """

        return (
            self.obter_bacterias_por_estrategia(
                ESTRATEGIA_PREDACAO
            )
        )

    # ========================================================
    # INICIALIZAÇÃO
    # ========================================================

    def inicializar_populacoes(
        self,
    ) -> None:
        """
        Cria as populações iniciais das três estratégias.
        """

        configuracoes = (
            (
                ESTRATEGIA_FOTOSSINTESE,
                BACTERIAS_FOTOSSINTETICAS_INICIAIS,
            ),
            (
                ESTRATEGIA_PREDACAO,
                BACTERIAS_PREDADORAS_INICIAIS,
            ),
            (
                ESTRATEGIA_NECROFAGIA,
                BACTERIAS_NECROFAGAS_INICIAIS,
            ),
        )

        for (
            estrategia,
            quantidade,
        ) in configuracoes:
            for _ in range(
                quantidade
            ):
                if (
                    len(self.bacterias)
                    >= MAX_BACTERIAS
                ):
                    return

                bacteria = Bacteria(
                    x=self.gerador.uniform(
                        0,
                        AREA_SIMULACAO_LARGURA
                        - 1,
                    ),
                    y=self.gerador.uniform(
                        0,
                        ALTURA - 1,
                    ),
                    estrategia_alimentar=(
                        estrategia
                    ),
                )

                self.adicionar_bacteria(
                    bacteria,
                    registrar_nascimento=False,
                )

    # ========================================================
    # QUADTREE
    # ========================================================

    def criar_quadtree(
        self,
    ) -> Quadtree:
        """
        Cria a estrutura espacial usada nas buscas de proximidade.
        """

        return Quadtree(
            (
                0.0,
                0.0,
                float(
                    AREA_SIMULACAO_LARGURA
                ),
                float(
                    ALTURA
                ),
            ),
            capacity=QUADTREE_CAPACIDADE,
            max_depth=(
                QUADTREE_PROFUNDIDADE_MAXIMA
            ),
        )

    def reconstruir_quadtree(
        self,
    ) -> None:
        """
        Reconstrói a árvore com as posições atuais.
        """

        self.quadtree = (
            self.criar_quadtree()
        )

        for bacteria in self.bacterias:
            if bacteria.esta_viva():
                self.quadtree.insert(
                    bacteria
                )

        for carcaca in self.carcacas:
            if carcaca.esta_disponivel():
                self.quadtree.insert(
                    carcaca
                )

    # ========================================================
    # ATUALIZAÇÃO PRINCIPAL
    # ========================================================

    def atualizar(
        self,
    ) -> None:
        """
        Executa um passo completo da simulação.
        """

        self.tempo += 1

        self.ambiente.atualizar()

        self.reconstruir_quadtree()
        self.atualizar_bacterias()
        self.atualizar_carcacas()
        self.garantir_limites_populacionais()

    def atualizar_bacterias(
        self,
    ) -> None:
        """
        Atualiza todas as bactérias sem modificar a lista durante
        a iteração.
        """

        bacterias_inicio = tuple(
            self.bacterias
        )

        mortes_registradas: dict[
            int,
            Bacteria,
        ] = {}

        novos_individuos: list[
            Bacteria
        ] = []

        vagas_disponiveis = max(
            0,
            MAX_BACTERIAS
            - len(
                bacterias_inicio
            ),
        )

        for bacteria in bacterias_inicio:
            if (
                id(bacteria)
                in mortes_registradas
            ):
                continue

            if not bacteria.esta_viva():
                mortes_registradas[
                    id(bacteria)
                ] = bacteria

                continue

            self.atualizar_bacteria_individual(
                bacteria=bacteria,
                bacterias_referencia=(
                    bacterias_inicio
                ),
                mortes_registradas=(
                    mortes_registradas
                ),
            )

            if not bacteria.esta_viva():
                mortes_registradas[
                    id(bacteria)
                ] = bacteria

                continue

            if vagas_disponiveis <= 0:
                continue

            filho = bacteria.reproduzir()

            if filho is None:
                continue

            novos_individuos.append(
                filho
            )

            vagas_disponiveis -= 1

        sobreviventes = [
            bacteria
            for bacteria in bacterias_inicio
            if (
                id(bacteria)
                not in mortes_registradas
                and bacteria.esta_viva()
            )
        ]

        self.bacterias = (
            sobreviventes
        )

        for bacteria_morta in (
            mortes_registradas.values()
        ):
            self.processar_morte_bacteria(
                bacteria_morta
            )

        for filho in novos_individuos:
            self.adicionar_bacteria(
                filho,
                registrar_nascimento=True,
            )

    def atualizar_bacteria_individual(
        self,
        bacteria: Bacteria,
        bacterias_referencia: tuple[
            Bacteria,
            ...,
        ],
        mortes_registradas: dict[
            int,
            Bacteria,
        ],
    ) -> None:
        """
        Executa alimentação, movimento e envelhecimento de uma bactéria.
        """

        estrategia = (
            bacteria.estrategia_alimentar
        )

        if (
            estrategia
            == ESTRATEGIA_FOTOSSINTESE
        ):
            ganho = (
                bacteria.realizar_fotossintese(
                    self.ambiente
                )
            )

            if ganho > 0:
                self.consumir_nutrientes_fotossintese(
                    bacteria,
                    ganho,
                )

            bacteria.alvo_atual = None

        elif (
            estrategia
            == ESTRATEGIA_PREDACAO
        ):
            alvo = (
                self.encontrar_presa_para_predador(
                    predador=bacteria,
                    bacterias_referencia=(
                        bacterias_referencia
                    ),
                    mortes_registradas=(
                        mortes_registradas
                    ),
                )
            )

            bacteria.alvo_atual = alvo

            if alvo is None:
                bacteria.aplicar_penalidade_sem_alimento()

            else:
                bacteria.apontar_para(
                    alvo.x,
                    alvo.y,
                )

        elif (
            estrategia
            == ESTRATEGIA_NECROFAGIA
        ):
            carcaca = (
                self.encontrar_carcaca_mais_proxima(
                    bacteria
                )
            )

            bacteria.alvo_atual = (
                carcaca
            )

            if carcaca is None:
                bacteria.aplicar_penalidade_sem_alimento()

            else:
                bacteria.apontar_para(
                    carcaca.x,
                    carcaca.y,
                )

        bacteria.mover(
            quadtree=self.quadtree,
            ambiente=self.ambiente,
        )

        if not bacteria.esta_viva():
            return

        if (
            estrategia
            == ESTRATEGIA_PREDACAO
        ):
            alvo = bacteria.alvo_atual

            if (
                isinstance(
                    alvo,
                    Bacteria,
                )
                and id(alvo)
                not in mortes_registradas
                and alvo.esta_viva()
            ):
                energia_antes = max(
                    alvo.energia,
                    ENERGIA_INICIAL_CARCACA,
                )

                sucesso = (
                    bacteria.tentar_predar(
                        alvo
                    )
                )

                if sucesso:
                    mortes_registradas[
                        id(alvo)
                    ] = alvo

                    setattr(
                        alvo,
                        "_energia_carcaca",
                        energia_antes,
                    )

                    self.predacoes += 1

        elif (
            estrategia
            == ESTRATEGIA_NECROFAGIA
        ):
            carcaca = (
                bacteria.alvo_atual
            )

            if isinstance(
                carcaca,
                Carcaca,
            ):
                energia_antes = (
                    carcaca.energia
                )

                energia_recebida = (
                    bacteria.consumir_carcaca(
                        carcaca
                    )
                )

                if (
                    energia_recebida > 0
                    and energia_antes > 0
                    and not carcaca.esta_disponivel()
                ):
                    self.carcacas_consumidas += 1

    # ========================================================
    # BUSCAS DE ALIMENTO
    # ========================================================

    def encontrar_presa_para_predador(
        self,
        predador: Bacteria,
        bacterias_referencia: tuple[
            Bacteria,
            ...,
        ],
        mortes_registradas: dict[
            int,
            Bacteria,
        ],
    ) -> Bacteria | None:
        """
        Retorna a presa válida mais próxima.
        """

        raio = (
            predador.obter_raio_busca_alimento()
        )

        candidatos = (
            self.quadtree.query_circle(
                predador.x,
                predador.y,
                raio,
            )
        )

        melhor: Bacteria | None = None

        menor_distancia = (
            raio * raio
        )

        for candidato in candidatos:
            if not isinstance(
                candidato,
                Bacteria,
            ):
                continue

            if (
                candidato
                not in bacterias_referencia
            ):
                continue

            if (
                id(candidato)
                in mortes_registradas
            ):
                continue

            if not predador.pode_atacar(
                candidato
            ):
                continue

            distancia = (
                predador.distancia_quadrada_para(
                    candidato
                )
            )

            if (
                distancia
                < menor_distancia
            ):
                menor_distancia = (
                    distancia
                )

                melhor = candidato

        return melhor

    def encontrar_carcaca_mais_proxima(
        self,
        bacteria: Bacteria,
    ) -> Carcaca | None:
        """
        Retorna a carcaça disponível mais próxima.
        """

        raio = (
            bacteria.obter_raio_busca_alimento()
        )

        candidatos = (
            self.quadtree.query_circle(
                bacteria.x,
                bacteria.y,
                raio,
            )
        )

        melhor: Carcaca | None = None

        menor_distancia = (
            raio * raio
        )

        for candidato in candidatos:
            if not isinstance(
                candidato,
                Carcaca,
            ):
                continue

            if not candidato.esta_disponivel():
                continue

            distancia = (
                bacteria.distancia_quadrada_para(
                    candidato
                )
            )

            if (
                distancia
                < menor_distancia
            ):
                menor_distancia = (
                    distancia
                )

                melhor = candidato

        return melhor

    # ========================================================
    # CARCAÇAS E NUTRIENTES
    # ========================================================

    def processar_morte_bacteria(
        self,
        bacteria: Bacteria,
    ) -> None:
        """
        Converte uma bactéria morta em carcaça.
        """

        energia_carcaca = float(
            getattr(
                bacteria,
                "_energia_carcaca",
                max(
                    ENERGIA_INICIAL_CARCACA,
                    bacteria.tamanho
                    * 6.0,
                ),
            )
        )

        carcaca = Carcaca(
            x=bacteria.x,
            y=bacteria.y,
            energia=energia_carcaca,
            origem_especie=(
                bacteria.especie
            ),
            origem_estrategia=(
                bacteria.estrategia_alimentar
            ),
        )

        self.adicionar_carcaca(
            carcaca
        )

        self.mortes += 1

    def atualizar_carcacas(
        self,
    ) -> None:
        """
        Degrada carcaças e devolve matéria ao ambiente quando possível.
        """

        sobreviventes: list[
            Carcaca
        ] = []

        metodo_degradacao = getattr(
            self.ambiente,
            "degradacao_carcaca",
            None,
        )

        for carcaca in self.carcacas:
            if callable(
                metodo_degradacao
            ):
                taxa = float(
                    metodo_degradacao()
                )

            else:
                taxa = 0.04

            energia_degradada = (
                carcaca.degradar(
                    taxa
                )
            )

            if energia_degradada > 0:
                self.devolver_nutrientes_ao_ambiente(
                    x=carcaca.x,
                    y=carcaca.y,
                    quantidade=(
                        energia_degradada
                        * RETORNO_NUTRIENTES_DECOMPOSICAO
                    ),
                )

            if carcaca.esta_disponivel():
                sobreviventes.append(
                    carcaca
                )

        self.carcacas = (
            sobreviventes
        )

    def consumir_nutrientes_fotossintese(
        self,
        bacteria: Bacteria,
        energia_obtida: float,
    ) -> None:
        """
        Consome nutrientes locais quando o Ambiente oferecer suporte
        mutável.

        O ambiente atual pode ainda ser somente consultivo. Nesse caso,
        o método não produz efeito.
        """

        quantidade = max(
            0.0,
            energia_obtida
            * CONSUMO_NUTRIENTES_FOTOSSINTESE,
        )

        metodo = getattr(
            self.ambiente,
            "consumir_nutrientes",
            None,
        )

        if not callable(
            metodo
        ):
            return

        try:
            metodo(
                bacteria.x,
                bacteria.y,
                quantidade,
            )

        except TypeError:
            metodo(
                x=bacteria.x,
                y=bacteria.y,
                quantidade=quantidade,
            )

    def devolver_nutrientes_ao_ambiente(
        self,
        x: float,
        y: float,
        quantidade: float,
    ) -> None:
        """
        Adiciona nutrientes ao ambiente quando a API estiver disponível.
        """

        metodo = getattr(
            self.ambiente,
            "adicionar_nutrientes",
            None,
        )

        if not callable(
            metodo
        ):
            return

        try:
            metodo(
                x,
                y,
                quantidade,
                RAIO_DISTRIBUICAO_NUTRIENTES,
            )

        except TypeError:
            try:
                metodo(
                    x=x,
                    y=y,
                    quantidade=quantidade,
                    raio=(
                        RAIO_DISTRIBUICAO_NUTRIENTES
                    ),
                )

            except TypeError:
                metodo(
                    x,
                    y,
                    quantidade,
                )

    # ========================================================
    # ADIÇÃO DE ENTIDADES
    # ========================================================

    def adicionar_bacteria(
        self,
        bacteria: Bacteria,
        *,
        registrar_nascimento: bool = True,
    ) -> bool:
        """
        Adiciona uma bactéria se ainda houver capacidade.
        """

        if (
            len(self.bacterias)
            >= MAX_BACTERIAS
        ):
            return False

        bacteria.x = self.limitar_x(
            bacteria.x
        )

        bacteria.y = self.limitar_y(
            bacteria.y
        )

        self.bacterias.append(
            bacteria
        )

        if registrar_nascimento:
            self.nascimentos += 1

        if (
            bacteria.especie
            not in self.especies_conhecidas
        ):
            self.especies_conhecidas.add(
                bacteria.especie
            )

            if registrar_nascimento:
                nome_estrategia = (
                    NOMES_ESTRATEGIAS.get(
                        bacteria.estrategia_alimentar,
                        bacteria.estrategia_alimentar,
                    )
                )

                self.registrar_evento(
                    "nova_especie",
                    (
                        "Nova espécie detectada: "
                        f"{bacteria.especie} "
                        f"({nome_estrategia})."
                    ),
                )

        return True

    def adicionar_carcaca(
        self,
        carcaca: Carcaca,
    ) -> bool:
        """
        Adiciona uma carcaça respeitando o limite configurado.
        """

        if (
            len(self.carcacas)
            >= MAX_CARCACAS
        ):
            return False

        carcaca.x = self.limitar_x(
            carcaca.x
        )

        carcaca.y = self.limitar_y(
            carcaca.y
        )

        self.carcacas.append(
            carcaca
        )

        return True

    def adicionar_bacteria_na_posicao(
        self,
        x: float,
        y: float,
        estrategia_alimentar: str = (
            ESTRATEGIA_FOTOSSINTESE
        ),
    ) -> bool:
        """
        Adiciona uma bactéria da estratégia informada.
        """

        if (
            estrategia_alimentar
            not in ESTRATEGIAS_ALIMENTARES
        ):
            raise ValueError(
                "Estratégia alimentar inválida."
            )

        return self.adicionar_bacteria(
            Bacteria(
                x=self.limitar_x(
                    x
                ),
                y=self.limitar_y(
                    y
                ),
                estrategia_alimentar=(
                    estrategia_alimentar
                ),
            )
        )

    def adicionar_fotossintetica_na_posicao(
        self,
        x: float,
        y: float,
    ) -> bool:
        return (
            self.adicionar_bacteria_na_posicao(
                x,
                y,
                ESTRATEGIA_FOTOSSINTESE,
            )
        )

    def adicionar_predadora_na_posicao(
        self,
        x: float,
        y: float,
    ) -> bool:
        return (
            self.adicionar_bacteria_na_posicao(
                x,
                y,
                ESTRATEGIA_PREDACAO,
            )
        )

    def adicionar_necrofaga_na_posicao(
        self,
        x: float,
        y: float,
    ) -> bool:
        return (
            self.adicionar_bacteria_na_posicao(
                x,
                y,
                ESTRATEGIA_NECROFAGIA,
            )
        )

    def adicionar_alga_na_posicao(
        self,
        x: float,
        y: float,
    ) -> bool:
        """
        Compatibilidade temporária com o main.py antigo.

        Uma antiga alga passa a ser uma bactéria fotossintética.
        """

        return (
            self.adicionar_fotossintetica_na_posicao(
                x,
                y,
            )
        )

    def adicionar_protozoario_na_posicao(
        self,
        x: float,
        y: float,
    ) -> bool:
        """
        Compatibilidade temporária com versões antigas.
        """

        return (
            self.adicionar_predadora_na_posicao(
                x,
                y,
            )
        )

    # ========================================================
    # LIMITES E CONSULTAS
    # ========================================================

    def garantir_limites_populacionais(
        self,
    ) -> None:
        """
        Aplica uma barreira final contra excesso de entidades.
        """

        if (
            len(self.bacterias)
            > MAX_BACTERIAS
        ):
            excedentes = (
                self.bacterias[
                    MAX_BACTERIAS:
                ]
            )

            self.bacterias = (
                self.bacterias[
                    :MAX_BACTERIAS
                ]
            )

            for bacteria in excedentes:
                self.processar_morte_bacteria(
                    bacteria
                )

        if (
            len(self.carcacas)
            > MAX_CARCACAS
        ):
            self.carcacas = (
                self.carcacas[
                    -MAX_CARCACAS:
                ]
            )

    def obter_bacterias_por_estrategia(
        self,
        estrategia: str,
    ) -> list[Bacteria]:
        """
        Retorna bactérias de uma estratégia alimentar.
        """

        return [
            bacteria
            for bacteria in self.bacterias
            if (
                bacteria.estrategia_alimentar
                == estrategia
            )
        ]

    def obter_organismos(
        self,
    ) -> list[Any]:
        """
        Retorna todas as entidades selecionáveis.
        """

        return [
            *self.bacterias,
            *self.carcacas,
        ]

    def encontrar_organismo_mais_proximo(
        self,
        x: float,
        y: float,
        raio: float,
        *,
        tipos: tuple[
            type,
            ...,
        ] = (
            Bacteria,
            Carcaca,
        ),
    ) -> Any | None:
        """
        Encontra a entidade válida mais próxima.
        """

        candidatos = (
            self.quadtree.query_circle(
                x,
                y,
                raio,
            )
        )

        melhor = None
        menor_distancia = raio * raio

        for organismo in candidatos:
            if not isinstance(
                organismo,
                tipos,
            ):
                continue

            dx = organismo.x - x
            dy = organismo.y - y

            distancia = (
                dx * dx
                + dy * dy
            )

            if (
                distancia
                < menor_distancia
            ):
                menor_distancia = (
                    distancia
                )

                melhor = organismo

        return melhor

    # ========================================================
    # ESTATÍSTICAS
    # ========================================================

    def obter_estatisticas(
        self,
    ) -> dict[str, Any]:
        """
        Retorna indicadores do ecossistema.

        Inclui aliases antigos para permitir a migração gradual
        da interface.
        """

        contagem_estrategias = Counter(
            bacteria.estrategia_alimentar
            for bacteria in self.bacterias
        )

        especies = {
            bacteria.especie
            for bacteria in self.bacterias
        }

        condicoes = (
            self.ambiente.obter_condicoes()
        )

        fotossinteticas = (
            contagem_estrategias[
                ESTRATEGIA_FOTOSSINTESE
            ]
        )

        predadoras = (
            contagem_estrategias[
                ESTRATEGIA_PREDACAO
            ]
        )

        necrofagas = (
            contagem_estrategias[
                ESTRATEGIA_NECROFAGIA
            ]
        )

        energia_media = self.obter_media(
            bacteria.energia
            for bacteria in self.bacterias
        )

        idade_media = self.obter_media(
            bacteria.idade
            for bacteria in self.bacterias
        )

        return {
            "bacterias": len(
                self.bacterias
            ),
            "fotossinteticas": (
                fotossinteticas
            ),
            "predadoras": predadoras,
            "necrofagas": necrofagas,
            "carcacas": len(
                self.carcacas
            ),
            "especies": len(
                especies
            ),
            "ciclo_luz": (
                condicoes.ciclo_luz
            ),
            "intensidade_luz": (
                condicoes.intensidade_luz
            ),
            "temperatura": (
                condicoes.temperatura
            ),
            "umidade": (
                condicoes.umidade
            ),
            "tempo": self.tempo,
            "energia_media": (
                energia_media
            ),
            "idade_media": (
                idade_media
            ),
            "nascimentos": (
                self.nascimentos
            ),
            "mortes": self.mortes,
            "predacoes": (
                self.predacoes
            ),
            "carcacas_consumidas": (
                self.carcacas_consumidas
            ),
            "nutrientes_medios": (
                self.obter_nivel_medio_nutrientes()
            ),

            # Compatibilidade com o painel antigo.
            "algas": fotossinteticas,
            "protozoarios": predadoras,
        }

    def obter_especies_mais_abundantes(
        self,
        limite: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Retorna as espécies mais abundantes.
        """

        contagem = Counter(
            bacteria.especie
            for bacteria in self.bacterias
        )

        resultado: list[
            dict[str, Any]
        ] = []

        for (
            especie,
            quantidade,
        ) in contagem.most_common(
            limite
        ):
            representantes = [
                bacteria
                for bacteria in self.bacterias
                if (
                    bacteria.especie
                    == especie
                )
            ]

            if not representantes:
                continue

            representante = (
                representantes[0]
            )

            estrategias = Counter(
                bacteria.estrategia_alimentar
                for bacteria in representantes
            )

            estrategia_dominante = (
                estrategias.most_common(
                    1
                )[0][0]
            )

            resultado.append(
                {
                    "nome": especie,
                    "quantidade": quantidade,
                    "cor": (
                        cores_especies.get(
                            especie,
                            representante.cor,
                        )
                    ),
                    "estrategia": (
                        estrategia_dominante
                    ),
                    "estrategia_nome": (
                        NOMES_ESTRATEGIAS.get(
                            estrategia_dominante,
                            estrategia_dominante,
                        )
                    ),

                    # Compatibilidade temporária.
                    "presa": (
                        estrategia_dominante
                    ),
                }
            )

        return resultado

    def obter_nivel_medio_nutrientes(
        self,
    ) -> float:
        """
        Estima os nutrientes médios usando uma grade de amostragem.
        """

        amostras_x = 6
        amostras_y = 5

        valores: list[
            float
        ] = []

        for indice_x in range(
            amostras_x
        ):
            x = (
                AREA_SIMULACAO_LARGURA
                * (
                    indice_x
                    + 0.5
                )
                / amostras_x
            )

            for indice_y in range(
                amostras_y
            ):
                y = (
                    ALTURA
                    * (
                        indice_y
                        + 0.5
                    )
                    / amostras_y
                )

                valores.append(
                    float(
                        self.ambiente.nivel_nutrientes(
                            x,
                            y,
                        )
                    )
                )

        return self.obter_media(
            valores
        )

    @staticmethod
    def obter_media(
        valores: Iterable[float],
    ) -> float:
        """
        Calcula uma média segura.
        """

        lista = [
            float(
                valor
            )
            for valor in valores
        ]

        if not lista:
            return 0.0

        return (
            sum(lista)
            / len(lista)
        )

    # ========================================================
    # EVENTOS
    # ========================================================

    def registrar_evento(
        self,
        tipo: str,
        mensagem: str,
    ) -> None:
        """
        Registra um acontecimento relevante.
        """

        self.eventos.appendleft(
            {
                "tempo": self.tempo,
                "tipo": tipo,
                "mensagem": mensagem,
            }
        )

    def obter_eventos(
        self,
        limite: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Retorna os eventos mais recentes.
        """

        limite = max(
            0,
            int(
                limite
            ),
        )

        return list(
            self.eventos
        )[:limite]

    # ========================================================
    # RENDERIZAÇÃO
    # ========================================================

    def desenhar(
        self,
        tela: pygame.Surface,
    ) -> None:
        """
        Desenha o ambiente, carcaças e bactérias.
        """

        area_simulacao = pygame.Rect(
            0,
            0,
            AREA_SIMULACAO_LARGURA,
            ALTURA,
        )

        pygame.draw.rect(
            tela,
            self.obter_cor_de_fundo(),
            area_simulacao,
        )

        for carcaca in self.carcacas:
            carcaca.desenhar(
                tela
            )

        for bacteria in self.bacterias:
            bacteria.desenhar(
                tela
            )

    def obter_cor_de_fundo(
        self,
    ) -> tuple[int, int, int]:
        """
        Interpola suavemente o fundo conforme a intensidade da luz.
        """

        intensidade = max(
            0.0,
            min(
                1.0,
                float(
                    self.ambiente.intensidade_luz()
                ),
            ),
        )

        return tuple(
            int(
                FUNDO_NOITE[indice]
                + (
                    FUNDO_DIA[indice]
                    - FUNDO_NOITE[indice]
                )
                * intensidade
            )
            for indice in range(
                3
            )
        )

    # ========================================================
    # UTILITÁRIOS
    # ========================================================

    @staticmethod
    def limitar_x(
        x: float,
    ) -> float:
        return max(
            0.0,
            min(
                float(x),
                float(
                    AREA_SIMULACAO_LARGURA
                    - 1
                ),
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
                float(
                    ALTURA - 1
                ),
            ),
        )

    def __repr__(
        self,
    ) -> str:
        estatisticas = (
            self.obter_estatisticas()
        )

        return (
            "Mundo("
            f"tempo={self.tempo}, "
            f"bacterias={estatisticas['bacterias']}, "
            f"fotossinteticas="
            f"{estatisticas['fotossinteticas']}, "
            f"predadoras="
            f"{estatisticas['predadoras']}, "
            f"necrofagas="
            f"{estatisticas['necrofagas']}, "
            f"carcacas="
            f"{estatisticas['carcacas']}"
            ")"
        )
