```python
# ambiente.py
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from configuracoes import (
    ALTURA,
    AREA_SIMULACAO_LARGURA,
)


@dataclass(slots=True)
class CondicoesAmbientais:
    """
    Representa as condições globais do ambiente em um instante da simulação.
    """

    ciclo_luz: str
    intensidade_luz: float
    temperatura: float
    umidade: float
    fator_sazonal: float


class Ambiente:
    """
    Gerencia as condições ambientais da simulação.

    O ambiente controla:

    - intensidade da luz;
    - transição entre dia e noite;
    - temperatura;
    - umidade;
    - distribuição espacial de nutrientes;
    - variação sazonal;
    - pequenas flutuações ambientais.
    """

    def __init__(
        self,
        duracao_ciclo: int = 500,
        duracao_estacao: int = 5000,
        temperatura_media: float = 25.0,
        umidade_media: float = 0.70,
        semente: int | None = None,
    ) -> None:
        if duracao_ciclo <= 0:
            raise ValueError("duracao_ciclo deve ser maior que zero.")

        if duracao_estacao <= 0:
            raise ValueError("duracao_estacao deve ser maior que zero.")

        self.duracao_ciclo = duracao_ciclo
        self.duracao_estacao = duracao_estacao

        self.temperatura_media = temperatura_media
        self.umidade_media = self.limitar(
            umidade_media,
            0.0,
            1.0,
        )

        self.tempo = 0

        self._gerador = random.Random(semente)

        self._ruido_temperatura = 0.0
        self._ruido_umidade = 0.0

        self._centros_nutrientes = self._criar_centros_nutrientes()

    def atualizar(self, passos: int = 1) -> None:
        """
        Avança o ambiente pelo número informado de passos.
        """

        if passos < 1:
            raise ValueError("passos deve ser maior ou igual a 1.")

        for _ in range(passos):
            self.tempo += 1
            self._atualizar_ruidos()

    def obter_condicoes(self) -> CondicoesAmbientais:
        """
        Retorna um retrato das condições ambientais atuais.
        """

        intensidade_luz = self.intensidade_luz()
        fator_sazonal = self.fator_sazonal()

        return CondicoesAmbientais(
            ciclo_luz=self.ciclo_luz(),
            intensidade_luz=intensidade_luz,
            temperatura=self.temperatura(),
            umidade=self.umidade(),
            fator_sazonal=fator_sazonal,
        )

    def ciclo_luz(self) -> str:
        """
        Retorna 'dia' ou 'noite' conforme a intensidade luminosa atual.
        """

        return "dia" if self.intensidade_luz() >= 0.15 else "noite"

    def intensidade_luz(self) -> float:
        """
        Retorna a intensidade de luz entre 0 e 1.

        A transição é gradual, evitando mudança abrupta entre dia e noite.
        """

        duracao_periodo_completo = self.duracao_ciclo * 2

        fase = (
            self.tempo % duracao_periodo_completo
        ) / duracao_periodo_completo

        valor = math.sin(
            2.0 * math.pi * fase
        )

        intensidade = max(0.0, valor)

        intensidade *= self.fator_sazonal()

        return self.limitar(
            intensidade,
            0.0,
            1.0,
        )

    def fator_sazonal(self) -> float:
        """
        Simula variações sazonais na disponibilidade de luz.

        O valor varia aproximadamente entre 0.75 e 1.0.
        """

        fase = (
            self.tempo % self.duracao_estacao
        ) / self.duracao_estacao

        oscilacao = (
            math.sin(2.0 * math.pi * fase) + 1.0
        ) / 2.0

        return 0.75 + oscilacao * 0.25

    def temperatura(self) -> float:
        """
        Retorna a temperatura atual em graus Celsius.
        """

        componente_diurno = (
            self.intensidade_luz() - 0.5
        ) * 6.0

        componente_sazonal = (
            self.fator_sazonal() - 0.875
        ) * 12.0

        return (
            self.temperatura_media
            + componente_diurno
            + componente_sazonal
            + self._ruido_temperatura
        )

    def umidade(self) -> float:
        """
        Retorna a umidade relativa normalizada entre 0 e 1.
        """

        perda_por_luz = self.intensidade_luz() * 0.12

        ganho_noturno = (
            1.0 - self.intensidade_luz()
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

    def nivel_nutrientes(
        self,
        x: float,
        y: float,
    ) -> float:
        """
        Calcula a disponibilidade de nutrientes em uma posição.

        O valor final fica entre 0 e 1.
        """

        x = self.limitar(
            x,
            0.0,
            float(AREA_SIMULACAO_LARGURA),
        )

        y = self.limitar(
            y,
            0.0,
            float(ALTURA),
        )

        nutrientes_base = 0.10

        maior_concentracao = 0.0

        for centro_x, centro_y, intensidade, raio in self._centros_nutrientes:
            dx = x - centro_x
            dy = y - centro_y

            distancia_quadrada = dx * dx + dy * dy
            raio_quadrado = raio * raio

            concentracao = intensidade * math.exp(
                -distancia_quadrada
                / max(2.0 * raio_quadrado, 1.0)
            )

            maior_concentracao = max(
                maior_concentracao,
                concentracao,
            )

        gradiente_central = self._gradiente_central(
            x,
            y,
        )

        variacao_espacial = self._variacao_espacial(
            x,
            y,
        )

        valor = (
            nutrientes_base
            + maior_concentracao
            + gradiente_central * 0.20
            + variacao_espacial * 0.08
        )

        return self.limitar(
            valor,
            0.0,
            1.0,
        )

    def fator_fotossintese(
        self,
        x: float,
        y: float,
    ) -> float:
        """
        Retorna um multiplicador para a fotossíntese.

        Considera luz, nutrientes, temperatura e umidade.
        """

        luz = self.intensidade_luz()
        nutrientes = self.nivel_nutrientes(x, y)
        temperatura = self.temperatura()
        umidade = self.umidade()

        fator_temperatura = self.fator_temperatura(
            temperatura,
            temperatura_otima=26.0,
            tolerancia=15.0,
        )

        fator_umidade = self.fator_umidade(
            umidade,
            umidade_otima=0.75,
            tolerancia=0.60,
        )

        return (
            luz
            * nutrientes
            * fator_temperatura
            * fator_umidade
        )

    def fator_metabolico(self) -> float:
        """
        Retorna um multiplicador metabólico global.

        Temperaturas muito baixas ou muito altas reduzem a atividade.
        """

        temperatura = self.temperatura()

        return self.fator_temperatura(
            temperatura,
            temperatura_otima=28.0,
            tolerancia=20.0,
        )

    def custo_metabolico(self) -> float:
        """
        Retorna o custo energético basal sugerido por passo.
        """

        temperatura = self.temperatura()
        umidade = self.umidade()

        custo = 0.015

        if temperatura < 10.0:
            custo += 0.010

        if temperatura > 38.0:
            custo += 0.020

        if umidade < 0.30:
            custo += 0.015

        return custo

    def degradacao_carcaca(self) -> float:
        """
        Calcula a taxa de degradação de carcaças.

        Ambientes quentes e úmidos aceleram a decomposição.
        """

        temperatura = self.temperatura()
        umidade = self.umidade()

        fator_temperatura = self.limitar(
            (temperatura - 5.0) / 35.0,
            0.1,
            1.5,
        )

        fator_umidade = self.limitar(
            umidade / 0.70,
            0.2,
            1.5,
        )

        return 0.03 * fator_temperatura * fator_umidade

    def regenerar_centros_nutrientes(self) -> None:
        """
        Gera uma nova distribuição espacial de nutrientes.
        """

        self._centros_nutrientes = self._criar_centros_nutrientes()

    def obter_centros_nutrientes(
        self,
    ) -> tuple[tuple[float, float, float, float], ...]:
        """
        Retorna uma cópia imutável dos centros de nutrientes.

        Cada item possui:
        x, y, intensidade e raio.
        """

        return tuple(self._centros_nutrientes)

    def _criar_centros_nutrientes(
        self,
    ) -> list[tuple[float, float, float, float]]:
        """
        Cria manchas de nutrientes espalhadas pelo mapa.
        """

        quantidade = 6

        centros: list[
            tuple[float, float, float, float]
        ] = []

        for _ in range(quantidade):
            x = self._gerador.uniform(
                0,
                AREA_SIMULACAO_LARGURA,
            )

            y = self._gerador.uniform(
                0,
                ALTURA,
            )

            intensidade = self._gerador.uniform(
                0.35,
                0.85,
            )

            raio = self._gerador.uniform(
                80.0,
                220.0,
            )

            centros.append(
                (
                    x,
                    y,
                    intensidade,
                    raio,
                )
            )

        return centros

    def _atualizar_ruidos(self) -> None:
        """
        Atualiza pequenas flutuações ambientais de forma gradual.
        """

        alvo_temperatura = self._gerador.uniform(
            -1.5,
            1.5,
        )

        alvo_umidade = self._gerador.uniform(
            -0.04,
            0.04,
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
        Retorna um gradiente suave com maior valor no centro do mapa.
        """

        centro_x = AREA_SIMULACAO_LARGURA / 2.0
        centro_y = ALTURA / 2.0

        distancia = math.hypot(
            x - centro_x,
            y - centro_y,
        )

        distancia_maxima = math.hypot(
            centro_x,
            centro_y,
        )

        if distancia_maxima <= 0:
            return 0.0

        return max(
            0.0,
            1.0 - distancia / distancia_maxima,
        )

    @staticmethod
    def _variacao_espacial(
        x: float,
        y: float,
    ) -> float:
        """
        Gera pequenas variações determinísticas no espaço.
        """

        valor = (
            math.sin(x * 0.018)
            + math.cos(y * 0.015)
            + math.sin((x + y) * 0.008)
        )

        normalizado = (
            valor + 3.0
        ) / 6.0

        return Ambiente.limitar(
            normalizado,
            0.0,
            1.0,
        )

    @staticmethod
    def fator_temperatura(
        temperatura: float,
        temperatura_otima: float,
        tolerancia: float,
    ) -> float:
        """
        Calcula adequação térmica entre 0 e 1.
        """

        if tolerancia <= 0:
            raise ValueError(
                "tolerancia deve ser maior que zero."
            )

        distancia = abs(
            temperatura - temperatura_otima
        )

        return Ambiente.limitar(
            1.0 - distancia / tolerancia,
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
        Calcula adequação da umidade entre 0 e 1.
        """

        if tolerancia <= 0:
            raise ValueError(
                "tolerancia deve ser maior que zero."
            )

        distancia = abs(
            umidade - umidade_otima
        )

        return Ambiente.limitar(
            1.0 - distancia / tolerancia,
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
            min(valor, maximo),
        )


_ambiente_padrao = Ambiente()


def nivel_nutrientes(
    x: float,
    y: float,
) -> float:
    """
    Mantém compatibilidade com versões anteriores de organismos.py.

    Para uma integração mais completa, prefira usar uma instância de Ambiente
    pertencente à classe Mundo.
    """

    return _ambiente_padrao.nivel_nutrientes(
        x,
        y,
    )


def intensidade_luz() -> float:
    """
    Retorna a intensidade luminosa do ambiente padrão.
    """

    return _ambiente_padrao.intensidade_luz()


def atualizar_ambiente_padrao(
    passos: int = 1,
) -> None:
    """
    Avança o ambiente global usado pelas funções de compatibilidade.
    """

    _ambiente_padrao.atualizar(passos)
```
