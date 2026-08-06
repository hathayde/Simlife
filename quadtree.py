# quadtree.py
from __future__ import annotations

from typing import Any


class Quadtree:
    """
    Estrutura espacial para localizar organismos próximos.

    O retângulo de cada nó segue o formato:

        (x, y, largura, altura)

    A quadtree aceita qualquer objeto que possua os atributos:

        objeto.x
        objeto.y

    Métodos principais:

        insert(objeto)
        query(retangulo, resultados)
        clear()
    """

    def __init__(
        self,
        boundary: tuple[float, float, float, float],
        capacity: int = 8,
        *,
        max_depth: int = 10,
        depth: int = 0,
    ) -> None:
        """
        Cria um nó da quadtree.

        Args:
            boundary:
                Retângulo no formato x, y, largura e altura.

            capacity:
                Quantidade máxima de objetos armazenados diretamente
                no nó antes da subdivisão.

            max_depth:
                Profundidade máxima permitida.

            depth:
                Profundidade atual do nó. Usado internamente.
        """

        x, y, largura, altura = boundary

        if largura <= 0:
            raise ValueError(
                "A largura da quadtree deve ser maior que zero."
            )

        if altura <= 0:
            raise ValueError(
                "A altura da quadtree deve ser maior que zero."
            )

        if capacity < 1:
            raise ValueError(
                "capacity deve ser maior ou igual a 1."
            )

        if max_depth < 0:
            raise ValueError(
                "max_depth não pode ser negativo."
            )

        self.boundary = (
            float(x),
            float(y),
            float(largura),
            float(altura),
        )

        self.capacity = int(capacity)
        self.max_depth = int(max_depth)
        self.depth = int(depth)

        self.objects: list[Any] = []

        self.divided = False

        self.northwest: Quadtree | None = None
        self.northeast: Quadtree | None = None
        self.southwest: Quadtree | None = None
        self.southeast: Quadtree | None = None

    def insert(
        self,
        objeto: Any,
    ) -> bool:
        """
        Insere um objeto na quadtree.

        Retorna True quando a inserção ocorre com sucesso.

        O objeto precisa possuir atributos numéricos x e y.
        """

        if not self._objeto_valido(objeto):
            return False

        if not self.contains_point(
            self.boundary,
            float(objeto.x),
            float(objeto.y),
        ):
            return False

        pode_armazenar_neste_no = (
            len(self.objects) < self.capacity
            or self.depth >= self.max_depth
        )

        if pode_armazenar_neste_no:
            self.objects.append(objeto)
            return True

        if not self.divided:
            self.subdivide()

        filho = self._obter_filho_para_ponto(
            float(objeto.x),
            float(objeto.y),
        )

        if filho is not None and filho.insert(objeto):
            return True

        # Barreira de segurança para casos de precisão de ponto flutuante.
        self.objects.append(objeto)
        return True

    def subdivide(self) -> None:
        """
        Divide o nó atual em quatro quadrantes.
        """

        if self.divided:
            return

        x, y, largura, altura = self.boundary

        meia_largura = largura / 2.0
        meia_altura = altura / 2.0

        proxima_profundidade = self.depth + 1

        self.northwest = Quadtree(
            (
                x,
                y,
                meia_largura,
                meia_altura,
            ),
            self.capacity,
            max_depth=self.max_depth,
            depth=proxima_profundidade,
        )

        self.northeast = Quadtree(
            (
                x + meia_largura,
                y,
                meia_largura,
                meia_altura,
            ),
            self.capacity,
            max_depth=self.max_depth,
            depth=proxima_profundidade,
        )

        self.southwest = Quadtree(
            (
                x,
                y + meia_altura,
                meia_largura,
                meia_altura,
            ),
            self.capacity,
            max_depth=self.max_depth,
            depth=proxima_profundidade,
        )

        self.southeast = Quadtree(
            (
                x + meia_largura,
                y + meia_altura,
                meia_largura,
                meia_altura,
            ),
            self.capacity,
            max_depth=self.max_depth,
            depth=proxima_profundidade,
        )

        self.divided = True

        objetos_anteriores = self.objects
        self.objects = []

        for objeto in objetos_anteriores:
            filho = self._obter_filho_para_ponto(
                float(objeto.x),
                float(objeto.y),
            )

            if filho is None or not filho.insert(objeto):
                self.objects.append(objeto)

    def query(
        self,
        range_query: tuple[float, float, float, float],
        found: list[Any] | None = None,
    ) -> list[Any]:
        """
        Busca objetos dentro de um retângulo.

        Args:
            range_query:
                Retângulo no formato x, y, largura e altura.

            found:
                Lista que receberá os resultados. Esse argumento existe
                para manter compatibilidade com o código da simulação.

        Returns:
            A própria lista de resultados.
        """

        if found is None:
            found = []

        if not self.intersects(
            self.boundary,
            range_query,
        ):
            return found

        for objeto in self.objects:
            if not self._objeto_valido(objeto):
                continue

            if self.contains_point(
                range_query,
                float(objeto.x),
                float(objeto.y),
            ):
                found.append(objeto)

        if not self.divided:
            return found

        for filho in self._filhos():
            filho.query(
                range_query,
                found,
            )

        return found

    def query_circle(
        self,
        x: float,
        y: float,
        raio: float,
        found: list[Any] | None = None,
    ) -> list[Any]:
        """
        Busca objetos dentro de uma área circular.

        A busca inicial usa um retângulo delimitador e depois filtra
        os objetos pela distância quadrática.
        """

        if found is None:
            found = []

        if raio < 0:
            raise ValueError(
                "O raio não pode ser negativo."
            )

        candidatos: list[Any] = []

        self.query(
            (
                x - raio,
                y - raio,
                raio * 2.0,
                raio * 2.0,
            ),
            candidatos,
        )

        raio_quadrado = raio * raio

        for objeto in candidatos:
            dx = float(objeto.x) - x
            dy = float(objeto.y) - y

            distancia_quadrada = (
                dx * dx
                + dy * dy
            )

            if distancia_quadrada <= raio_quadrado:
                found.append(objeto)

        return found

    def clear(self) -> None:
        """
        Remove todos os objetos e subdivisões da árvore.
        """

        self.objects.clear()

        if self.divided:
            for filho in self._filhos():
                filho.clear()

        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

        self.divided = False

    def count(self) -> int:
        """
        Retorna o número total de objetos armazenados.
        """

        total = len(self.objects)

        if self.divided:
            for filho in self._filhos():
                total += filho.count()

        return total

    def node_count(self) -> int:
        """
        Retorna a quantidade total de nós da árvore.
        """

        total = 1

        if self.divided:
            for filho in self._filhos():
                total += filho.node_count()

        return total

    def max_used_depth(self) -> int:
        """
        Retorna a maior profundidade efetivamente usada.
        """

        if not self.divided:
            return self.depth

        return max(
            filho.max_used_depth()
            for filho in self._filhos()
        )

    def all_objects(self) -> list[Any]:
        """
        Retorna todos os objetos armazenados na árvore.
        """

        resultado = list(self.objects)

        if self.divided:
            for filho in self._filhos():
                resultado.extend(
                    filho.all_objects()
                )

        return resultado

    def _obter_filho_para_ponto(
        self,
        x: float,
        y: float,
    ) -> Quadtree | None:
        """
        Retorna o quadrante correspondente ao ponto.
        """

        if not self.divided:
            return None

        boundary_x, boundary_y, largura, altura = self.boundary

        meio_x = boundary_x + largura / 2.0
        meio_y = boundary_y + altura / 2.0

        lado_oeste = x < meio_x
        lado_norte = y < meio_y

        if lado_oeste and lado_norte:
            return self.northwest

        if not lado_oeste and lado_norte:
            return self.northeast

        if lado_oeste and not lado_norte:
            return self.southwest

        return self.southeast

    def _filhos(
        self,
    ) -> tuple[
        Quadtree,
        Quadtree,
        Quadtree,
        Quadtree,
    ]:
        """
        Retorna os quatro filhos do nó.

        Só deve ser chamado quando divided for True.
        """

        if (
            self.northwest is None
            or self.northeast is None
            or self.southwest is None
            or self.southeast is None
        ):
            raise RuntimeError(
                "A quadtree está marcada como dividida, "
                "mas seus quadrantes não foram inicializados."
            )

        return (
            self.northwest,
            self.northeast,
            self.southwest,
            self.southeast,
        )

    @staticmethod
    def _objeto_valido(
        objeto: Any,
    ) -> bool:
        """
        Verifica se o objeto possui coordenadas válidas.
        """

        if objeto is None:
            return False

        if not hasattr(objeto, "x"):
            return False

        if not hasattr(objeto, "y"):
            return False

        try:
            float(objeto.x)
            float(objeto.y)

        except (TypeError, ValueError):
            return False

        return True

    @staticmethod
    def contains_point(
        boundary: tuple[float, float, float, float],
        x: float,
        y: float,
    ) -> bool:
        """
        Verifica se um ponto está dentro de um retângulo.

        A borda direita e a borda inferior são exclusivas.
        Isso evita que um ponto pertença a dois quadrantes ao mesmo tempo.
        """

        boundary_x, boundary_y, largura, altura = boundary

        return (
            boundary_x <= x < boundary_x + largura
            and boundary_y <= y < boundary_y + altura
        )

    @staticmethod
    def contains(
        boundary: tuple[float, float, float, float],
        objeto: Any,
    ) -> bool:
        """
        Mantém compatibilidade com versões anteriores da quadtree.
        """

        if not Quadtree._objeto_valido(objeto):
            return False

        return Quadtree.contains_point(
            boundary,
            float(objeto.x),
            float(objeto.y),
        )

    @staticmethod
    def intersects(
        primeiro: tuple[float, float, float, float],
        segundo: tuple[float, float, float, float],
    ) -> bool:
        """
        Verifica se dois retângulos se intersectam.
        """

        primeiro_x, primeiro_y, primeira_largura, primeira_altura = (
            primeiro
        )

        segundo_x, segundo_y, segunda_largura, segunda_altura = (
            segundo
        )

        return not (
            segundo_x >= primeiro_x + primeira_largura
            or segundo_x + segunda_largura <= primeiro_x
            or segundo_y >= primeiro_y + primeira_altura
            or segundo_y + segunda_altura <= primeiro_y
        )

    def __len__(
        self,
    ) -> int:
        return self.count()

    def __repr__(
        self,
    ) -> str:
        return (
            "Quadtree("
            f"boundary={self.boundary}, "
            f"capacity={self.capacity}, "
            f"depth={self.depth}, "
            f"objects={len(self.objects)}, "
            f"divided={self.divided}"
            ")"
        )
