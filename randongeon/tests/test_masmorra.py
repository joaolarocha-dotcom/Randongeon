"""
Suíte de testes unitários para jogo/sistemas/masmorra.py — v2

Mudanças em relação à versão anterior:
  - Todas as chamadas inline Inimigo(...) recebem 'moedas'.
  - Inimigos criados via __new__ recebem i.moedas = X.
  - resolver_combate() agora concede moedas — testes atualizados.
  - gerar_boss(): atributo moedas testado e escalonamento verificado.
  - gerar_mimico(): bloco de testes inteiramente novo.
  - Testes de moedas adicionados nos blocos de combate.

Execute com:
    pytest tests/test_masmorra.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
from jogo.entidades.jogador import Jogador
from jogo.entidades.inimigo import Inimigo
from jogo.entidades.item    import Item
from jogo.sistemas.masmorra import Masmorra, BOSS_A_CADA_ANDARES, CHANCE_FUGA
from jogo.sistemas.gerador  import GeradorSala


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS — Stubs de Gerador reutilizáveis
# ══════════════════════════════════════════════════════════════════════════════

def fake_gerador_inimigo(inimigo: Inimigo):
    """Stub: sempre retorna o inimigo fornecido."""
    class _FG:
        def gerar_sala(self, andar=1):
            return ("inimigo", inimigo, "Sala de teste.")
    return _FG()


def fake_gerador_item(item: Item):
    """Stub: sempre retorna o item fornecido."""
    class _FG:
        def gerar_sala(self, andar=1):
            return ("item", item, "Sala de teste.")
    return _FG()


def dummy_inimigo(hp=1, atk=0, xp=10, moedas=5):
    """
    Cria um Inimigo de teste via __new__ (ignora validação de atk=0).
    Inclui moedas — necessário na v2.
    """
    i             = Inimigo.__new__(Inimigo)
    i.nome        = "Dummy"
    i.hp          = hp
    i.atk         = atk
    i.dificuldade = 1
    i.xp          = xp
    i.moedas      = moedas
    return i


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 1 — Inicialização
# ══════════════════════════════════════════════════════════════════════════════

class TestInicializacao:
    """Testa o estado inicial da Masmorra após instanciação."""

    def test_andar_inicial_e_zero(self, masmorra_padrao):
        """Caminho feliz: andar deve começar em 0."""
        assert masmorra_padrao.andar == 0

    def test_desistiu_inicial_e_false(self, masmorra_padrao):
        """Caminho feliz: desistiu deve começar como False."""
        assert masmorra_padrao.desistiu is False

    def test_jogador_atribuido_corretamente(self, masmorra_padrao, jogador_padrao):
        """Caminho feliz: jogador deve ser o mesmo passado no construtor."""
        assert masmorra_padrao.jogador is jogador_padrao

    def test_gerador_padrao_criado_quando_none(self, jogador_padrao):
        """Borda: gerador=None deve criar um GeradorSala padrão."""
        m = Masmorra(jogador_padrao, gerador=None)
        assert isinstance(m.gerador, GeradorSala)

    def test_gerador_customizado_e_preservado(self, jogador_padrao):
        """Borda: gerador customizado (stub) deve ser armazenado sem substituição."""
        stub = MagicMock()
        m    = Masmorra(jogador_padrao, gerador=stub)
        assert m.gerador is stub

    def test_jogador_vivo_ao_iniciar(self, masmorra_padrao):
        """Invariante: jogador deve estar vivo ao iniciar qualquer run."""
        assert masmorra_padrao.jogador.esta_vivo() is True

    def test_jogador_sem_moedas_ao_iniciar(self, masmorra_padrao):
        """Invariante (novo v2): jogador começa sem moedas."""
        assert masmorra_padrao.jogador.moedas == 0


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 2 — resolver_combate(): resultado
# ══════════════════════════════════════════════════════════════════════════════

class TestResolverCombateResultado:
    """Testa os resultados possíveis de resolver_combate()."""

    def test_retorna_vitoria_contra_inimigo_fraco(self, masmorra_forte):
        """Caminho feliz: jogador forte vs inimigo fraco deve retornar 'vitoria'."""
        assert masmorra_forte.resolver_combate(dummy_inimigo()) == "vitoria"

    def test_retorna_derrota_contra_inimigo_forte(self, masmorra_padrao, inimigo_forte):
        """Caminho feliz: jogador padrão vs inimigo forte deve retornar 'derrota'."""
        assert masmorra_padrao.resolver_combate(inimigo_forte) == "derrota"

    def test_inimigo_none_levanta_value_error(self, masmorra_padrao):
        """Exceção: inimigo=None deve lançar ValueError."""
        with pytest.raises(ValueError):
            masmorra_padrao.resolver_combate(None)

    def test_retorno_e_string(self, masmorra_forte):
        """Tipo: resultado deve sempre ser uma string."""
        assert isinstance(masmorra_forte.resolver_combate(dummy_inimigo()), str)

    def test_retorno_e_valor_valido(self, masmorra_padrao, inimigo_forte):
        """Valores: resultado deve ser 'vitoria' ou 'derrota'."""
        resultado = masmorra_padrao.resolver_combate(inimigo_forte)
        assert resultado in ("vitoria", "derrota")


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 — resolver_combate(): efeitos colaterais
# ══════════════════════════════════════════════════════════════════════════════

class TestResolverCombateEfeitos:
    """Testa os efeitos colaterais de resolver_combate() no estado do jogo."""

    def test_vitoria_concede_xp_ao_jogador(self, masmorra_forte):
        """Caminho feliz: vitória deve aumentar o xp do jogador."""
        xp_antes = masmorra_forte.jogador.xp
        masmorra_forte.resolver_combate(dummy_inimigo(xp=10))
        assert masmorra_forte.jogador.xp > xp_antes

    def test_xp_concedido_igual_ao_xp_do_inimigo(self, masmorra_forte):
        """Caminho feliz: xp ganho deve ser exatamente o xp do inimigo."""
        xp_antes = masmorra_forte.jogador.xp
        masmorra_forte.resolver_combate(dummy_inimigo(xp=25))
        assert masmorra_forte.jogador.xp == xp_antes + 25

    def test_vitoria_concede_moedas_ao_jogador(self, masmorra_forte):
        """
        Caminho feliz (novo v2): vitória deve transferir moedas do inimigo.
        """
        moedas_antes = masmorra_forte.jogador.moedas
        masmorra_forte.resolver_combate(dummy_inimigo(moedas=7))
        assert masmorra_forte.jogador.moedas == moedas_antes + 7

    def test_moedas_concedidas_iguais_as_do_inimigo(self, masmorra_forte):
        """
        Caminho feliz (novo v2): moedas ganhas devem ser exatamente
        as moedas que o inimigo carregava.
        """
        masmorra_forte.resolver_combate(dummy_inimigo(moedas=12))
        assert masmorra_forte.jogador.moedas == 12

    def test_derrota_nao_concede_xp(self, masmorra_padrao, inimigo_forte):
        """Exceção de estado: derrota não deve conceder xp ao jogador."""
        xp_antes = masmorra_padrao.jogador.xp
        masmorra_padrao.resolver_combate(inimigo_forte)
        assert masmorra_padrao.jogador.xp == xp_antes

    def test_derrota_nao_concede_moedas(self, masmorra_padrao, inimigo_forte):
        """
        Exceção de estado (novo v2): derrota não deve conceder moedas.
        """
        moedas_antes = masmorra_padrao.jogador.moedas
        masmorra_padrao.resolver_combate(inimigo_forte)
        assert masmorra_padrao.jogador.moedas == moedas_antes

    def test_derrota_mata_o_jogador(self, masmorra_padrao, inimigo_forte):
        """Exceção de estado: após derrota, jogador deve estar morto."""
        masmorra_padrao.resolver_combate(inimigo_forte)
        assert masmorra_padrao.jogador.esta_vivo() is False

    def test_vitoria_mantem_jogador_vivo(self, masmorra_forte):
        """Caminho feliz: após vitória, jogador deve continuar vivo."""
        masmorra_forte.resolver_combate(dummy_inimigo())
        assert masmorra_forte.jogador.esta_vivo() is True

    def test_vitoria_elimina_inimigo(self, masmorra_forte):
        """Caminho feliz: após vitória, inimigo deve ter hp=0."""
        i = dummy_inimigo()
        masmorra_forte.resolver_combate(i)
        assert i.esta_vivo() is False

    def test_multiplas_vitorias_acumulam_xp_e_moedas(self, masmorra_forte):
        """
        Acúmulo (atualizado v2): xp e moedas devem se acumular
        corretamente em combates sequenciais.
        """
        for _ in range(3):
            masmorra_forte.resolver_combate(dummy_inimigo(xp=10, moedas=5))
        assert masmorra_forte.jogador.xp     == 30
        assert masmorra_forte.jogador.moedas == 15

    def test_dano_equilibrado_reduz_hp_dos_dois_lados(self):
        """Equilíbrio: em combate equilibrado, o jogador deve sofrer dano."""
        jogador = Jogador("Teste", hp=50, atk=3)
        m       = Masmorra(jogador)
        inimigo = Inimigo("Médio", hp=10, atk=5, dificuldade=1, xp=15, moedas=3)
        hp_antes = jogador.hp
        m.resolver_combate(inimigo)
        assert jogador.hp < hp_antes


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 4 — e_andar_de_boss()
# ══════════════════════════════════════════════════════════════════════════════

class TestEAndarDeBoss:
    """Testa a regra de aparição de bosses a cada BOSS_A_CADA_ANDARES andares."""

    def test_andar_zero_nao_e_boss(self, masmorra_padrao):
        """Borda: andar=0 nunca deve ser andar de boss."""
        masmorra_padrao.andar = 0
        assert masmorra_padrao.e_andar_de_boss() is False

    def test_andar_cinco_e_boss(self, masmorra_padrao):
        """Caminho feliz: andar=5 deve ser andar de boss."""
        masmorra_padrao.andar = BOSS_A_CADA_ANDARES
        assert masmorra_padrao.e_andar_de_boss() is True

    def test_andar_dez_e_boss(self, masmorra_padrao):
        """Caminho feliz: andar=10 deve ser andar de boss."""
        masmorra_padrao.andar = BOSS_A_CADA_ANDARES * 2
        assert masmorra_padrao.e_andar_de_boss() is True

    @pytest.mark.parametrize("andar_nao_boss", [1, 2, 3, 4, 6, 7, 8, 9, 11])
    def test_andares_intermediarios_nao_sao_boss(self, masmorra_padrao, andar_nao_boss):
        """Parametrizado: andares não múltiplos de 5 não devem ser de boss."""
        masmorra_padrao.andar = andar_nao_boss
        assert masmorra_padrao.e_andar_de_boss() is False

    @pytest.mark.parametrize("andar_boss", [5, 10, 15, 20, 25])
    def test_multiplos_de_cinco_sao_boss(self, masmorra_padrao, andar_boss):
        """Parametrizado: todos os múltiplos de 5 devem ser andares de boss."""
        masmorra_padrao.andar = andar_boss
        assert masmorra_padrao.e_andar_de_boss() is True


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 5 — gerar_boss() (atualizado v2 com moedas)
# ══════════════════════════════════════════════════════════════════════════════

class TestGerarBoss:
    """Testa a geração de bosses e seu escalonamento por andar."""

    def test_gerar_boss_retorna_instancia_de_inimigo(self, masmorra_padrao):
        """Caminho feliz: gerar_boss() deve retornar instância de Inimigo."""
        masmorra_padrao.andar = 5
        assert isinstance(masmorra_padrao.gerar_boss(), Inimigo)

    def test_boss_tem_dificuldade_3(self, masmorra_padrao):
        """Caminho feliz: boss deve ter dificuldade=3."""
        masmorra_padrao.andar = 5
        assert masmorra_padrao.gerar_boss().dificuldade == 3

    def test_boss_tem_hp_positivo(self, masmorra_padrao):
        """Caminho feliz: boss deve ter hp > 0."""
        masmorra_padrao.andar = 5
        assert masmorra_padrao.gerar_boss().hp > 0

    def test_boss_tem_atk_positivo(self, masmorra_padrao):
        """Caminho feliz: boss deve ter atk > 0."""
        masmorra_padrao.andar = 5
        assert masmorra_padrao.gerar_boss().atk > 0

    def test_boss_tem_xp_positivo(self, masmorra_padrao):
        """Caminho feliz: boss deve ter xp > 0."""
        masmorra_padrao.andar = 5
        assert masmorra_padrao.gerar_boss().xp > 0

    def test_boss_tem_moedas_positivas(self, masmorra_padrao):
        """Caminho feliz (novo v2): boss deve dropar moedas > 0."""
        masmorra_padrao.andar = 5
        assert masmorra_padrao.gerar_boss().moedas > 0

    def test_boss_andar_10_mais_forte_que_andar_5(self, masmorra_padrao):
        """Escalonamento: boss do andar 10 deve ter hp e atk maiores."""
        masmorra_padrao.andar = 5;  boss_5  = masmorra_padrao.gerar_boss()
        masmorra_padrao.andar = 10; boss_10 = masmorra_padrao.gerar_boss()
        assert boss_10.hp  > boss_5.hp
        assert boss_10.atk > boss_5.atk

    def test_boss_andar_10_tem_mais_moedas_que_andar_5(self, masmorra_padrao):
        """
        Escalonamento (novo v2): boss do andar 10 deve dropar mais moedas
        que o boss do andar 5.
        """
        masmorra_padrao.andar = 5;  boss_5  = masmorra_padrao.gerar_boss()
        masmorra_padrao.andar = 10; boss_10 = masmorra_padrao.gerar_boss()
        assert boss_10.moedas > boss_5.moedas

    def test_boss_xp_escala_com_andar(self, masmorra_padrao):
        """Escalonamento: xp do boss deve aumentar a cada nível de boss."""
        masmorra_padrao.andar = 5;  xp_5  = masmorra_padrao.gerar_boss().xp
        masmorra_padrao.andar = 10; xp_10 = masmorra_padrao.gerar_boss().xp
        assert xp_10 > xp_5

    def test_nome_boss_contem_numero_do_andar(self, masmorra_padrao):
        """Identificação: nome do boss deve conter o número do andar atual."""
        masmorra_padrao.andar = 5
        assert "5" in masmorra_padrao.gerar_boss().nome


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 6 (NOVO v2) — gerar_mimico()
# ══════════════════════════════════════════════════════════════════════════════

class TestGerarMimico:
    """Testa a geração do Mímico — inimigo especial novo na v2."""

    def test_gerar_mimico_retorna_instancia_de_inimigo(self, masmorra_padrao):
        """Caminho feliz: gerar_mimico() deve retornar instância de Inimigo."""
        assert isinstance(masmorra_padrao.gerar_mimico(), Inimigo)

    def test_mimico_tem_nome_correto(self, masmorra_padrao):
        """Caminho feliz: nome do Mímico deve ser 'Mimico'."""
        mimico = masmorra_padrao.gerar_mimico()
        assert "imico" in mimico.nome   # cobre 'Mimico' e 'Mímico'

    def test_mimico_tem_dificuldade_2(self, masmorra_padrao):
        """Caminho feliz: Mímico é um inimigo elite (dificuldade=2)."""
        assert masmorra_padrao.gerar_mimico().dificuldade == 2

    def test_mimico_tem_hp_positivo(self, masmorra_padrao):
        """Caminho feliz: Mímico deve ter hp > 0."""
        assert masmorra_padrao.gerar_mimico().hp > 0

    def test_mimico_tem_atk_positivo(self, masmorra_padrao):
        """Caminho feliz: Mímico deve ter atk > 0."""
        assert masmorra_padrao.gerar_mimico().atk > 0

    def test_mimico_tem_xp_positivo(self, masmorra_padrao):
        """Caminho feliz: Mímico deve recompensar xp > 0."""
        assert masmorra_padrao.gerar_mimico().xp > 0

    def test_mimico_tem_moedas_positivas(self, masmorra_padrao):
        """Caminho feliz (novo v2): Mímico deve dropar moedas > 0."""
        assert masmorra_padrao.gerar_mimico().moedas > 0

    def test_mimico_e_sempre_igual(self, masmorra_padrao):
        """
        Invariante: ao contrário dos inimigos comuns, o Mímico
        tem atributos fixos — cada chamada deve retornar o mesmo resultado.
        """
        m1 = masmorra_padrao.gerar_mimico()
        m2 = masmorra_padrao.gerar_mimico()
        assert m1.hp     == m2.hp
        assert m1.atk    == m2.atk
        assert m1.xp     == m2.xp
        assert m1.moedas == m2.moedas

    def test_mimico_e_mais_forte_que_inimigo_comum_andar_1(self, masmorra_padrao):
        """
        Comparação: o Mímico (dif=2) deve ser mais forte que um
        inimigo comum gerado no andar 1 em média.
        """
        mimico = masmorra_padrao.gerar_mimico()
        medias_comuns = [Inimigo.gerar(andar=1).xp for _ in range(20)]
        media_comum = sum(medias_comuns) / len(medias_comuns)
        assert mimico.xp > media_comum

    def test_derrota_contra_mimico_remove_hp_do_jogador(self, masmorra_padrao):
        """
        Integração: um combate contra o Mímico deve de fato reduzir
        o hp do jogador (inimigo não é trivial).
        """
        mimico = masmorra_padrao.gerar_mimico()
        hp_antes = masmorra_padrao.jogador.hp
        masmorra_padrao.resolver_combate(mimico)
        # Independente do resultado, o Mímico ataca (atk>0)
        assert masmorra_padrao.jogador.hp < hp_antes


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 7 — aplicar_item()
# ══════════════════════════════════════════════════════════════════════════════

class TestAplicarItem:
    """Testa o método aplicar_item() da Masmorra."""

    def test_aplicar_item_cura_aumenta_hp(self, masmorra_padrao):
        """Caminho feliz: item de cura deve aumentar o hp do jogador."""
        masmorra_padrao.jogador.hp = 10
        masmorra_padrao.aplicar_item(Item("Poção", bonus_hp=5))
        assert masmorra_padrao.jogador.hp == 15

    def test_aplicar_item_retorna_resultado_correto(self, masmorra_padrao):
        """Caminho feliz: deve retornar o dict com os efeitos aplicados."""
        masmorra_padrao.jogador.hp = 10
        resultado = masmorra_padrao.aplicar_item(Item("Poção", bonus_hp=5))
        assert "hp" in resultado and resultado["hp"] == 5

    def test_aplicar_item_ataque_aumenta_atk(self, masmorra_padrao):
        """Caminho feliz: item de ataque deve aumentar o atk do jogador."""
        atk_antes = masmorra_padrao.jogador.atk
        masmorra_padrao.aplicar_item(Item("Espada", bonus_atk=3))
        assert masmorra_padrao.jogador.atk == atk_antes + 3

    def test_aplicar_item_esquiva_aumenta_esq(self, masmorra_padrao):
        """Caminho feliz (novo v2): item de esquiva deve aumentar a esq."""
        esq_antes = masmorra_padrao.jogador.esq
        masmorra_padrao.aplicar_item(Item("Poção Gato", bonus_esq=0.1))
        assert round(masmorra_padrao.jogador.esq, 2) == round(esq_antes + 0.1, 2)

    def test_aplicar_item_none_levanta_value_error(self, masmorra_padrao):
        """Exceção: item=None deve lançar ValueError."""
        with pytest.raises(ValueError):
            masmorra_padrao.aplicar_item(None)

    def test_aplicar_item_com_mock_verifica_delegacao(self, masmorra_padrao):
        """Mock: aplicar_item() deve delegar para item.usar() com o jogador correto."""
        item_mock = MagicMock()
        item_mock.usar.return_value = {"hp": 5}
        masmorra_padrao.aplicar_item(item_mock)
        item_mock.usar.assert_called_once_with(masmorra_padrao.jogador)


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 8 — tentar_fuga()
# ══════════════════════════════════════════════════════════════════════════════

class TestTentarFuga:
    """Testa o sistema de fuga com mock de random.random."""

    @patch("jogo.sistemas.masmorra.random.random", return_value=0.1)
    def test_fuga_bem_sucedida_quando_random_abaixo_de_chance(self, _, masmorra_padrao):
        """Mock: random.random=0.1 < CHANCE_FUGA(0.5) → fuga deve ter sucesso."""
        assert masmorra_padrao.tentar_fuga() is True

    @patch("jogo.sistemas.masmorra.random.random", return_value=0.9)
    def test_fuga_falha_quando_random_acima_de_chance(self, _, masmorra_padrao):
        """Mock: random.random=0.9 > CHANCE_FUGA(0.5) → fuga deve falhar."""
        assert masmorra_padrao.tentar_fuga() is False

    @patch("jogo.sistemas.masmorra.random.random", return_value=CHANCE_FUGA - 0.01)
    def test_fuga_sucesso_exatamente_abaixo_do_limiar(self, _, masmorra_padrao):
        """Borda: valor imediatamente abaixo de CHANCE_FUGA deve ser sucesso."""
        assert masmorra_padrao.tentar_fuga() is True

    @patch("jogo.sistemas.masmorra.random.random", return_value=CHANCE_FUGA + 0.01)
    def test_fuga_falha_exatamente_acima_do_limiar(self, _, masmorra_padrao):
        """Borda: valor imediatamente acima de CHANCE_FUGA deve falhar."""
        assert masmorra_padrao.tentar_fuga() is False

    def test_tentar_fuga_retorna_bool(self, masmorra_padrao):
        """Tipo: tentar_fuga() deve sempre retornar um bool."""
        assert isinstance(masmorra_padrao.tentar_fuga(), bool)


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 9 — Sequências de integração
# ══════════════════════════════════════════════════════════════════════════════

class TestSequenciasIntegracao:
    """
    Testa sequências de operações que simulam situações reais do jogo,
    usando stubs para eliminar aleatoriedade.
    """

    def test_vitoria_seguida_de_xp_e_moedas(self, jogador_forte):
        """
        Integração (atualizado v2): dois combates devem acumular
        xp E moedas corretamente.
        """
        m = Masmorra(jogador_forte)
        m.resolver_combate(dummy_inimigo(xp=10, moedas=5))
        m.resolver_combate(dummy_inimigo(xp=20, moedas=8))
        assert jogador_forte.xp     == 30
        assert jogador_forte.moedas == 13
        assert jogador_forte.esta_vivo() is True

    def test_derrota_encerra_jogabilidade(self, jogador_padrao, inimigo_forte):
        """Integração: após derrota, jogador.esta_vivo() deve ser False."""
        Masmorra(jogador_padrao).resolver_combate(inimigo_forte)
        assert not jogador_padrao.esta_vivo()

    def test_item_de_esquiva_antes_de_combate(self):
        """
        Integração (novo v2): usar item de esquiva antes de combate
        deve aumentar a esq do jogador.
        """
        j = Jogador("Ninja", hp=20, atk=5, esq=0.3)
        m = Masmorra(j)
        esq_antes = j.esq
        m.aplicar_item(Item("Poção Gato", bonus_esq=0.1))
        assert round(j.esq, 2) == round(esq_antes + 0.1, 2)

    def test_boss_mais_forte_que_inimigo_comum_no_mesmo_andar(self, masmorra_padrao):
        """Comparação: boss gerado deve ter mais hp e atk que inimigo comum."""
        masmorra_padrao.andar = 5
        boss  = masmorra_padrao.gerar_boss()
        comum = Inimigo.gerar(andar=5)
        assert boss.hp  > comum.hp
        assert boss.atk > comum.atk

    def test_mimico_concede_moedas_apos_vitoria(self, masmorra_forte):
        """
        Integração (novo v2): derrotar o Mímico deve conceder suas moedas
        ao jogador via resolver_combate().
        """
        mimico = masmorra_forte.gerar_mimico()
        moedas_do_mimico = mimico.moedas
        moedas_antes     = masmorra_forte.jogador.moedas
        resultado = masmorra_forte.resolver_combate(mimico)
        assert resultado == "vitoria"
        assert masmorra_forte.jogador.moedas == moedas_antes + moedas_do_mimico

    def test_estado_masmorra_consistente_apos_combate_e_item(self):
        """Estado: após combate + item, o estado da masmorra deve ser consistente."""
        j = Jogador("Consistente", hp=20, atk=50)
        j.hp = 10
        m = Masmorra(j)

        fraco = dummy_inimigo(hp=1, atk=0, xp=15, moedas=8)
        m.resolver_combate(fraco)
        assert j.xp == 15 and j.moedas == 8 and j.esta_vivo()

        m.aplicar_item(Item("Poção", bonus_hp=5))
        assert j.hp == 15

        assert m.desistiu is False
        assert m.andar    == 0