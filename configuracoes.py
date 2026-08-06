# configuracoes.py
from __future__ import annotations


# ============================================================
# JANELA E ÁREA DA SIMULAÇÃO
# ============================================================

LARGURA = 1280
ALTURA = 720

AREA_SIMULACAO_LARGURA = 880
PAINEL_LATERAL_LARGURA = LARGURA - AREA_SIMULACAO_LARGURA

TITULO_JANELA = "SimLife — Ecossistema Bacteriano"

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

COR_CARCACA = (139, 89, 45)

COR_GRAFICO_FOTOSSINTETICAS = (
    80,
    220,
    110,
)

COR_GRAFICO_PREDADORAS = (
    245,
    90,
    90,
)

COR_GRAFICO_NECROFAGAS = (
    230,
    180,
    70,
)

COR_DESTAQUE_SELECAO = (
    255,
    220,
    70,
)


# ============================================================
# ESTRATÉGIAS ALIMENTARES
# ============================================================

ESTRATEGIA_FOTOSSINTESE = "fotossintese"
ESTRATEGIA_PREDACAO = "predacao"
ESTRATEGIA_NECROFAGIA = "necrofagia"

ESTRATEGIAS_ALIMENTARES = (
    ESTRATEGIA_FOTOSSINTESE,
    ESTRATEGIA_PREDACAO,
    ESTRATEGIA_NECROFAGIA,
)

CORES_ESTRATEGIAS = {
    ESTRATEGIA_FOTOSSINTESE: (
        80,
        220,
        110,
    ),
    ESTRATEGIA_PREDACAO: (
        245,
        90,
        90,
    ),
    ESTRATEGIA_NECROFAGIA: (
        230,
        180,
        70,
    ),
}

NOMES_ESTRATEGIAS = {
    ESTRATEGIA_FOTOSSINTESE: (
        "Fotossintética"
    ),
    ESTRATEGIA_PREDACAO: (
        "Predadora"
    ),
    ESTRATEGIA_NECROFAGIA: (
        "Necrófaga"
    ),
}


# ============================================================
# POPULAÇÕES
# ============================================================

MAX_BACTERIAS = 500
MAX_CARCACAS = 700

BACTERIAS_FOTOSSINTETICAS_INICIAIS = 40
BACTERIAS_PREDADORAS_INICIAIS = 8
BACTERIAS_NECROFAGAS_INICIAIS = 7

BACTERIAS_INICIAIS = (
    BACTERIAS_FOTOSSINTETICAS_INICIAIS
    + BACTERIAS_PREDADORAS_INICIAIS
    + BACTERIAS_NECROFAGAS_INICIAIS
)


# ============================================================
# CICLO AMBIENTAL
# ============================================================

DURACAO_CICLO = 500
DURACAO_ESTACAO = 5000

TEMPERATURA_MEDIA = 25.0
UMIDADE_MEDIA = 0.70

INTENSIDADE_LUZ_DIA = 1.0
INTENSIDADE_LUZ_NOITE = 0.05

INTENSIDADE_MINIMA_FOTOSSINTESE = 0.15


# ============================================================
# NUTRIENTES DO AMBIENTE
# ============================================================

TAMANHO_CELULA_NUTRIENTES = 40

NIVEL_NUTRIENTES_INICIAL = 0.75
NIVEL_NUTRIENTES_MINIMO = 0.0
NIVEL_NUTRIENTES_MAXIMO = 1.0

VARIACAO_INICIAL_NUTRIENTES = 0.20

REGENERACAO_NATURAL_NUTRIENTES = 0.0005

CONSUMO_NUTRIENTES_FOTOSSINTESE = 0.004

RETORNO_NUTRIENTES_DECOMPOSICAO = 0.35

RAIO_DISTRIBUICAO_NUTRIENTES = 35.0


# ============================================================
# ENERGIA DAS BACTÉRIAS
# ============================================================

ENERGIA_INICIAL_BACTERIA = 100.0
ENERGIA_MAXIMA_BACTERIA = 400.0

ENERGIA_REPRODUCAO_BACTERIA = 200.0

# Fração da energia comprometida durante a divisão.
CUSTO_REPRODUCAO_BACTERIA = 0.50

ENERGIA_MINIMA_SOBREVIVENCIA = 0.0

CUSTO_MOVIMENTO_BACTERIA = 0.02
CUSTO_METABOLICO_BACTERIA = 0.008

PENALIDADE_SEM_ALIMENTO = 0.10


# ============================================================
# FOTOSSÍNTESE
# ============================================================

GANHO_BASE_FOTOSSINTESE = 1.80

EFICIENCIA_FOTOSSINTESE_MINIMA = 0.40
EFICIENCIA_FOTOSSINTESE_MAXIMA = 2.00

CUSTO_NOTURNO_FOTOSSINTETICA = 0.06

MOVIMENTO_FOTOSSINTETICA_MINIMO = 0.25
MOVIMENTO_FOTOSSINTETICA_MAXIMO = 1.50


# ============================================================
# PREDAÇÃO
# ============================================================

ENERGIA_PREDACAO_BACTERIA = 65.0

PENALIDADE_FALHA_PREDACAO = 8.0

RAIO_CACA_PADRAO = 110.0

TEMPO_RECUPERACAO_ATAQUE = 12

DISTANCIA_MAXIMA_CONTATO_PREDACAO = 2.0

PREDADOR_PODE_ATACAR_MESMA_ESPECIE = False


# ============================================================
# NECROFAGIA
# ============================================================

EFICIENCIA_CONSUMO_CARCACA = 0.85

RAIO_BUSCA_CARCACA_PADRAO = 120.0

CONSUMO_MAXIMO_CARCACA_POR_FRAME = 8.0

ENERGIA_MINIMA_CARCACA_CONSUMIVEL = 0.5


# ============================================================
# CARCAÇAS
# ============================================================

ENERGIA_INICIAL_CARCACA = 40.0

TAMANHO_CARCACA = 4

DEGRADACAO_CARCACA_PADRAO = 0.04

ENERGIA_MINIMA_CARCACA = 0.1


# ============================================================
# GENES DAS BACTÉRIAS
# ============================================================

VELOCIDADE_MINIMA = 0.10
VELOCIDADE_MAXIMA = 5.00

VELOCIDADE_INICIAL_MINIMA = 0.50
VELOCIDADE_INICIAL_MAXIMA = 1.50

TAMANHO_MINIMO_BACTERIA = 2
TAMANHO_MAXIMO_BACTERIA = 16

TAMANHO_INICIAL_MINIMO = 4
TAMANHO_INICIAL_MAXIMO = 6

ESPERANCA_VIDA_MINIMA = 100

ESPERANCA_VIDA_INICIAL_MINIMA = 1200
ESPERANCA_VIDA_INICIAL_MAXIMA = 2400

DEFESA_MINIMA = 0.05
DEFESA_MAXIMA = 10.0

DEFESA_INICIAL_MINIMA = 0.10
DEFESA_INICIAL_MAXIMA = 1.00

ATAQUE_MINIMO = 0.05
ATAQUE_MAXIMO = 10.0

ATAQUE_INICIAL_MINIMO = 0.10
ATAQUE_INICIAL_MAXIMO = 1.00

EFICIENCIA_METABOLICA_MINIMA = 0.25
EFICIENCIA_METABOLICA_MAXIMA = 2.50

EFICIENCIA_METABOLICA_INICIAL_MINIMA = 0.75
EFICIENCIA_METABOLICA_INICIAL_MAXIMA = 1.25

RAIO_DETECCAO_MINIMO = 20.0
RAIO_DETECCAO_MAXIMO = 300.0

RAIO_DETECCAO_INICIAL_MINIMO = 70.0
RAIO_DETECCAO_INICIAL_MAXIMO = 130.0

TAXA_MUTACAO_MINIMA = 0.001
TAXA_MUTACAO_MAXIMA = 0.75

TAXA_MUTACAO_INICIAL_MINIMA = 0.03
TAXA_MUTACAO_INICIAL_MAXIMA = 0.12

EFICIENCIA_FOTOSSINTESE_INICIAL_MINIMA = 0.80
EFICIENCIA_FOTOSSINTESE_INICIAL_MAXIMA = 1.20


# ============================================================
# MUTAÇÕES
# ============================================================

MUTACAO_VELOCIDADE_DESVIO = 0.15
MUTACAO_TAMANHO_MAXIMA = 1

MUTACAO_ESPERANCA_VIDA_MAXIMA = 150

MUTACAO_DEFESA_DESVIO = 0.12
MUTACAO_ATAQUE_DESVIO = 0.12

MUTACAO_EFICIENCIA_METABOLICA_DESVIO = 0.08

MUTACAO_EFICIENCIA_FOTOSSINTESE_DESVIO = 0.08

MUTACAO_RAIO_DETECCAO_DESVIO = 8.0

MUTACAO_TAXA_MUTACAO_DESVIO = 0.015

# Mudanças de estratégia devem ser raras para preservar
# especializações ecológicas.
PROBABILIDADE_MUTACAO_ESTRATEGIA = 0.002

PROBABILIDADE_MUTACAO_ESPECIE_ALVO = 0.01

DISTANCIA_GENETICA_NOVA_ESPECIE = 0.35


# ============================================================
# REPRODUÇÃO
# ============================================================

# Bactérias se reproduzem por divisão assexuada.
REPRODUCAO_ASSEXUADA = True

DISTANCIA_MAXIMA_DESCENDENTE = 7.0

DIVISAO_ENERGIA_REPRODUCAO = 0.50

PROBABILIDADE_REPRODUCAO_POR_FRAME = 1.0


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
# QUADTREE
# ============================================================

QUADTREE_CAPACIDADE = 8

QUADTREE_PROFUNDIDADE_MAXIMA = 10


# ============================================================
# INTERFACE E HISTÓRICO
# ============================================================

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

RAIO_MINIMO_SELECAO = 12.0

MARGEM_SELECAO_ORGANISMO = 8.0

DURACAO_MENSAGEM_INTERFACE = 100


# ============================================================
# EVENTOS DA SIMULAÇÃO
# ============================================================

MAX_EVENTOS_REGISTRADOS = 100

INTERVALO_ANALISE_EVENTOS = 60

LIMIAR_QUEDA_POPULACIONAL = 0.40

LIMIAR_DOMINANCIA_ESTRATEGIA = 0.70

LIMIAR_NUTRIENTES_CRITICOS = 0.15


# ============================================================
# VALIDAÇÃO DAS CONFIGURAÇÕES
# ============================================================

def validar_configuracoes() -> None:
    """
    Valida os principais parâmetros antes da simulação começar.
    """

    if LARGURA <= 0 or ALTURA <= 0:
        raise ValueError(
            "LARGURA e ALTURA devem ser maiores que zero."
        )

    if not (
        0
        < AREA_SIMULACAO_LARGURA
        < LARGURA
    ):
        raise ValueError(
            "AREA_SIMULACAO_LARGURA deve estar "
            "entre 0 e LARGURA."
        )

    if PAINEL_LATERAL_LARGURA <= 0:
        raise ValueError(
            "PAINEL_LATERAL_LARGURA deve ser "
            "maior que zero."
        )

    if (
        AREA_SIMULACAO_LARGURA
        + PAINEL_LATERAL_LARGURA
        != LARGURA
    ):
        raise ValueError(
            "A área da simulação e o painel devem "
            "completar a largura total."
        )

    if FPS <= 0:
        raise ValueError(
            "FPS deve ser maior que zero."
        )

    if not ESTRATEGIAS_ALIMENTARES:
        raise ValueError(
            "ESTRATEGIAS_ALIMENTARES não pode "
            "estar vazio."
        )

    if (
        len(
            set(
                ESTRATEGIAS_ALIMENTARES
            )
        )
        != len(
            ESTRATEGIAS_ALIMENTARES
        )
    ):
        raise ValueError(
            "As estratégias alimentares devem ser únicas."
        )

    if (
        set(
            CORES_ESTRATEGIAS
        )
        != set(
            ESTRATEGIAS_ALIMENTARES
        )
    ):
        raise ValueError(
            "CORES_ESTRATEGIAS deve conter "
            "todas as estratégias."
        )

    if (
        set(
            NOMES_ESTRATEGIAS
        )
        != set(
            ESTRATEGIAS_ALIMENTARES
        )
    ):
        raise ValueError(
            "NOMES_ESTRATEGIAS deve conter "
            "todas as estratégias."
        )

    if MAX_BACTERIAS < 1:
        raise ValueError(
            "MAX_BACTERIAS deve ser pelo menos 1."
        )

    if MAX_CARCACAS < 0:
        raise ValueError(
            "MAX_CARCACAS não pode ser negativo."
        )

    populacoes_iniciais = (
        BACTERIAS_FOTOSSINTETICAS_INICIAIS,
        BACTERIAS_PREDADORAS_INICIAIS,
        BACTERIAS_NECROFAGAS_INICIAIS,
    )

    if any(
        quantidade < 0
        for quantidade in populacoes_iniciais
    ):
        raise ValueError(
            "As populações iniciais não podem "
            "ser negativas."
        )

    if BACTERIAS_INICIAIS > MAX_BACTERIAS:
        raise ValueError(
            "BACTERIAS_INICIAIS não pode exceder "
            "MAX_BACTERIAS."
        )

    if (
        DURACAO_CICLO <= 0
        or DURACAO_ESTACAO <= 0
    ):
        raise ValueError(
            "DURACAO_CICLO e DURACAO_ESTACAO "
            "devem ser positivos."
        )

    if not 0.0 <= UMIDADE_MEDIA <= 1.0:
        raise ValueError(
            "UMIDADE_MEDIA deve estar entre 0 e 1."
        )

    if not 0.0 <= INTENSIDADE_LUZ_DIA <= 1.0:
        raise ValueError(
            "INTENSIDADE_LUZ_DIA deve estar "
            "entre 0 e 1."
        )

    if not 0.0 <= INTENSIDADE_LUZ_NOITE <= 1.0:
        raise ValueError(
            "INTENSIDADE_LUZ_NOITE deve estar "
            "entre 0 e 1."
        )

    if (
        INTENSIDADE_LUZ_NOITE
        > INTENSIDADE_LUZ_DIA
    ):
        raise ValueError(
            "A luz noturna não pode superar "
            "a luz diurna."
        )

    if not (
        0.0
        <= INTENSIDADE_MINIMA_FOTOSSINTESE
        <= 1.0
    ):
        raise ValueError(
            "INTENSIDADE_MINIMA_FOTOSSINTESE "
            "deve estar entre 0 e 1."
        )

    if TAMANHO_CELULA_NUTRIENTES < 1:
        raise ValueError(
            "TAMANHO_CELULA_NUTRIENTES deve ser "
            "pelo menos 1."
        )

    if not (
        NIVEL_NUTRIENTES_MINIMO
        <= NIVEL_NUTRIENTES_INICIAL
        <= NIVEL_NUTRIENTES_MAXIMO
    ):
        raise ValueError(
            "NIVEL_NUTRIENTES_INICIAL deve estar "
            "dentro dos limites."
        )

    if VARIACAO_INICIAL_NUTRIENTES < 0:
        raise ValueError(
            "VARIACAO_INICIAL_NUTRIENTES não pode "
            "ser negativa."
        )

    if ENERGIA_INICIAL_BACTERIA <= 0:
        raise ValueError(
            "ENERGIA_INICIAL_BACTERIA deve ser "
            "maior que zero."
        )

    if (
        ENERGIA_MAXIMA_BACTERIA
        < ENERGIA_INICIAL_BACTERIA
    ):
        raise ValueError(
            "ENERGIA_MAXIMA_BACTERIA deve ser "
            "maior ou igual à inicial."
        )

    if ENERGIA_REPRODUCAO_BACTERIA <= 0:
        raise ValueError(
            "ENERGIA_REPRODUCAO_BACTERIA deve ser "
            "maior que zero."
        )

    if not (
        0.0
        < CUSTO_REPRODUCAO_BACTERIA
        < 1.0
    ):
        raise ValueError(
            "CUSTO_REPRODUCAO_BACTERIA deve estar "
            "entre 0 e 1."
        )

    if not (
        0.0
        < DIVISAO_ENERGIA_REPRODUCAO
        < 1.0
    ):
        raise ValueError(
            "DIVISAO_ENERGIA_REPRODUCAO deve estar "
            "entre 0 e 1."
        )

    if not (
        0.0
        <= PROBABILIDADE_REPRODUCAO_POR_FRAME
        <= 1.0
    ):
        raise ValueError(
            "PROBABILIDADE_REPRODUCAO_POR_FRAME "
            "deve estar entre 0 e 1."
        )

    if (
        VELOCIDADE_MINIMA <= 0
        or VELOCIDADE_MAXIMA
        < VELOCIDADE_MINIMA
    ):
        raise ValueError(
            "Os limites de velocidade são inválidos."
        )

    if (
        TAMANHO_MINIMO_BACTERIA < 1
        or TAMANHO_MAXIMO_BACTERIA
        < TAMANHO_MINIMO_BACTERIA
    ):
        raise ValueError(
            "Os limites de tamanho das bactérias "
            "são inválidos."
        )

    if DEFESA_MAXIMA < DEFESA_MINIMA:
        raise ValueError(
            "DEFESA_MAXIMA deve ser maior ou "
            "igual à mínima."
        )

    if ATAQUE_MAXIMO < ATAQUE_MINIMO:
        raise ValueError(
            "ATAQUE_MAXIMO deve ser maior ou "
            "igual ao mínimo."
        )

    if (
        EFICIENCIA_METABOLICA_MAXIMA
        < EFICIENCIA_METABOLICA_MINIMA
    ):
        raise ValueError(
            "Os limites de eficiência metabólica "
            "são inválidos."
        )

    if (
        EFICIENCIA_FOTOSSINTESE_MAXIMA
        < EFICIENCIA_FOTOSSINTESE_MINIMA
    ):
        raise ValueError(
            "Os limites de eficiência fotossintética "
            "são inválidos."
        )

    if (
        TAXA_MUTACAO_MINIMA < 0
        or TAXA_MUTACAO_MAXIMA > 1
    ):
        raise ValueError(
            "As taxas de mutação devem estar "
            "entre 0 e 1."
        )

    if (
        TAXA_MUTACAO_MAXIMA
        < TAXA_MUTACAO_MINIMA
    ):
        raise ValueError(
            "TAXA_MUTACAO_MAXIMA deve ser maior "
            "ou igual à mínima."
        )

    probabilidades = (
        PROBABILIDADE_MUTACAO_ESTRATEGIA,
        PROBABILIDADE_MUTACAO_ESPECIE_ALVO,
    )

    if any(
        not 0.0 <= probabilidade <= 1.0
        for probabilidade in probabilidades
    ):
        raise ValueError(
            "As probabilidades de mutação devem "
            "estar entre 0 e 1."
        )

    if QUADTREE_CAPACIDADE < 1:
        raise ValueError(
            "QUADTREE_CAPACIDADE deve ser pelo menos 1."
        )

    if QUADTREE_PROFUNDIDADE_MAXIMA < 0:
        raise ValueError(
            "QUADTREE_PROFUNDIDADE_MAXIMA não pode "
            "ser negativa."
        )

    if not VELOCIDADES_DISPONIVEIS:
        raise ValueError(
            "VELOCIDADES_DISPONIVEIS não pode "
            "estar vazio."
        )

    if any(
        velocidade < VELOCIDADE_SIMULACAO_MINIMA
        or velocidade > VELOCIDADE_SIMULACAO_MAXIMA
        for velocidade in VELOCIDADES_DISPONIVEIS
    ):
        raise ValueError(
            "As velocidades disponíveis devem "
            "respeitar os limites."
        )

    if RAIO_MINIMO_SELECAO <= 0:
        raise ValueError(
            "RAIO_MINIMO_SELECAO deve ser "
            "maior que zero."
        )

    if MARGEM_SELECAO_ORGANISMO < 0:
        raise ValueError(
            "MARGEM_SELECAO_ORGANISMO não pode "
            "ser negativa."
        )


validar_configuracoes()
