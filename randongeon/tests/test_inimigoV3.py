"""
Suíte de testes para os atributos v3 do Inimigo — NÃO conflita com test_inimigo.py

Este arquivo contém APENAS testes de funcionalidade nova:
  - hp_max        (novo atributo v3)
  - curar()       (novo método v3)
  - absorcao_dano (processado em receber_dano())
  - atributos especiais com valores padrão neutros
  - validações dos novos parâmetros do __init__
  - Correções de testes que quebram do test_inimigo.py original
    (andar=3→5 para elite, range de moedas dif2=5-10)

Os testes marcados com # CORREÇÃO são a versão correta dos testes
originais de test_inimigo.py que precisam de atualização.

Execute com:
    pytest tests/test_inimigo_v3.py -v
"""

import pytest
from unittest.mock import patch
from jogo.entidades.inimigo import Inimigo, NOMES_DIFICULDADE_1, NOMES_DIFICULDADE_2


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 1 — hp_max: o novo atributo de teto de vida
# ══════════════════════════════════════════════════════════════════════════════

class TestHpMax:
    """Testa o atributo hp_max introduzido na v3."""

    def test_hp_max_igual_ao_hp_inicial(self):
        """Invariante: hp_max deve ser igual ao hp passado no __init__."""
        i = Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=15, moedas=5)
        assert i.hp_max == 10

    def test_hp_max_nao_muda_apos_dano(self):
        """Invariante: hp_max deve permanecer fixo mesmo após receber dano."""
        i = Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=15, moedas=5)
        i.receber_dano(5)
        assert i.hp     == 5
        assert i.hp_max == 10

    def test_hp_max_nao_muda_apos_cura(self):
        """Invariante: curar() nunca altera hp_max."""
        i = Inimigo("Vampiro", hp=15, atk=5, dificuldade=2,
                    xp=40, moedas=10, cura_percentual=0.20)
        i.hp = 10
        i.curar(3)
        assert i.hp_max == 15

    def test_hp_max_com_hp_grande(self):
        """Borda: hp_max deve refletir qualquer hp inicial, incluindo valores altos."""
        boss = Inimigo("Boss", hp=999, atk=50, dificuldade=3, xp=500, moedas=200)
        assert boss.hp_max == 999

    @pytest.mark.parametrize("hp_inicial", [1, 5, 10, 20, 100])
    def test_hp_max_para_varios_hp_iniciais(self, hp_inicial):
        """Parametrizado: hp_max deve sempre refletir o hp no momento da criação."""
        i = Inimigo("X", hp=hp_inicial, atk=1, dificuldade=1, xp=0, moedas=0)
        assert i.hp_max == hp_inicial


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 2 — curar(): método novo v3 do Inimigo
# ══════════════════════════════════════════════════════════════════════════════

class TestCurarInimigo:
    """Testa o método curar() adicionado ao Inimigo na v3."""

    def test_curar_aumenta_hp(self):
        """Caminho feliz: curar deve restaurar HP."""
        i = Inimigo("Goblin", hp=10, atk=2, dificuldade=1, xp=10, moedas=3)
        i.hp = 5
        i.curar(3)
        assert i.hp == 8

    def test_curar_nao_ultrapassa_hp_max(self):
        """Limite: curar() nunca ultrapassa hp_max."""
        i = Inimigo("Vampiro", hp=15, atk=5, dificuldade=2, xp=40, moedas=10)
        i.hp = 10
        i.curar(100)
        assert i.hp == 15

    def test_curar_exatamente_ao_maximo(self):
        """Borda: curar() que leva ao hp_max exato deve resultar em hp == hp_max."""
        i = Inimigo("X", hp=15, atk=2, dificuldade=1, xp=10, moedas=3)
        i.hp = 10
        i.curar(5)
        assert i.hp == 15

    def test_curar_zero_nao_altera_hp(self):
        """Borda: curar(0) não deve alterar o hp."""
        i = Inimigo("X", hp=10, atk=2, dificuldade=1, xp=10, moedas=3)
        i.hp = 7
        i.curar(0)
        assert i.hp == 7

    def test_curar_negativo_levanta_value_error(self):
        """Exceção: curar(-1) deve lançar ValueError."""
        i = Inimigo("X", hp=10, atk=2, dificuldade=1, xp=10, moedas=3)
        with pytest.raises(ValueError):
            i.curar(-1)

    def test_curar_com_hp_cheio_nao_altera(self):
        """Borda: curar() com HP já cheio não deve alterar nada."""
        i = Inimigo("X", hp=10, atk=2, dificuldade=1, xp=10, moedas=3)
        i.curar(5)
        assert i.hp == 10

    @pytest.mark.parametrize("hp_atual,cura,hp_esperado", [
        (5, 3,   8),
        (5, 10, 15),
        (1, 14, 15),
        (1, 99, 15),
    ])
    def test_curar_parametrizado(self, hp_atual, cura, hp_esperado):
        """Parametrizado: verifica hp resultante após diferentes curas (hp_max=15)."""
        i = Inimigo("X", hp=15, atk=2, dificuldade=1, xp=10, moedas=3)
        i.hp = hp_atual
        i.curar(cura)
        assert i.hp == hp_esperado


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 — absorcao_dano em receber_dano()
# ══════════════════════════════════════════════════════════════════════════════

class TestAbsorcaoDano:
    """Testa o comportamento de absorcao_dano processado em receber_dano()."""

    def test_absorcao_reduz_dano_recebido(self):
        """Mecânica: absorcao=2 deve reduzir ataque de força 5 para 3."""
        golem = Inimigo("Golem", hp=20, atk=3, dificuldade=2, xp=35, moedas=9,
                        absorcao_dano=2)
        dano = golem.receber_dano(5)
        assert dano     == 3
        assert golem.hp == 17

    def test_dano_menor_que_absorcao_resulta_zero(self):
        """Mecânica: ataque de força 1 com absorcao=2 → dano zero."""
        golem = Inimigo("Golem", hp=20, atk=3, dificuldade=2, xp=35, moedas=9,
                        absorcao_dano=2)
        hp_antes = golem.hp
        dano = golem.receber_dano(1)
        assert dano     == 0
        assert golem.hp == hp_antes

    def test_dano_exatamente_igual_a_absorcao_resulta_zero(self):
        """Borda: ataque de força 2 com absorcao=2 → exatamente zero."""
        golem = Inimigo("Golem", hp=20, atk=3, dificuldade=2, xp=35, moedas=9,
                        absorcao_dano=2)
        hp_antes = golem.hp
        dano = golem.receber_dano(2)
        assert dano     == 0
        assert golem.hp == hp_antes

    def test_sem_absorcao_comportamento_original(self):
        """Regressão: absorcao_dano=0 (padrão) deve manter o comportamento v2."""
        i = Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=15, moedas=5)
        dano = i.receber_dano(4)
        assert dano  == 4
        assert i.hp  == 6

    @pytest.mark.parametrize("forca,absorcao,dano_esperado", [
        (5, 0, 5),
        (5, 2, 3),
        (5, 5, 0),
        (5, 9, 0),
        (1, 2, 0),
        (3, 2, 1),
    ])
    def test_absorcao_parametrizada(self, forca, absorcao, dano_esperado):
        """Parametrizado: verifica dano efetivo para diferentes forças e absorções."""
        i = Inimigo("X", hp=50, atk=2, dificuldade=1, xp=10, moedas=3,
                    absorcao_dano=absorcao)
        assert i.receber_dano(forca) == dano_esperado


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 4 — Atributos especiais: valores padrão neutros
# ══════════════════════════════════════════════════════════════════════════════

class TestAtributosEspeciaisPadrao:
    """
    Testa que inimigos comuns criados sem os kwargs especiais
    têm todos os atributos no valor neutro.
    """

    def test_modificador_fuga_padrao_e_zero(self):
        """Padrão: modificador_fuga deve ser 0.0 para inimigos comuns."""
        i = Inimigo("Goblin", hp=5, atk=2, dificuldade=1, xp=10, moedas=3)
        assert i.modificador_fuga == 0.0

    def test_cura_percentual_padrao_e_zero(self):
        """Padrão: cura_percentual deve ser 0.0 para inimigos comuns."""
        i = Inimigo("Goblin", hp=5, atk=2, dificuldade=1, xp=10, moedas=3)
        assert i.cura_percentual == 0.0

    def test_absorcao_dano_padrao_e_zero(self):
        """Padrão: absorcao_dano deve ser 0 para inimigos comuns."""
        i = Inimigo("Goblin", hp=5, atk=2, dificuldade=1, xp=10, moedas=3)
        assert i.absorcao_dano == 0

    def test_bonus_atk_por_turno_padrao_e_zero(self):
        """Padrão: bonus_atk_por_turno deve ser 0 para inimigos comuns."""
        i = Inimigo("Goblin", hp=5, atk=2, dificuldade=1, xp=10, moedas=3)
        assert i.bonus_atk_por_turno == 0

    def test_chance_atordoar_padrao_e_zero(self):
        """Padrão: chance_atordoar deve ser 0.0 para inimigos comuns."""
        i = Inimigo("Goblin", hp=5, atk=2, dificuldade=1, xp=10, moedas=3)
        assert i.chance_atordoar == 0.0

    def test_tipo_especial_padrao_e_none(self):
        """Padrão: tipo_especial deve ser None para inimigos comuns."""
        i = Inimigo("Goblin", hp=5, atk=2, dificuldade=1, xp=10, moedas=3)
        assert i.tipo_especial is None

    def test_todos_os_atributos_especiais_neutros_juntos(self):
        """Conjunto: todos os atributos especiais neutros de uma vez."""
        i = Inimigo("Goblin", hp=5, atk=2, dificuldade=1, xp=10, moedas=3)
        assert i.modificador_fuga    == 0.0
        assert i.cura_percentual     == 0.0
        assert i.absorcao_dano       == 0
        assert i.bonus_atk_por_turno == 0
        assert i.chance_atordoar     == 0.0
        assert i.tipo_especial       is None


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 5 — Validações dos novos parâmetros do __init__
# ══════════════════════════════════════════════════════════════════════════════

class TestValidacoesNovasV3:
    """Testa as novas validações adicionadas ao __init__ na v3."""

    def test_cura_percentual_acima_de_um_levanta_value_error(self):
        """Exceção: cura_percentual=1.1 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("X", hp=10, atk=2, dificuldade=1, xp=5, moedas=1,
                    cura_percentual=1.1)

    def test_cura_percentual_negativa_levanta_value_error(self):
        """Exceção: cura_percentual=-0.1 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("X", hp=10, atk=2, dificuldade=1, xp=5, moedas=1,
                    cura_percentual=-0.1)

    def test_cura_percentual_exatamente_um_e_valido(self):
        """Borda: cura_percentual=1.0 deve ser aceito (cura 100% do dano)."""
        i = Inimigo("X", hp=10, atk=2, dificuldade=1, xp=5, moedas=1,
                    cura_percentual=1.0)
        assert i.cura_percentual == 1.0

    def test_cura_percentual_zero_e_valido(self):
        """Borda: cura_percentual=0.0 deve ser aceito (sem cura)."""
        i = Inimigo("X", hp=10, atk=2, dificuldade=1, xp=5, moedas=1,
                    cura_percentual=0.0)
        assert i.cura_percentual == 0.0

    def test_absorcao_dano_negativa_levanta_value_error(self):
        """Exceção: absorcao_dano=-1 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("X", hp=10, atk=2, dificuldade=1, xp=5, moedas=1,
                    absorcao_dano=-1)

    def test_bonus_atk_por_turno_negativo_levanta_value_error(self):
        """Exceção: bonus_atk_por_turno=-1 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("X", hp=10, atk=2, dificuldade=1, xp=5, moedas=1,
                    bonus_atk_por_turno=-1)

    def test_chance_atordoar_acima_de_um_levanta_value_error(self):
        """Exceção: chance_atordoar=1.5 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("X", hp=10, atk=2, dificuldade=1, xp=5, moedas=1,
                    chance_atordoar=1.5)

    def test_chance_atordoar_negativa_levanta_value_error(self):
        """Exceção: chance_atordoar=-0.1 deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("X", hp=10, atk=2, dificuldade=1, xp=5, moedas=1,
                    chance_atordoar=-0.1)

    def test_chance_atordoar_exatamente_um_e_valido(self):
        """Borda: chance_atordoar=1.0 deve ser aceito (atordoa sempre)."""
        i = Inimigo("X", hp=10, atk=2, dificuldade=1, xp=5, moedas=1,
                    chance_atordoar=1.0)
        assert i.chance_atordoar == 1.0


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 6 — Correções dos testes de test_inimigo.py que quebram na v3
#           (SUBSTITUA os métodos correspondentes em test_inimigo.py)
# ══════════════════════════════════════════════════════════════════════════════

class TestCorrecoesV3:
    """
    Versões corrigidas dos testes do test_inimigo.py original que quebram
    com o balanceamento v3.

    Principais mudanças:
      - Elite exige andar >= 5 (era >= 3). Testes com andar=3 → andar=5.
      - Moedas dif 1: 0-4 (era 0-5).
      - Moedas dif 2: 5-10 (era 6-11).
    """

    @patch("jogo.entidades.inimigo.random.random", return_value=0.11)
    @patch("jogo.entidades.inimigo.random.choice", return_value="Orc")
    @patch("jogo.entidades.inimigo.random.randint", side_effect=[12, 4, 40, 8])
    def test_mock_gera_inimigo_dificuldade_2_corrigido(
        self, mock_randint, mock_choice, mock_random
    ):
        """
        CORRIGIDO (era andar=3): Elite exige andar >= 5 na v3.
        random=0.11: horda? 0.11 > 0.10 → não. Elite? andar=5 >= 5 E 0.11 < 0.25 → sim.
        Sem especiais em andar=5 (primeiro é golem no andar=8).
        side_effect: hp=12, atk=4, xp=40, moedas=8.
        """
        inimigo = Inimigo.gerar(andar=5)
        assert inimigo.dificuldade == 2
        assert inimigo.nome        == "Orc"
        assert inimigo.hp          == 12
        assert inimigo.atk         == 4
        assert inimigo.xp          == 40
        assert inimigo.moedas      == 8

    @patch("jogo.entidades.inimigo.random.random", return_value=0.11)
    def test_elite_nao_aparece_antes_do_andar_5(self, mock_random):
        """
        CORRIGIDO (era 'antes do andar 3'): threshold subiu para andar 5.
        Com andar=4: andar >= 5 é falso → sempre dif 1.
        random=0.11: horda? 0.11 > 0.10 → não. Elite? andar=4 < 5 → não.
        """
        inimigo = Inimigo.gerar(andar=4)
        assert inimigo.dificuldade == 1

    @patch("jogo.entidades.inimigo.random.random", return_value=0.11)
    def test_inimigo_dif2_nome_pertence_ao_pool_correto_corrigido(self, mock_random):
        """
        CORRIGIDO (era andar=3): usa andar=5 para gerar elite.
        random=0.11: horda? 0.11 > 0.10 → não. Elite? 0.11 < 0.25 → sim.
        Sem especiais em andar=5 → elite comum do NOMES_DIFICULDADE_2.
        """
        inimigo = Inimigo.gerar(andar=5)
        assert inimigo.nome in NOMES_DIFICULDADE_2

    @patch("jogo.entidades.inimigo.random.random", return_value=0.50)
    def test_inimigo_dif1_moedas_dentro_do_range_corrigido(self, mock_random):
        """
        CORRIGIDO: range novo é 0-4 (era 0-5) na v3.
        random=0.50: horda? 0.50 > 0.10 → não. Elite? andar=1 < 5 → não.
        """
        for _ in range(30):
            i = Inimigo.gerar(andar=1)
            assert 0 <= i.moedas <= 4, f"moedas={i.moedas} fora do range 0-4"

    @patch("jogo.entidades.inimigo.random.random", return_value=0.11)
    def test_inimigo_dif2_moedas_dentro_do_range_corrigido(self, mock_random):
        """
        CORRIGIDO: andar=3→5, range 6-11→5-10 na v3.
        random=0.11: horda? 0.11 > 0.10 → não. Elite? 0.11 < 0.25 → sim.
        """
        for _ in range(30):
            i = Inimigo.gerar(andar=5)
            assert 5 <= i.moedas <= 10, f"moedas={i.moedas} fora do range 5-10"

    def test_inimigos_dif2_tem_moedas_maiores_que_dif1_em_media_corrigido(self):
        """
        CORRIGIDO: andar=3→5. Médias: dif1 ≈ 2, dif2 ≈ 7.5. Dif2 > Dif1.
        """
        with patch("jogo.entidades.inimigo.random.random", return_value=0.50):
            moedas_dif1 = [Inimigo.gerar(andar=1).moedas for _ in range(30)]
        with patch("jogo.entidades.inimigo.random.random", return_value=0.11):
            moedas_dif2 = [Inimigo.gerar(andar=5).moedas for _ in range(30)]
        assert (sum(moedas_dif2) / 30) > (sum(moedas_dif1) / 30)