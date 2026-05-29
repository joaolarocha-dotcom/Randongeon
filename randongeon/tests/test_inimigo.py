import pytest
from unittest.mock import patch
from jogo.entidades.inimigo import Inimigo, NOMES_DIFICULDADE_1, NOMES_DIFICULDADE_2

class TestCriacaoInimigo:
    def test_atributos_iniciais_corretos(self, inimigo_padrao):
        assert inimigo_padrao.nome        == "Goblin"
        assert inimigo_padrao.hp          == 10
        assert inimigo_padrao.atk         == 3
        assert inimigo_padrao.dificuldade == 1
        assert inimigo_padrao.xp          == 15
        assert inimigo_padrao.moedas      == 5

    def test_criacao_com_dificuldade_maxima(self):
        boss = Inimigo("Dragão", hp=50, atk=20, dificuldade=3, xp=200, moedas=100)
        assert boss.dificuldade == 3
        assert boss.moedas      == 100

    def test_criacao_com_moedas_zero(self):
        i = Inimigo("Fantasma", hp=5, atk=2, dificuldade=1, xp=10, moedas=0)
        assert i.moedas == 0

    @pytest.mark.parametrize("nome_invalido", ["", None, 42])
    def test_nome_invalido_levanta_value_error(self, nome_invalido):
        with pytest.raises(ValueError):
            Inimigo(nome_invalido, hp=10, atk=3, dificuldade=1, xp=10, moedas=0)

    @pytest.mark.parametrize("hp_invalido", [0, -1, -50])
    def test_hp_invalido_levanta_value_error(self, hp_invalido):
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=hp_invalido, atk=3, dificuldade=1, xp=10, moedas=0)

    @pytest.mark.parametrize("atk_invalido", [0, -1, -10])
    def test_atk_invalido_levanta_value_error(self, atk_invalido):
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=10, atk=atk_invalido, dificuldade=1, xp=10, moedas=0)

    def test_dificuldade_zero_levanta_value_error(self):
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=10, atk=3, dificuldade=0, xp=10, moedas=0)

    def test_xp_negativo_levanta_value_error(self):
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=-5, moedas=0)

    def test_moedas_negativas_levanta_value_error(self):
        with pytest.raises(ValueError):
            Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=10, moedas=-1)

    def test_xp_zero_e_valido(self):
        i = Inimigo("Sombra", hp=5, atk=2, dificuldade=1, xp=0, moedas=0)
        assert i.xp == 0

class TestEstaVivo:
    def test_vivo_quando_hp_maior_que_zero(self, inimigo_padrao):
        assert inimigo_padrao.esta_vivo() is True

    def test_morto_quando_hp_igual_a_zero(self, inimigo_padrao):
        inimigo_padrao.hp = 0
        assert inimigo_padrao.esta_vivo() is False

    def test_morto_apos_dano_letal(self, inimigo_padrao):
        inimigo_padrao.receber_dano(10)
        assert inimigo_padrao.esta_vivo() is False

class TestReceberDano:
    def test_dano_reduz_hp_corretamente(self, inimigo_padrao):
        inimigo_padrao.receber_dano(4)
        assert inimigo_padrao.hp == 6

    def test_retorna_dano_efetivo(self, inimigo_padrao):
        assert inimigo_padrao.receber_dano(4) == 4

    def test_hp_nao_fica_negativo(self, inimigo_padrao):
        inimigo_padrao.receber_dano(9999)
        assert inimigo_padrao.hp == 0

    def test_dano_excessivo_retorna_hp_disponivel(self, inimigo_padrao):
        assert inimigo_padrao.receber_dano(9999) == 10

    def test_dano_zero_nao_altera_hp(self, inimigo_padrao):
        inimigo_padrao.receber_dano(0)
        assert inimigo_padrao.hp == 10

    def test_dano_negativo_levanta_value_error(self, inimigo_padrao):
        with pytest.raises(ValueError):
            inimigo_padrao.receber_dano(-3)

    @pytest.mark.parametrize("dano,hp_esperado", [
        (0,   10),
        (3,    7),
        (10,   0),
        (100,  0),
    ])
    def test_dano_parametrizado(self, inimigo_padrao, dano, hp_esperado):
        inimigo_padrao.receber_dano(dano)
        assert inimigo_padrao.hp == hp_esperado

class TestGerar:
    def test_gerar_retorna_instancia_de_inimigo(self):
        inimigo = Inimigo.gerar(andar=1)
        assert isinstance(inimigo, Inimigo)

    def test_inimigo_gerado_tem_hp_positivo(self):
        assert Inimigo.gerar(andar=1).hp > 0

    def test_inimigo_gerado_tem_xp_nao_negativo(self):
        assert Inimigo.gerar(andar=1).xp >= 0

    def test_inimigo_gerado_tem_moedas_nao_negativas(self):
        assert Inimigo.gerar(andar=1).moedas >= 0

    def test_andar_zero_levanta_value_error(self):
        with pytest.raises(ValueError):
            Inimigo.gerar(andar=0)

    def test_andar_negativo_levanta_value_error(self):
        with pytest.raises(ValueError):
            Inimigo.gerar(andar=-1)

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    @patch("jogo.entidades.inimigo.random.choice", return_value="Goblin")
    @patch("jogo.entidades.inimigo.random.randint", side_effect=[5, 2, 15, 3])
    def test_mock_gera_inimigo_dificuldade_1(self, mock_randint, mock_choice, mock_random):
        inimigo = Inimigo.gerar(andar=3)
        assert inimigo.dificuldade == 1
        assert inimigo.nome        == "Goblin"
        assert inimigo.hp          == 5
        assert inimigo.atk         == 2
        assert inimigo.xp          == 15
        assert inimigo.moedas      == 3

    @patch("jogo.entidades.inimigo.random.random", return_value=0.1)
    @patch("jogo.entidades.inimigo.random.choice", return_value="Orc")
    @patch("jogo.entidades.inimigo.random.randint", side_effect=[12, 4, 40, 8])
    def test_mock_gera_inimigo_dificuldade_2(self, mock_randint, mock_choice, mock_random):
        inimigo = Inimigo.gerar(andar=5)
        assert inimigo.dificuldade == 2
        assert inimigo.nome        == "Orc"
        assert inimigo.hp          == 12
        assert inimigo.atk         == 4
        assert inimigo.xp          == 40
        assert inimigo.moedas      == 8

    @patch("jogo.entidades.inimigo.random.random", return_value=0.1)
    def test_elite_nao_aparece_antes_do_andar_3(self, mock_random):
        inimigo = Inimigo.gerar(andar=2)
        assert inimigo.dificuldade == 1

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    def test_dificuldade_1_sem_elite_no_andar_1(self, mock_random):
        assert Inimigo.gerar(andar=1).dificuldade == 1

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    def test_inimigo_dif1_nome_pertence_ao_pool_correto(self, mock_random):
        assert Inimigo.gerar(andar=1).nome in NOMES_DIFICULDADE_1

    @patch("jogo.entidades.inimigo.random.random", return_value=0.1)
    def test_inimigo_dif2_nome_pertence_ao_pool_correto(self, mock_random):
        assert Inimigo.gerar(andar=5).nome in NOMES_DIFICULDADE_2

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    def test_inimigo_dif1_moedas_dentro_do_range(self, mock_random):
        for _ in range(20):
            i = Inimigo.gerar(andar=1)
            assert 0 <= i.moedas <= 4

    @patch("jogo.entidades.inimigo.random.random", return_value=0.1)
    def test_inimigo_dif2_moedas_dentro_do_range(self, mock_random):
        for _ in range(20):
            i = Inimigo.gerar(andar=5)
            assert 5 <= i.moedas <= 10

class TestEscalonamentoPorAndar:
    def test_inimigos_andar_alto_tem_hp_medio_maior(self):
        hp_andar_1  = [Inimigo.gerar(andar=1).hp  for _ in range(30)]
        hp_andar_10 = [Inimigo.gerar(andar=10).hp for _ in range(30)]
        assert (sum(hp_andar_10) / 30) >= (sum(hp_andar_1) / 30)

    def test_todo_inimigo_gerado_e_instancia_valida(self):
        for andar in [1, 2, 3, 5, 10]:
            i = Inimigo.gerar(andar=andar)
            assert isinstance(i, Inimigo)
            assert i.hp   > 0
            assert i.atk  > 0
            assert i.dificuldade >= 1
            assert i.moedas      >= 0

    def test_inimigos_dif2_tem_moedas_maiores_que_dif1_em_media(self):
        with patch("jogo.entidades.inimigo.random.random", return_value=0.9):
            moedas_dif1 = [Inimigo.gerar(andar=1).moedas for _ in range(20)]
        with patch("jogo.entidades.inimigo.random.random", return_value=0.1):
            moedas_dif2 = [Inimigo.gerar(andar=5).moedas for _ in range(20)]
        assert (sum(moedas_dif2) / 20) > (sum(moedas_dif1) / 20)

class TestRepresentacao:
    def test_repr_contem_nome(self, inimigo_padrao):
        assert "Goblin" in repr(inimigo_padrao)

    def test_repr_contem_hp(self, inimigo_padrao):
        assert "10" in repr(inimigo_padrao)

    def test_repr_contem_atk(self, inimigo_padrao):
        assert "3" in repr(inimigo_padrao)