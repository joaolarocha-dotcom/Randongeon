# randongeon/jogo/entidades/efeitos.py

"""
Sistema de efeitos de status (Lote B2).

Um EfeitoStatus é um estado TEMPORÁRIO (dura N turnos) que vive sobre uma
Entidade. Em vez de espalhar flags soltas (veneno_turnos, fraqueza_turnos...),
cada efeito é uma classe com hooks; a Entidade carrega uma lista de efeitos e os
processa de forma uniforme.

POO: classe base + subclasses (Polimorfismo) — a Entidade chama os mesmos hooks
(`ao_iniciar_turno`, `modifica_atk`, `modifica_esquiva`) sem saber o efeito
concreto. Cada efeito sobrescreve só o hook que lhe interessa.
"""

from abc import ABC


class EfeitoStatus(ABC):
    """Base de um efeito temporário. Hooks têm default neutro (no-op)."""

    tipo: str = "efeito"          # identificador único do tipo de efeito
    remove_ao_curar: bool = False  # sai quando o portador se cura / sobe de nível

    def __init__(self, turnos: int) -> None:
        if turnos < 0:
            raise ValueError("Duração do efeito não pode ser negativa.")
        self.turnos = turnos

    def ativo(self) -> bool:
        return self.turnos > 0

    # ── Hooks (Polimorfismo) ────────────────────────────────────────────────
    def ao_iniciar_turno(self, portador) -> int:
        """Executado a cada turno. Retorna dano causado (DoT); 0 por padrão."""
        return 0

    def modifica_atk(self, atk: int) -> int:
        """Modifica o ATK efetivo do portador. Identidade por padrão."""
        return atk

    def modifica_esquiva(self, esq: float) -> float:
        """Modifica a esquiva efetiva do portador. Identidade por padrão."""
        return esq


class Veneno(EfeitoStatus):
    """Dano por turno (Goblin/Rato Gigante). Curado por poção/level-up."""
    tipo = "veneno"
    remove_ao_curar = True
    DANO = 1

    def ao_iniciar_turno(self, portador) -> int:
        return portador.receber_dano(self.DANO)


class Fraqueza(EfeitoStatus):
    """Reduz o ATK do portador por alguns turnos (Orc). Não zera o ataque."""
    tipo = "fraqueza"

    def __init__(self, turnos: int, reducao: int = 2) -> None:
        super().__init__(turnos)
        self.reducao = reducao

    def modifica_atk(self, atk: int) -> int:
        return max(1, atk - self.reducao)


class EsquivaReduzida(EfeitoStatus):
    """Reduz a esquiva do portador (Troll das Cavernas — golpe de maça)."""
    tipo = "esquiva_reduzida"

    def __init__(self, turnos: int, reducao: float = 0.20) -> None:
        super().__init__(turnos)
        self.reducao = reducao

    def modifica_esquiva(self, esq: float) -> float:
        return max(0.0, esq - self.reducao)
