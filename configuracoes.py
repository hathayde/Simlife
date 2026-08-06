# configuracoes.py
from __future__ import annotations


# ============================================================
# JANELA E ÁREA DA SIMULAÇÃO
# ============================================================

# Dimensão alinhada ao template padrão do Pygbag.
LARGURA = 1280
ALTURA = 720

# Área principal do ecossistema.
AREA_SIMULACAO_LARGURA = 880

# Painel lateral da interface.
PAINEL_LATERAL_LARGURA = (
    LARGURA - AREA_SIMULACAO_LARGURA
)

TITULO_JANELA = (
    "SimLife — Evolução Microbiana"
)

FPS = 30


# ============================================================
# CORES GERAIS
# ============================================================

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)

CINZA_ESCURO = (40, 40, 40)
CINZA_MEDIO = (100, 100, 100)
CINZA_CLARO = (180, 180, 180)

FUNDO_DIA = (8, 18, 24)
FUNDO_NOITE = (2, 5, 12)

COR_ALGA = (0, 120, 30)
COR_CARCACA = (139, 69, 19)
COR_PROTOZOARIO = (220, 50, 50)

COR_GRAFICO_BACTERIAS = (0, 255, 100)
COR_GRAFICO_ALGAS = (0, 150, 0)
COR_GRAFICO_PROTOZOARIOS = (255, 80, 80)


# ============================================================
# POPULAÇÕES
# ============================================================

MAX_BACTERIAS = 100
MAX_ALGAS = 500
MAX_PROTOZOARIOS = 20

BACTERIAS_INICIAIS = 10
ALGAS_INICIAIS = 500
PROTOZOARIOS_INICIAIS = 5

QUANTIDADE_REINTRODUCAO_ALGAS = 100


# ============================================================
# CICLO AMBIENTAL
# ============================================================

# Quantidade de atualizações entre dia e noite.
DURACAO_CICLO = 500

# Quantidade de atualizações de uma estação ambiental.
DURACAO_ESTACAO = 5000

TEMPERATURA_MEDIA = 25.0
UMIDADE_MEDIA = 0.70

INTENSIDADE_MINIMA_DIA = 0.15


# ============================================================
# ALGAS
# ============================================================

ENERGIA_INICIAL_ALGA = 100.0
ENERGIA_REPRODUCAO_ALGA = 120.0

GANHO_BASE_FOTOSSINTESE = 2.0
CUSTO_NOTURNO_ALGA = 0.1

TAMANHO_ALGA = 3
DISPERSAO_REPRODUCAO_ALGA = 8.0


# ============================================================
# BACTÉRIAS
# ============================================================

ENERGIA_INICIAL_BACTERIA = 100.0
ENERGIA_REPRODUCAO_BACTERIA = 200.0

CUSTO_MOVIMENTO_BACTERIA = 0.02
CUSTO_METABOLICO_BACTERIA = 0.008

ENERGIA_CONSUMO_ALGA = 30.0
ENERGIA_CONSUMO_CARCACA = 30.0
ENERGIA_PREDACAO_BACTERIA = 50.0

PENALIDADE_FALHA_PREDACAO = 10.0
PENALIDADE_SEM_ALIMENTO = 0.1

RAIO_DETECCAO_PADRAO = 100.0
RAIO_DETECCAO_MINIMO = 20.0
RAIO_DETECCAO_MAXIMO = 300.0

VELOCIDADE_MINIMA = 0.1
VELOCIDADE_MAXIMA = 5.0

TAMANHO_MINIMO_BACTERIA = 2
TAMANHO_MAXIMO_BACTERIA = 16

DEFESA_MINIMA = 0.05
DEFESA_MAXIMA = 10.0

ATAQUE_MINIMO = 0.05
ATAQUE_MAXIMO = 10.0

ESPERANCA_VIDA_MINIMA = 100

EFICIENCIA_METABOLICA_MINIMA = 0.25
EFICIENCIA_METABOLICA_MAXIMA = 2.5

TAXA_MUTACAO_MINIMA = 0.001
TAXA_MUTACAO_MAXIMA = 0.75


# ============================================================
# GENES INICIAIS DAS BACTÉRIAS
# ============================================================

VELOCIDADE_INICIAL_MINIMA = 0.5
VELOCIDADE_INICIAL_MAXIMA = 1.5

TAMANHO_INICIAL_MINIMO = 4
TAMANHO_INICIAL_MAXIMO = 6

ESPERANCA_VIDA_INICIAL_MINIMA = 1000
ESPERANCA_VIDA_INICIAL_MAXIMA = 2000

DEFESA_INICIAL_MINIMA = 0.1
DEFESA_INICIAL_MAXIMA = 1.0

ATAQUE_INICIAL_MINIMO = 0.1
ATAQUE_INICIAL_MAXIMO = 1.0

EFICIENCIA_METABOLICA_INICIAL_MINIMA = 0.75
EFICIENCIA_METABOLICA_INICIAL_MAXIMA = 1.25

RAIO_DETECCAO_INICIAL_MINIMO = 70.0
RAIO_DETECCAO_INICIAL_MAXIMO = 130.0

TAXA_MUTACAO_INICIAL_MINIMA = 0.05
TAXA_MUTACAO_INICIAL_MAXIMA = 0.20


# ============================================================
# MUTAÇÕES
# ============================================================

MUTACAO_VELOCIDADE_DESVIO = 0.15
MUTACAO_ESPERANCA_VIDA_MAXIMA = 150
MUTACAO_DEFESA_DESVIO = 0.12
MUTACAO_ATAQUE_DESVIO = 0.12
MUTACAO_EFICIENCIA_DESVIO = 0.08
MUTACAO_RAIO_DETECCAO_DESVIO = 8.0
MUTACAO_TAXA_MUTACAO_DESVIO = 0.015


# ============================================================
# MOVIMENTO
# ============================================================

RUIDO_BROWNIANO_INTELIGENTE = 0.08
RUIDO_BROWNIANO_PADRAO = 0.18

DISTANCIA_AMOSTRA_QUIMIOTAXIA = 14.0

INTENSIDADE_QUIMIOTAXIA_INTELIGENTE = 0.45
INTENSIDADE_QUIMIOTAXIA_PADRAO = 0.15

FATOR_REPULSAO = 0.10


# ============================================================
# CARCAÇAS
# ============================================================

ENERGIA_INICIAL_CARCACA = 30.0
ENERGIA_CARCACA_PROTOZOARIO = 20.0

TAMANHO_CARCACA = 3
DEGRADACAO_CARCACA_PADRAO = 0.05


# ============================================================
# PROTOZOÁRIOS
# ============================================================

ENERGIA_INICIAL_PROTOZOARIO = 200.0

ENERGIA_CONSUMO_BACTERIA_PROTOZOARIO = 50.0

TAMANHO_PROTOZOARIO = 8
VELOCIDADE_PROTOZOARIO = 1.0

CUSTO_MOVIMENTO_PROTOZOARIO = 0.025
CUSTO_METABOLICO_PROTOZOARIO = 0.1

RAIO_DETECCAO_PROTOZOARIO = 150.0

ESPERANCA_VIDA_PROTOZOARIO_MINIMA = 2500
ESPERANCA_VIDA_PROTOZOARIO_MAXIMA = 4500


# ============================================================
# QUADTREE
# ============================================================

QUADTREE_CAPACIDADE = 8
QUADTREE_PROFUNDIDADE_MAXIMA = 10


# ============================================================
# INTERFACE E HISTÓRICO
# ============================================================

# Mantida para compatibilidade com módulos antigos.
# O novo main.py utiliza pygame.font.Font(None, tamanho).
FONTE_PADRAO = "Arial"

TAMANHO_FONTE = 16
TAMANHO_FONTE_PEQUENA = 13
TAMANHO_FONTE_TITULO = 20

TAMANHO_HISTORICO = 300

MAX_ESPECIES_EXIBIDAS = 10

VELOCIDADE_SIMULACAO_MINIMA = 1
VELOCIDADE_SIMULACAO_MAXIMA = 8

VELOCIDADES_DISPONIVEIS = (
    1,
    2,
    4,
    8,
)


# ============================================================
# INTERAÇÃO
# ============================================================

# Distância mínima usada para selecionar organismos pequenos.
RAIO_MINIMO_SELECAO = 12.0

# Espaço adicional ao redor do organismo para facilitar o clique.
MARGEM_SELECAO_ORGANISMO = 8.0

# Quantidade de frames durante os quais mensagens ficam visíveis.
DURACAO_MENSAGEM_INTERFACE = 100


# ============================================================
# VALIDAÇÃO DAS CONFIGURAÇÕES
# ============================================================

def validar_configuracoes() -> None:
    """
    Valida os principais parâmetros do projeto.

    A função é executada automaticamente ao importar este módulo.
    """

    if LARGURA <= 0:
        raise ValueError(
            "LARGURA deve ser maior que zero."
        )

    if ALTURA <= 0:
        raise ValueError(
            "ALTURA deve ser maior que zero."
        )

    if AREA_SIMULACAO_LARGURA <= 0:
        raise ValueError(
            "AREA_SIMULACAO_LARGURA deve ser maior que zero."
        )

    if AREA_SIMULACAO_LARGURA >= LARGURA:
        raise ValueError(
            "AREA_SIMULACAO_LARGURA deve ser menor que LARGURA."
        )

    if PAINEL_LATERAL_LARGURA <= 0:
        raise ValueError(
            "PAINEL_LATERAL_LARGURA deve ser maior que zero."
        )

    if (
        AREA_SIMULACAO_LARGURA
        + PAINEL_LATERAL_LARGURA
        != LARGURA
    ):
        raise ValueError(
            "A área da simulação e o painel devem completar "
            "a largura total da janela."
        )

    if FPS <= 0:
        raise ValueError(
            "FPS deve ser maior que zero."
        )

    if MAX_BACTERIAS < 0:
        raise ValueError(
            "MAX_BACTERIAS não pode ser negativo."
        )

    if MAX_ALGAS < 0:
        raise ValueError(
            "MAX_ALGAS não pode ser negativo."
        )

    if MAX_PROTOZOARIOS < 0:
        raise ValueError(
            "MAX_PROTOZOARIOS não pode ser negativo."
        )

    if BACTERIAS_INICIAIS < 0:
        raise ValueError(
            "BACTERIAS_INICIAIS não pode ser negativo."
        )

    if ALGAS_INICIAIS < 0:
        raise ValueError(
            "ALGAS_INICIAIS não pode ser negativo."
        )

    if PROTOZOARIOS_INICIAIS < 0:
        raise ValueError(
            "PROTOZOARIOS_INICIAIS não pode ser negativo."
        )

    if BACTERIAS_INICIAIS > MAX_BACTERIAS:
        raise ValueError(
            "BACTERIAS_INICIAIS não pode exceder "
            "MAX_BACTERIAS."
        )

    if ALGAS_INICIAIS > MAX_ALGAS:
        raise ValueError(
            "ALGAS_INICIAIS não pode exceder MAX_ALGAS."
        )

    if PROTOZOARIOS_INICIAIS > MAX_PROTOZOARIOS:
        raise ValueError(
            "PROTOZOARIOS_INICIAIS não pode exceder "
            "MAX_PROTOZOARIOS."
        )

    if QUANTIDADE_REINTRODUCAO_ALGAS < 0:
        raise ValueError(
            "QUANTIDADE_REINTRODUCAO_ALGAS não pode ser negativa."
        )

    if DURACAO_CICLO <= 0:
        raise ValueError(
            "DURACAO_CICLO deve ser maior que zero."
        )

    if DURACAO_ESTACAO <= 0:
        raise ValueError(
            "DURACAO_ESTACAO deve ser maior que zero."
        )

    if not 0.0 <= UMIDADE_MEDIA <= 1.0:
        raise ValueError(
            "UMIDADE_MEDIA deve estar entre 0 e 1."
        )

    if not 0.0 <= INTENSIDADE_MINIMA_DIA <= 1.0:
        raise ValueError(
            "INTENSIDADE_MINIMA_DIA deve estar entre 0 e 1."
        )

    if ENERGIA_REPRODUCAO_ALGA <= 0:
        raise ValueError(
            "ENERGIA_REPRODUCAO_ALGA deve ser maior que zero."
        )

    if ENERGIA_REPRODUCAO_BACTERIA <= 0:
        raise ValueError(
            "ENERGIA_REPRODUCAO_BACTERIA deve ser maior que zero."
        )

    if TAMANHO_MINIMO_BACTERIA < 1:
        raise ValueError(
            "TAMANHO_MINIMO_BACTERIA deve ser pelo menos 1."
        )

    if (
        TAMANHO_MAXIMO_BACTERIA
        < TAMANHO_MINIMO_BACTERIA
    ):
        raise ValueError(
            "TAMANHO_MAXIMO_BACTERIA deve ser maior ou igual "
            "a TAMANHO_MINIMO_BACTERIA."
        )

    if VELOCIDADE_MINIMA <= 0:
        raise ValueError(
            "VELOCIDADE_MINIMA deve ser maior que zero."
        )

    if VELOCIDADE_MAXIMA < VELOCIDADE_MINIMA:
        raise ValueError(
            "VELOCIDADE_MAXIMA deve ser maior ou igual "
            "a VELOCIDADE_MINIMA."
        )

    if DEFESA_MAXIMA < DEFESA_MINIMA:
        raise ValueError(
            "DEFESA_MAXIMA deve ser maior ou igual "
            "a DEFESA_MINIMA."
        )

    if ATAQUE_MAXIMO < ATAQUE_MINIMO:
        raise ValueError(
            "ATAQUE_MAXIMO deve ser maior ou igual "
            "a ATAQUE_MINIMO."
        )

    if (
        EFICIENCIA_METABOLICA_MAXIMA
        < EFICIENCIA_METABOLICA_MINIMA
    ):
        raise ValueError(
            "EFICIENCIA_METABOLICA_MAXIMA deve ser maior "
            "ou igual à mínima."
        )

    if TAXA_MUTACAO_MINIMA < 0:
        raise ValueError(
            "TAXA_MUTACAO_MINIMA não pode ser negativa."
        )

    if TAXA_MUTACAO_MAXIMA > 1:
        raise ValueError(
            "TAXA_MUTACAO_MAXIMA não pode ser maior que 1."
        )

    if TAXA_MUTACAO_MAXIMA < TAXA_MUTACAO_MINIMA:
        raise ValueError(
            "TAXA_MUTACAO_MAXIMA deve ser maior ou igual "
            "a TAXA_MUTACAO_MINIMA."
        )

    if QUADTREE_CAPACIDADE < 1:
        raise ValueError(
            "QUADTREE_CAPACIDADE deve ser maior ou igual a 1."
        )

    if QUADTREE_PROFUNDIDADE_MAXIMA < 0:
        raise ValueError(
            "QUADTREE_PROFUNDIDADE_MAXIMA não pode ser negativa."
        )

    if VELOCIDADE_SIMULACAO_MINIMA < 1:
        raise ValueError(
            "VELOCIDADE_SIMULACAO_MINIMA deve ser pelo menos 1."
        )

    if (
        VELOCIDADE_SIMULACAO_MAXIMA
        < VELOCIDADE_SIMULACAO_MINIMA
    ):
        raise ValueError(
            "VELOCIDADE_SIMULACAO_MAXIMA deve ser maior ou igual "
            "à velocidade mínima."
        )

    if not VELOCIDADES_DISPONIVEIS:
        raise ValueError(
            "VELOCIDADES_DISPONIVEIS não pode estar vazio."
        )

    if any(
        velocidade < VELOCIDADE_SIMULACAO_MINIMA
        or velocidade > VELOCIDADE_SIMULACAO_MAXIMA
        for velocidade in VELOCIDADES_DISPONIVEIS
    ):
        raise ValueError(
            "Todas as velocidades disponíveis devem estar dentro "
            "dos limites configurados."
        )

    if RAIO_MINIMO_SELECAO <= 0:
        raise ValueError(
            "RAIO_MINIMO_SELECAO deve ser maior que zero."
        )

    if MARGEM_SELECAO_ORGANISMO < 0:
        raise ValueError(
            "MARGEM_SELECAO_ORGANISMO não pode ser negativa."
        )

    if DURACAO_MENSAGEM_INTERFACE < 0:
        raise ValueError(
            "DURACAO_MENSAGEM_INTERFACE não pode ser negativa."
        )


validar_configuracoes()
