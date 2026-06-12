# randongeon/jogo/entidades/entidade.py

"""
Base abstrata das entidades de combate (Jogador e Inimigo).
"""

from abc import ABC, abstractmethod


class Entidade(ABC):
    """
    Classe base abstrata de tudo que participa do combate: TEM vida, sabe se
    está vivo, recebe cura e sofre dano.

    Pilares de POO da disciplina:
      - Abstração + ABC (slide "Classes Abstratas"): `Entidade` define a
        INTERFACE e o comportamento COMUM (esta_vivo / curar), mas é abstrata —
        não pode ser instanciada por si só. Quem combate trata Jogador e
        Inimigo de forma uniforme, "como Entidades".
      - Herança: `Jogador` e `Inimigo` herdam vida/cura prontas, eliminando o
        código duplicado que existia nas duas classes.
      - Polimorfismo: `receber_dano()` é ABSTRATO — cada subclasse aplica o dano
        do seu jeito (o Inimigo desconta armadura; o Jogador sofre direto).
    """

    def __init__(self, nome: str, hp: int) -> None:
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("Nome da entidade deve ser uma string não vazia.")
        if hp <= 0:
            raise ValueError("HP inicial deve ser maior que zero.")
        self.nome   = nome
        self.hp_max = hp
        self.hp     = hp
        self.efeitos: list = []   # efeitos de status ativos (Lote B2)

    def esta_vivo(self) -> bool:
        """True se ainda há HP."""
        return self.hp > 0

    # ── Efeitos de status (Lote B2) ─────────────────────────────────────────
    def aplicar_efeito(self, efeito) -> None:
        """
        Adiciona um efeito. Se já houver um do mesmo tipo, apenas RENOVA a
        duração para o maior valor (não empilha vários iguais).
        """
        existente = self.buscar_efeito(efeito.tipo)
        if existente is not None:
            existente.turnos = max(existente.turnos, efeito.turnos)
        else:
            self.efeitos.append(efeito)

    def buscar_efeito(self, tipo: str):
        """Devolve o efeito ativo do tipo dado, ou None."""
        for e in self.efeitos:
            if e.tipo == tipo and e.ativo():
                return e
        return None

    def remover_efeitos(self, apenas_ao_curar: bool = False) -> None:
        """Remove efeitos. Se apenas_ao_curar, só os marcados (ex.: veneno)."""
        if apenas_ao_curar:
            self.efeitos = [e for e in self.efeitos if not e.remove_ao_curar]
        else:
            self.efeitos = []

    def processar_efeitos_turno(self) -> int:
        """
        Processa um turno de efeitos: aplica cada hook `ao_iniciar_turno`,
        consome 1 turno de cada e descarta os expirados.
        Retorna o dano total causado por efeitos (DoT) neste turno.
        """
        dano = 0
        for e in list(self.efeitos):
            dano += e.ao_iniciar_turno(self)
            e.turnos -= 1
        self.efeitos = [e for e in self.efeitos if e.ativo()]
        return dano

    def curar(self, quantidade: int) -> int:
        """
        Restaura HP sem ultrapassar o hp_max. Retorna o HP efetivamente curado.
        Comportamento idêntico para Jogador e Inimigo — por isso vive na base.
        """
        if quantidade < 0:
            raise ValueError("Quantidade de cura não pode ser negativa.")
        hp_antes = self.hp
        self.hp  = min(self.hp_max, self.hp + quantidade)
        return self.hp - hp_antes

    @abstractmethod
    def receber_dano(self, dano: int) -> int:
        """
        Aplica dano à entidade e devolve o dano EFETIVO sofrido.

        Método abstrato (Polimorfismo): cada subclasse implementa sua regra —
        o Inimigo desconta `absorcao_dano` (armadura) antes; o Jogador não.
        """
        raise NotImplementedError
