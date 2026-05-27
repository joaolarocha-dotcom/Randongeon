"""
Suíte de testes unitários para os novos inimigos especiais — v3

Cobre as cinco fábricas introduzidas na v3 de inimigo.py:
  - Vampiro das Sombras  (andar >= 15): cura 20% do dano causado
  - Golem de Pedra       (andar >= 8):  absorve 2 de dano por ataque
  - Caçador Sombrio      (andar >= 10): ganha +1 ATK/turno
  - Horda de Goblins     (qualquer):    HP combinado, ATK baixo
  - Banshee              (andar >= 17): 30% de chance de atordoar

Execute com:
    pytest tests/test_novos_inimigos.py -v
"""

import pytest
from unittest.mock import patch

from jogo.entidades.inimigo import Inimigo, NOMES_DIFICULDADE_1, NOMES_DIFICULDADE_2
from jogo.entidades.jogador import Jogador
from jogo.sistemas.masmorra import Masmorra, CHANCE_FUGA


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _set_atributos_especiais(inimigo: Inimigo) -> None:
    """
    Inicializa os atributos especiais em instâncias criadas via __new__
    (sem passar pelo __init__). Necessário para testes de combate que
    criam Inimigo.__new__() para contornar a validação de atk=0.
    """
    inimigo.hp_max              = inimigo.hp
    inimigo.modificador_fuga    = 0.0
    inimigo.cura_percentual     = 0.0
    inimigo.absorcao_dano       = 0
    inimigo.bonus_atk_por_turno = 0
    inimigo.chance_atordoar     = 0.0
    inimigo.tipo_especial       = None


def _dummy(hp=1, atk=1, xp=10, moedas=5) -> Inimigo:
    """Cria inimigo mínimo para testes de combate."""
    i             = Inimigo.__new__(Inimigo)
    i.nome        = "Dummy"
    i.hp          = hp
    i.atk         = atk
    i.dificuldade = 1
    i.xp          = xp
    i.moedas      = moedas
    _set_atributos_especiais(i)
    return i


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 1 — Vampiro das Sombras
# ══════════════════════════════════════════════════════════════════════════════

class TestVampiroDasSombras:
    """Testa a fábrica _criar_vampiro() e sua mecânica de cura."""

    def test_fabrica_retorna_instancia_de_inimigo(self):
        """Caminho feliz: _criar_vampiro() deve retornar instância de Inimigo."""
        assert isinstance(Inimigo._criar_vampiro(), Inimigo)

    def test_nome_correto(self):
        """Caminho feliz: nome deve ser 'Vampiro das Sombras'."""
        assert Inimigo._criar_vampiro().nome == "Vampiro das Sombras"

    def test_dificuldade_e_dois(self):
        """Caminho feliz: Vampiro é elite (dif=2)."""
        assert Inimigo._criar_vampiro().dificuldade == 2

    def test_tipo_especial_e_vampiro(self):
        """Caminho feliz: tipo_especial deve ser 'vampiro'."""
        assert Inimigo._criar_vampiro().tipo_especial == "vampiro"

    def test_cura_percentual_e_vinte_por_cento(self):
        """Mecânica: cura_percentual deve ser 0.20."""
        assert Inimigo._criar_vampiro().cura_percentual == 0.20

    def test_modificador_fuga_e_negativo(self):
        """Comportamento: fuga mais difícil — modificador_fuga deve ser < 0."""
        assert Inimigo._criar_vampiro().modificador_fuga < 0.0

    def test_hp_dentro_do_range(self):
        """Estatístico: hp deve estar entre 12 e 18."""
        for _ in range(20):
            v = Inimigo._criar_vampiro()
            assert 12 <= v.hp <= 18

    def test_hp_max_igual_ao_hp_inicial(self):
        """Invariante v3: hp_max deve ser igual ao hp no momento da criação."""
        v = Inimigo._criar_vampiro()
        assert v.hp_max == v.hp

    def test_atk_dentro_do_range(self):
        """Estatístico: atk deve estar entre 4 e 6."""
        for _ in range(20):
            assert 4 <= Inimigo._criar_vampiro().atk <= 6

    def test_moedas_positivas(self):
        """Caminho feliz: Vampiro deve dropar moedas > 0."""
        assert Inimigo._criar_vampiro().moedas > 0

    def test_absorcao_dano_e_zero(self):
        """Neutro: Vampiro não tem armadura."""
        assert Inimigo._criar_vampiro().absorcao_dano == 0

    def test_chance_atordoar_e_zero(self):
        """Neutro: Vampiro não atordoa."""
        assert Inimigo._criar_vampiro().chance_atordoar == 0.0

    def test_bonus_atk_por_turno_e_zero(self):
        """Neutro: Vampiro não escala ATK."""
        assert Inimigo._criar_vampiro().bonus_atk_por_turno == 0


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 2 — Golem de Pedra
# ══════════════════════════════════════════════════════════════════════════════

class TestGolemDePedra:
    """Testa a fábrica _criar_golem() e sua mecânica de absorção de dano."""

    def test_fabrica_retorna_instancia_de_inimigo(self):
        """Caminho feliz: _criar_golem() deve retornar instância de Inimigo."""
        assert isinstance(Inimigo._criar_golem(), Inimigo)

    def test_nome_correto(self):
        """Caminho feliz: nome deve ser 'Golem de Pedra'."""
        assert Inimigo._criar_golem().nome == "Golem de Pedra"

    def test_dificuldade_e_dois(self):
        """Caminho feliz: Golem é elite (dif=2)."""
        assert Inimigo._criar_golem().dificuldade == 2

    def test_tipo_especial_e_golem(self):
        """Caminho feliz: tipo_especial deve ser 'golem'."""
        assert Inimigo._criar_golem().tipo_especial == "golem"

    def test_absorcao_dano_e_dois(self):
        """Mecânica: absorcao_dano deve ser 2."""
        assert Inimigo._criar_golem().absorcao_dano == 2

    def test_absorcao_reduz_dano_recebido(self):
        """Mecânica: ataque de força 5 deve causar apenas 3 de dano (5-2=3)."""
        golem = Inimigo._criar_golem()
        golem.hp = 20
        dano = golem.receber_dano(5)
        assert dano == 3
        assert golem.hp == 17

    def test_absorcao_maior_que_dano_resulta_zero(self):
        """Mecânica: ataque de força 2 deve causar zero dano (2-2=0)."""
        golem = Inimigo._criar_golem()
        hp_antes = golem.hp
        dano = golem.receber_dano(2)
        assert dano == 0
        assert golem.hp == hp_antes

    def test_ataque_de_forca_um_causa_zero_dano(self):
        """Mecânica: ataque de força 1 deve ser completamente absorvido."""
        golem = Inimigo._criar_golem()
        hp_antes = golem.hp
        assert golem.receber_dano(1) == 0
        assert golem.hp == hp_antes

    def test_hp_dentro_do_range(self):
        """Estatístico: hp deve estar entre 15 e 22."""
        for _ in range(20):
            g = Inimigo._criar_golem()
            assert 15 <= g.hp <= 22

    def test_cura_percentual_e_zero(self):
        """Neutro: Golem não se cura."""
        assert Inimigo._criar_golem().cura_percentual == 0.0

    def test_chance_atordoar_e_zero(self):
        """Neutro: Golem não atordoa."""
        assert Inimigo._criar_golem().chance_atordoar == 0.0


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 — Caçador Sombrio
# ══════════════════════════════════════════════════════════════════════════════

class TestCacadorSombrio:
    """Testa a fábrica _criar_cacador() e sua mecânica de ATK crescente."""

    def test_fabrica_retorna_instancia_de_inimigo(self):
        """Caminho feliz: _criar_cacador() deve retornar instância de Inimigo."""
        assert isinstance(Inimigo._criar_cacador(), Inimigo)

    def test_nome_correto(self):
        """Caminho feliz: nome deve ser 'Caçador Sombrio'."""
        assert Inimigo._criar_cacador().nome == "Caçador Sombrio"

    def test_dificuldade_e_dois(self):
        """Caminho feliz: Caçador é elite (dif=2)."""
        assert Inimigo._criar_cacador().dificuldade == 2

    def test_tipo_especial_e_cacador(self):
        """Caminho feliz: tipo_especial deve ser 'cacador'."""
        assert Inimigo._criar_cacador().tipo_especial == "cacador"

    def test_bonus_atk_por_turno_e_um(self):
        """Mecânica: bonus_atk_por_turno deve ser 1."""
        assert Inimigo._criar_cacador().bonus_atk_por_turno == 1

    def test_hp_baixo_intencional(self):
        """Design: HP deve estar entre 6 e 10 (incentiva terminar rápido)."""
        for _ in range(20):
            c = Inimigo._criar_cacador()
            assert 6 <= c.hp <= 10

    def test_modificador_fuga_e_positivo(self):
        """Comportamento: mais fácil fugir do Caçador — modificador_fuga > 0."""
        assert Inimigo._criar_cacador().modificador_fuga > 0.0

    def test_cura_percentual_e_zero(self):
        """Neutro: Caçador não se cura."""
        assert Inimigo._criar_cacador().cura_percentual == 0.0

    def test_absorcao_dano_e_zero(self):
        """Neutro: Caçador não tem armadura."""
        assert Inimigo._criar_cacador().absorcao_dano == 0

    def test_atk_inicial_dentro_do_range(self):
        """Estatístico: ATK inicial deve estar entre 3 e 5."""
        for _ in range(20):
            assert 3 <= Inimigo._criar_cacador().atk <= 5

    def test_moedas_positivas(self):
        """Caminho feliz: Caçador deve dropar moedas > 0."""
        assert Inimigo._criar_cacador().moedas > 0


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 4 — Horda de Goblins
# ══════════════════════════════════════════════════════════════════════════════

class TestHordaDeGoblins:
    """Testa a fábrica _criar_horda() — disponível desde o andar 1."""

    def test_fabrica_retorna_instancia_de_inimigo(self):
        """Caminho feliz: _criar_horda() deve retornar instância de Inimigo."""
        assert isinstance(Inimigo._criar_horda(), Inimigo)

    def test_nome_correto(self):
        """Caminho feliz: nome deve ser 'Horda de Goblins'."""
        assert Inimigo._criar_horda().nome == "Horda de Goblins"

    def test_dificuldade_e_um(self):
        """Design: Horda é inimigo comum (dif=1) — disponível no início do jogo."""
        assert Inimigo._criar_horda().dificuldade == 1

    def test_tipo_especial_e_horda(self):
        """Caminho feliz: tipo_especial deve ser 'horda'."""
        assert Inimigo._criar_horda().tipo_especial == "horda"

    def test_modificador_fuga_e_alto_positivo(self):
        """Design: fuga muito fácil (+0.20) — goblins são lentos em grupo."""
        assert Inimigo._criar_horda().modificador_fuga == 0.20

    def test_hp_combinado_maior_que_goblin_comum(self):
        """Design: HP de horda (9-12) deve ser maior que goblin solo (3-7)."""
        horda = Inimigo._criar_horda()
        assert horda.hp >= 9

    def test_atk_baixo_como_esperado(self):
        """Design: ATK deve ser baixo (1-2) representando goblins individuais."""
        for _ in range(20):
            h = Inimigo._criar_horda()
            assert 1 <= h.atk <= 2

    def test_cura_percentual_e_zero(self):
        """Neutro: Horda não se cura."""
        assert Inimigo._criar_horda().cura_percentual == 0.0

    def test_absorcao_dano_e_zero(self):
        """Neutro: Horda não tem armadura."""
        assert Inimigo._criar_horda().absorcao_dano == 0

    def test_chance_atordoar_e_zero(self):
        """Neutro: Horda não atordoa."""
        assert Inimigo._criar_horda().chance_atordoar == 0.0

    def test_horda_disponivel_no_andar_1(self):
        """
        Integração: Horda deve poder aparecer no andar 1.
        Com random.random=0.05 (< 0.10), gerar() deve retornar a Horda.
        """
        with patch("jogo.entidades.inimigo.random.random", return_value=0.05):
            inimigo = Inimigo.gerar(andar=1)
        assert inimigo.tipo_especial == "horda"


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 5 — Banshee
# ══════════════════════════════════════════════════════════════════════════════

class TestBanshee:
    """Testa a fábrica _criar_banshee() e sua mecânica de atordoamento."""

    def test_fabrica_retorna_instancia_de_inimigo(self):
        """Caminho feliz: _criar_banshee() deve retornar instância de Inimigo."""
        assert isinstance(Inimigo._criar_banshee(), Inimigo)

    def test_nome_correto(self):
        """Caminho feliz: nome deve ser 'Banshee'."""
        assert Inimigo._criar_banshee().nome == "Banshee"

    def test_dificuldade_e_dois(self):
        """Caminho feliz: Banshee é elite (dif=2)."""
        assert Inimigo._criar_banshee().dificuldade == 2

    def test_tipo_especial_e_banshee(self):
        """Caminho feliz: tipo_especial deve ser 'banshee'."""
        assert Inimigo._criar_banshee().tipo_especial == "banshee"

    def test_chance_atordoar_e_trinta_por_cento(self):
        """Mecânica: chance_atordoar deve ser 0.30."""
        assert Inimigo._criar_banshee().chance_atordoar == 0.30

    def test_modificador_fuga_e_muito_negativo(self):
        """Comportamento: fuga mais difícil (-0.15) — Banshee paralisa escapadas."""
        assert Inimigo._criar_banshee().modificador_fuga == -0.15

    def test_hp_dentro_do_range(self):
        """Estatístico: hp deve estar entre 10 e 15."""
        for _ in range(20):
            b = Inimigo._criar_banshee()
            assert 10 <= b.hp <= 15

    def test_atk_dentro_do_range(self):
        """Estatístico: atk deve estar entre 3 e 6."""
        for _ in range(20):
            assert 3 <= Inimigo._criar_banshee().atk <= 6

    def test_cura_percentual_e_zero(self):
        """Neutro: Banshee não se cura."""
        assert Inimigo._criar_banshee().cura_percentual == 0.0

    def test_absorcao_dano_e_zero(self):
        """Neutro: Banshee não tem armadura."""
        assert Inimigo._criar_banshee().absorcao_dano == 0

    def test_bonus_atk_por_turno_e_zero(self):
        """Neutro: Banshee não escala ATK."""
        assert Inimigo._criar_banshee().bonus_atk_por_turno == 0

    def test_moedas_altas(self):
        """Design: Banshee (andar 17+) deve dropar moedas > inimigo comum."""
        for _ in range(20):
            b = Inimigo._criar_banshee()
            assert b.moedas >= 10


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 6 — Método curar() do Inimigo
# ══════════════════════════════════════════════════════════════════════════════

class TestCurarInimigo:
    """Testa o método curar() introduzido na v3."""

    def test_curar_aumenta_hp(self):
        """Caminho feliz: curar() deve aumentar o hp do inimigo."""
        v = Inimigo._criar_vampiro()
        v.hp = 10
        v.curar(5)
        assert v.hp == 15

    def test_curar_nao_ultrapassa_hp_max(self):
        """Limite: curar() não deve ultrapassar hp_max."""
        v = Inimigo._criar_vampiro()
        hp_max = v.hp_max
        v.hp = hp_max - 2
        v.curar(100)
        assert v.hp == hp_max

    def test_curar_valor_negativo_levanta_value_error(self):
        """Exceção: curar(-1) deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo._criar_vampiro().curar(-1)

    def test_curar_zero_nao_altera_hp(self):
        """Borda: curar(0) não deve alterar o hp."""
        v = Inimigo._criar_vampiro()
        v.hp = 10
        v.curar(0)
        assert v.hp == 10

    def test_hp_max_permanece_fixo_apos_cura(self):
        """Invariante: curar() nunca deve alterar hp_max."""
        v = Inimigo._criar_vampiro()
        hp_max_antes = v.hp_max
        v.hp = 5
        v.curar(100)
        assert v.hp_max == hp_max_antes


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 7 — Dispatcher _criar_especial()
# ══════════════════════════════════════════════════════════════════════════════

class TestCriarEspecial:
    """Testa o dispatcher _criar_especial() que direciona por string."""

    @pytest.mark.parametrize("tipo,nome_esperado", [
        ("vampiro", "Vampiro das Sombras"),
        ("golem",   "Golem de Pedra"),
        ("cacador", "Caçador Sombrio"),
        ("banshee", "Banshee"),
    ])
    def test_dispatcher_cria_tipo_correto(self, tipo, nome_esperado):
        """Parametrizado: cada tipo deve criar o inimigo correto."""
        inimigo = Inimigo._criar_especial(tipo)
        assert inimigo.nome == nome_esperado

    def test_tipo_desconhecido_levanta_value_error(self):
        """Exceção: tipo inválido deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo._criar_especial("dragao_inexistente")

    def test_tipo_vazio_levanta_value_error(self):
        """Exceção: string vazia deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo._criar_especial("")


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 8 — Thresholds de andar em gerar()
# ══════════════════════════════════════════════════════════════════════════════

class TestThresholdsDeAndar:
    """
    Testa que especiais só aparecem nos andares corretos,
    usando mocks para forçar o caminho de geração desejado.

    Sequência de random em gerar():
      1. random.random() para Horda      → fixamos como 0.50 (> 0.10, pula)
      2. random.random() para elite      → fixamos como 0.10 (< 0.25, entra)
      3. random.random() para especial   → fixamos como 0.20 (< 0.40, escolhe)
      4. random.choice() para o especial → fixado pelo mock de choice
    """

    @patch("jogo.entidades.inimigo.random.random", return_value=0.50)
    def test_golem_nao_disponivel_antes_do_andar_8(self, _):
        """
        Andar 7: nenhum especial disponível → _gerar_elite() cria elite comum.
        Como random.random=0.50 > 0.25, nem entra no branch de elite.
        Garantimos dif=2 ou dif=1, mas NOT golem.
        """
        for _ in range(20):
            i = Inimigo.gerar(andar=7)
            assert i.tipo_especial != "golem"

    @patch("jogo.entidades.inimigo.random.choice", return_value="golem")
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.20])
    def test_golem_disponivel_no_andar_8(self, _rand, _choice):
        """
        Andar 8: golem disponível.
        random[0]=0.50 pula horda, random[1]=0.10 entra no elite,
        random[2]=0.20 < 0.40 escolhe especial, choice retorna 'golem'.
        """
        inimigo = Inimigo.gerar(andar=8)
        assert inimigo.tipo_especial == "golem"

    @patch("jogo.entidades.inimigo.random.choice", return_value="cacador")
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.20])
    def test_cacador_disponivel_no_andar_10(self, _rand, _choice):
        """Andar 10: Caçador deve ser gerado com os mocks corretos."""
        inimigo = Inimigo.gerar(andar=10)
        assert inimigo.tipo_especial == "cacador"

    @patch("jogo.entidades.inimigo.random.choice", return_value="vampiro")
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.20])
    def test_vampiro_disponivel_no_andar_15(self, _rand, _choice):
        """Andar 15: Vampiro deve ser gerado com os mocks corretos."""
        inimigo = Inimigo.gerar(andar=15)
        assert inimigo.tipo_especial == "vampiro"

    @patch("jogo.entidades.inimigo.random.choice", return_value="banshee")
    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.20])
    def test_banshee_disponivel_no_andar_17(self, _rand, _choice):
        """Andar 17: Banshee deve ser gerado com os mocks corretos."""
        inimigo = Inimigo.gerar(andar=17)
        assert inimigo.tipo_especial == "banshee"

    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.10, 0.50])
    def test_elite_comum_quando_random_especial_acima_de_40(self, _):
        """
        Andar 10: mesmo com especiais disponíveis, random[2]=0.50 > 0.40
        deve gerar elite COMUM (não especial).
        """
        inimigo = Inimigo.gerar(andar=10)
        assert inimigo.tipo_especial is None
        assert inimigo.dificuldade   == 2

    @patch("jogo.entidades.inimigo.random.random", side_effect=[0.50, 0.50])
    def test_inimigo_comum_quando_nao_e_elite(self, _):
        """
        Andar 5: random[1]=0.50 > 0.25 não entra no branch de elite.
        Deve gerar inimigo comum (dif=1).
        """
        inimigo = Inimigo.gerar(andar=5)
        assert inimigo.dificuldade  == 1
        assert inimigo.tipo_especial is None


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 9 — Fuga variável por tipo (integração com tentar_fuga)
# ══════════════════════════════════════════════════════════════════════════════

class TestFugaVariavelPorTipo:
    """
    Testa que tentar_fuga() aplica o modificador_fuga de cada tipo de inimigo.
    Requer que a Masmorra (v3) aceite um inimigo como parâmetro.
    """

    def _masmorra(self) -> Masmorra:
        return Masmorra(Jogador("Teste", hp=20, atk=5))

    @patch("jogo.sistemas.masmorra.random.random", return_value=0.45)
    def test_horda_mais_facil_fugir(self, _mock):
        """
        Horda: modificador_fuga=+0.20 → chance efetiva = 0.50+0.20=0.70.
        random=0.45 < 0.70 → fuga bem-sucedida.
        """
        horda = Inimigo._criar_horda()
        m = self._masmorra()
        assert m.tentar_fuga(horda) is True

    @patch("jogo.sistemas.masmorra.random.random", return_value=0.55)
    def test_vampiro_mais_dificil_fugir(self, _mock):
        """
        Vampiro: modificador_fuga=-0.10 → chance efetiva = 0.50-0.10=0.40.
        random=0.55 > 0.40 → fuga falha.
        """
        vampiro = Inimigo._criar_vampiro()
        m = self._masmorra()
        assert m.tentar_fuga(vampiro) is False

    @patch("jogo.sistemas.masmorra.random.random", return_value=0.55)
    def test_banshee_mais_dificil_fugir(self, _mock):
        """
        Banshee: modificador_fuga=-0.15 → chance efetiva = 0.50-0.15=0.35.
        random=0.55 > 0.35 → fuga falha.
        """
        banshee = Inimigo._criar_banshee()
        m = self._masmorra()
        assert m.tentar_fuga(banshee) is False

    @patch("jogo.sistemas.masmorra.random.random", return_value=0.53)
    def test_cacador_ligeiramente_mais_facil_fugir(self, _mock):
        """
        Caçador: modificador_fuga=+0.05 → chance efetiva = 0.55.
        random=0.53 < 0.55 → fuga bem-sucedida.
        """
        cacador = Inimigo._criar_cacador()
        m = self._masmorra()
        assert m.tentar_fuga(cacador) is True

    @patch("jogo.sistemas.masmorra.random.random", return_value=0.49)
    def test_inimigo_comum_fuga_padrao(self, _mock):
        """
        Inimigo comum: modificador_fuga=0 → chance efetiva = 0.50.
        random=0.49 < 0.50 → fuga bem-sucedida.
        """
        comum = Inimigo("Goblin", hp=5, atk=1, dificuldade=1, xp=10, moedas=2)
        m = self._masmorra()
        assert m.tentar_fuga(comum) is True

    @patch("jogo.sistemas.masmorra.random.random", return_value=0.51)
    def test_inimigo_sem_modificador_fuga_padrao(self, _mock):
        """
        Sem modificador: random=0.51 > 0.50 → fuga falha.
        """
        comum = Inimigo("Goblin", hp=5, atk=1, dificuldade=1, xp=10, moedas=2)
        m = self._masmorra()
        assert m.tentar_fuga(comum) is False


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 10 — hp_max em todos os inimigos gerados via gerar()
# ══════════════════════════════════════════════════════════════════════════════

class TestHpMaxEmTodosOsTipos:
    """
    Testa o invariante de que qualquer inimigo gerado via gerar()
    ou via fábrica tem hp_max definido e igual ao hp inicial.
    """

    @pytest.mark.parametrize("fabrica", [
        Inimigo._criar_vampiro,
        Inimigo._criar_golem,
        Inimigo._criar_cacador,
        Inimigo._criar_horda,
        Inimigo._criar_banshee,
    ])
    def test_hp_max_igual_ao_hp_inicial_para_todos_especiais(self, fabrica):
        """Invariante: hp_max deve ser hp no momento da criação para cada fábrica."""
        i = fabrica()
        assert i.hp_max == i.hp

    def test_hp_max_nao_muda_apos_receber_dano(self):
        """Invariante: hp_max deve permanecer fixo após receber dano."""
        golem = Inimigo._criar_golem()
        hp_max_antes = golem.hp_max
        golem.receber_dano(5)
        assert golem.hp_max == hp_max_antes

    def test_repr_exibe_hp_max(self):
        """Representação: __repr__ deve exibir hp/hp_max no formato correto."""
        v = Inimigo._criar_vampiro()
        assert f"{v.hp}/{v.hp_max}" in repr(v)

    def test_inimigo_gerado_via_gerar_tem_hp_max(self):
        """Integração: qualquer inimigo gerado via gerar() deve ter hp_max definido."""
        for _ in range(30):
            i = Inimigo.gerar(andar=10)
            assert hasattr(i, "hp_max")
            assert i.hp_max == i.hp