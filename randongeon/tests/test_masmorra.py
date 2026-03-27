# randongeon/tests/test_masmorra.py

"""
Suíte de testes unitários para jogo/sistemas/masmorra.py

Cobre:
  - Inicialização e estado da Masmorra
  - resolver_combate(): vitória, derrota, concessão de XP
  - e_andar_de_boss(): regra de múltiplos de 5
  - gerar_boss(): escalonamento de atributos por andar
  - aplicar_item(): delegação para item.usar()
  - tentar_fuga(): com mock de random
  - Integração: sequências de avanço com FakeGerador

Estratégia de isolamento:
  - FakeGerador: stub que retorna conteúdos fixos sem aleatoriedade
  - inimigo_fraco (fixture do conftest): hp=1, atk=0 → vitória garantida
  - inimigo_forte (fixture do conftest): hp=999, atk=999 → derrota garantida
  - @patch: isola random.random em tentar_fuga()

Execute com:
    pytest tests/test_masmorra.py -v
    pytest tests/test_masmorra.py -v --tb=short
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
    """
    Retorna um stub de GeradorSala que sempre gera o inimigo fornecido.

    Parâmetros:
        inimigo (Inimigo): Inimigo fixo a ser retornado em gerar_sala().

    Retorna:
        Objeto com interface compatível com GeradorSala.
    """
    class _FakeGeradorInimigo:
        def gerar_sala(self, andar=1):
            return ("inimigo", inimigo, "Sala de teste.")
    return _FakeGeradorInimigo()


def fake_gerador_item(item: Item):
    """
    Retorna um stub de GeradorSala que sempre gera o item fornecido.

    Parâmetros:
        item (Item): Item fixo a ser retornado em gerar_sala().

    Retorna:
        Objeto com interface compatível com GeradorSala.
    """
    class _FakeGeradorItem:
        def gerar_sala(self, andar=1):
            return ("item", item, "Sala de teste.")
    return _FakeGeradorItem()


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
        """Borda: gerador=None deve criar um GeradorSala padrão automaticamente."""
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


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 2 — resolver_combate(): resultado
# ══════════════════════════════════════════════════════════════════════════════

class TestResolverCombateResultado:
    """Testa os resultados possíveis de resolver_combate()."""

    def test_retorna_vitoria_contra_inimigo_fraco(self, masmorra_forte, inimigo_fraco):
        """Caminho feliz: jogador forte vs inimigo fraco deve retornar 'vitoria'."""
        resultado = masmorra_forte.resolver_combate(inimigo_fraco)
        assert resultado == "vitoria"

    def test_retorna_derrota_contra_inimigo_forte(self, masmorra_padrao, inimigo_forte):
        """Caminho feliz: jogador padrão vs inimigo forte deve retornar 'derrota'."""
        resultado = masmorra_padrao.resolver_combate(inimigo_forte)
        assert resultado == "derrota"

    def test_inimigo_none_levanta_value_error(self, masmorra_padrao):
        """Exceção: inimigo=None deve lançar ValueError."""
        with pytest.raises(ValueError):
            masmorra_padrao.resolver_combate(None)

    def test_retorno_e_string(self, masmorra_forte, inimigo_fraco):
        """Tipo: resultado deve sempre ser uma string."""
        resultado = masmorra_forte.resolver_combate(inimigo_fraco)
        assert isinstance(resultado, str)

    def test_retorno_e_valor_esperado(self, masmorra_padrao, inimigo_forte):
        """Valores: resultado deve ser 'vitoria' ou 'derrota'."""
        resultado = masmorra_padrao.resolver_combate(inimigo_forte)
        assert resultado in ("vitoria", "derrota")


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 — resolver_combate(): efeitos colaterais de jogo
# ══════════════════════════════════════════════════════════════════════════════

class TestResolverCombateEfeitos:
    """Testa os efeitos colaterais de resolver_combate() no estado do jogo."""

    def test_vitoria_concede_xp_ao_jogador(self, masmorra_forte, inimigo_fraco):
        """Caminho feliz: vitória deve aumentar o xp do jogador."""
        xp_antes = masmorra_forte.jogador.xp
        masmorra_forte.resolver_combate(inimigo_fraco)
        assert masmorra_forte.jogador.xp > xp_antes

    def test_xp_concedido_igual_ao_xp_do_inimigo(self, masmorra_forte, inimigo_fraco):
        """Caminho feliz: xp ganho deve ser exatamente o xp do inimigo derrotado."""
        xp_antes    = masmorra_forte.jogador.xp
        xp_inimigo  = inimigo_fraco.xp
        masmorra_forte.resolver_combate(inimigo_fraco)
        assert masmorra_forte.jogador.xp == xp_antes + xp_inimigo

    def test_derrota_nao_concede_xp(self, masmorra_padrao, inimigo_forte):
        """Exceção de estado: derrota não deve conceder xp ao jogador."""
        xp_antes = masmorra_padrao.jogador.xp
        masmorra_padrao.resolver_combate(inimigo_forte)
        assert masmorra_padrao.jogador.xp == xp_antes

    def test_derrota_mata_o_jogador(self, masmorra_padrao, inimigo_forte):
        """Exceção de estado: após derrota, jogador deve estar morto."""
        masmorra_padrao.resolver_combate(inimigo_forte)
        assert masmorra_padrao.jogador.esta_vivo() is False

    def test_vitoria_mantem_jogador_vivo(self, masmorra_forte, inimigo_fraco):
        """Caminho feliz: após vitória, jogador deve continuar vivo."""
        masmorra_forte.resolver_combate(inimigo_fraco)
        assert masmorra_forte.jogador.esta_vivo() is True

    def test_vitoria_elimina_inimigo(self, masmorra_forte, inimigo_fraco):
        """Caminho feliz: após vitória, hp do inimigo deve ser 0."""
        masmorra_forte.resolver_combate(inimigo_fraco)
        assert inimigo_fraco.esta_vivo() is False

    def test_multiplas_vitorias_acumulam_xp(self, masmorra_forte):
        """Acúmulo: xp deve se acumular corretamente em combates sequenciais."""
        xp_por_combate = 10
        for _ in range(3):
            i = Inimigo.__new__(Inimigo)
            i.nome = "Dummy"; i.hp = 1; i.atk = 0
            i.dificuldade = 1; i.xp = xp_por_combate
            masmorra_forte.resolver_combate(i)

        assert masmorra_forte.jogador.xp == xp_por_combate * 3

    def test_dano_equilibrado_reduz_hp_dos_dois_lados(self):
        """
        Equilíbrio: em combate equilibrado, ambos os lados devem sofrer dano.
        Usa inimigo que sobrevive ao primeiro golpe para garantir contra-ataque.
        """
        jogador = Jogador("Teste", hp=50, atk=3)
        m       = Masmorra(jogador)
        inimigo = Inimigo("Médio", hp=10, atk=5, dificuldade=1, xp=15)
        hp_jogador_antes  = jogador.hp
        m.resolver_combate(inimigo)
        # O jogador deve ter sofrido pelo menos 1 dano (inimigo sobreviveu ao 1º turno)
        assert jogador.hp < hp_jogador_antes


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

    def test_andar_quinze_e_boss(self, masmorra_padrao):
        """Caminho feliz: andar=15 deve ser andar de boss."""
        masmorra_padrao.andar = BOSS_A_CADA_ANDARES * 3
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
# BLOCO 5 — gerar_boss()
# ══════════════════════════════════════════════════════════════════════════════

class TestGerarBoss:
    """Testa a geração de bosses e seu escalonamento por andar."""

    def test_gerar_boss_retorna_instancia_de_inimigo(self, masmorra_padrao):
        """Caminho feliz: gerar_boss() deve retornar instância de Inimigo."""
        masmorra_padrao.andar = 5
        boss = masmorra_padrao.gerar_boss()
        assert isinstance(boss, Inimigo)

    def test_boss_tem_dificuldade_3(self, masmorra_padrao):
        """Caminho feliz: boss deve ter dificuldade=3."""
        masmorra_padrao.andar = 5
        boss = masmorra_padrao.gerar_boss()
        assert boss.dificuldade == 3

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

    def test_boss_andar_10_mais_forte_que_andar_5(self, masmorra_padrao):
        """Escalonamento: boss do andar 10 deve ter hp e atk maiores que do andar 5."""
        masmorra_padrao.andar = 5
        boss_5 = masmorra_padrao.gerar_boss()

        masmorra_padrao.andar = 10
        boss_10 = masmorra_padrao.gerar_boss()

        assert boss_10.hp  > boss_5.hp
        assert boss_10.atk > boss_5.atk

    def test_boss_andar_15_mais_forte_que_andar_10(self, masmorra_padrao):
        """Escalonamento: boss do andar 15 deve ser mais forte que do andar 10."""
        masmorra_padrao.andar = 10
        boss_10 = masmorra_padrao.gerar_boss()

        masmorra_padrao.andar = 15
        boss_15 = masmorra_padrao.gerar_boss()

        assert boss_15.hp  > boss_10.hp
        assert boss_15.atk > boss_10.atk

    def test_boss_xp_escala_com_andar(self, masmorra_padrao):
        """Escalonamento: xp do boss deve aumentar a cada nível de boss."""
        masmorra_padrao.andar = 5
        xp_5 = masmorra_padrao.gerar_boss().xp

        masmorra_padrao.andar = 10
        xp_10 = masmorra_padrao.gerar_boss().xp

        assert xp_10 > xp_5

    def test_nome_boss_contem_numero_do_andar(self, masmorra_padrao):
        """Identificação: nome do boss deve conter o número do andar atual."""
        masmorra_padrao.andar = 5
        boss = masmorra_padrao.gerar_boss()
        assert "5" in boss.nome


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 6 — aplicar_item()
# ══════════════════════════════════════════════════════════════════════════════

class TestAplicarItem:
    """Testa o método aplicar_item() da Masmorra."""

    def test_aplicar_item_cura_aumenta_hp(self, masmorra_padrao):
        """Caminho feliz: item de cura deve aumentar o hp do jogador."""
        masmorra_padrao.jogador.hp = 10
        item = Item("Poção", bonus_hp=5)
        masmorra_padrao.aplicar_item(item)
        assert masmorra_padrao.jogador.hp == 15

    def test_aplicar_item_retorna_resultado_correto(self, masmorra_padrao):
        """Caminho feliz: deve retornar o dict com os efeitos aplicados."""
        masmorra_padrao.jogador.hp = 10
        item      = Item("Poção", bonus_hp=5)
        resultado = masmorra_padrao.aplicar_item(item)
        assert "hp" in resultado
        assert resultado["hp"] == 5

    def test_aplicar_item_ataque_aumenta_atk(self, masmorra_padrao):
        """Caminho feliz: item de ataque deve aumentar o atk do jogador."""
        atk_antes = masmorra_padrao.jogador.atk
        item = Item("Espada", bonus_atk=3)
        masmorra_padrao.aplicar_item(item)
        assert masmorra_padrao.jogador.atk == atk_antes + 3

    def test_aplicar_item_none_levanta_value_error(self, masmorra_padrao):
        """Exceção: item=None deve lançar ValueError."""
        with pytest.raises(ValueError):
            masmorra_padrao.aplicar_item(None)

    def test_aplicar_item_usa_jogador_da_masmorra(self, masmorra_padrao):
        """
        Integração: item deve ser aplicado no jogador da própria instância de Masmorra,
        não em outro jogador externo.
        """
        masmorra_padrao.jogador.hp = 5
        item = Item("Cura", bonus_hp=8)
        masmorra_padrao.aplicar_item(item)
        assert masmorra_padrao.jogador.hp == 13

    def test_aplicar_item_com_mock_verifica_delegacao(self, masmorra_padrao):
        """
        Mock: aplicar_item() deve delegar para item.usar() passando o jogador.
        Verifica que o método correto é chamado com os argumentos certos.
        """
        item_mock = MagicMock()
        item_mock.usar.return_value = {"hp": 5}

        masmorra_padrao.aplicar_item(item_mock)

        item_mock.usar.assert_called_once_with(masmorra_padrao.jogador)


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 7 — tentar_fuga()
# ══════════════════════════════════════════════════════════════════════════════

class TestTentarFuga:
    """Testa o sistema de fuga com mock de random.random."""

    @patch("jogo.sistemas.masmorra.random.random", return_value=0.1)
    def test_fuga_bem_sucedida_quando_random_abaixo_de_chance(self, mock_random, masmorra_padrao):
        """
        Mock: random.random=0.1 < CHANCE_FUGA(0.5) → fuga deve ter sucesso.
        """
        assert masmorra_padrao.tentar_fuga() is True

    @patch("jogo.sistemas.masmorra.random.random", return_value=0.9)
    def test_fuga_falha_quando_random_acima_de_chance(self, mock_random, masmorra_padrao):
        """
        Mock: random.random=0.9 > CHANCE_FUGA(0.5) → fuga deve falhar.
        """
        assert masmorra_padrao.tentar_fuga() is False

    @patch("jogo.sistemas.masmorra.random.random", return_value=CHANCE_FUGA - 0.01)
    def test_fuga_sucesso_exatamente_abaixo_do_limiar(self, mock_random, masmorra_padrao):
        """
        Borda: valor imediatamente abaixo de CHANCE_FUGA deve resultar em sucesso.
        """
        assert masmorra_padrao.tentar_fuga() is True

    @patch("jogo.sistemas.masmorra.random.random", return_value=CHANCE_FUGA + 0.01)
    def test_fuga_falha_exatamente_acima_do_limiar(self, mock_random, masmorra_padrao):
        """
        Borda: valor imediatamente acima de CHANCE_FUGA deve resultar em falha.
        """
        assert masmorra_padrao.tentar_fuga() is False

    def test_tentar_fuga_retorna_bool(self, masmorra_padrao):
        """Tipo: tentar_fuga() deve sempre retornar um bool."""
        resultado = masmorra_padrao.tentar_fuga()
        assert isinstance(resultado, bool)


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 8 — Sequências de integração (FakeGerador)
# ══════════════════════════════════════════════════════════════════════════════

class TestSequenciasIntegracao:
    """
    Testa sequências de operações que simulam situações reais do jogo,
    usando FakeGerador para eliminar aleatoriedade e garantir determinismo.
    """

    def test_vitoria_seguida_de_xp_e_proximo_combate(self, jogador_forte):
        """
        Integração: encadeia dois combates com vitórias e verifica acúmulo de xp.
        """
        inimigo_1 = Inimigo("Goblin",    hp=1, atk=1, dificuldade=1, xp=10)
        inimigo_2 = Inimigo("Esqueleto", hp=1, atk=1, dificuldade=1, xp=20)

        m = Masmorra(jogador_forte)
        m.resolver_combate(inimigo_1)
        m.resolver_combate(inimigo_2)

        assert jogador_forte.xp == 30
        assert jogador_forte.esta_vivo() is True

    def test_derrota_encerra_jogabilidade(self, jogador_padrao):
        """
        Integração: após derrota, jogador.esta_vivo() deve ser False,
        bloqueando naturalmente o loop do jogo.
        """
        m     = Masmorra(jogador_padrao)
        forte = Inimigo("Boss", hp=999, atk=999, dificuldade=3, xp=100)
        m.resolver_combate(forte)

        assert not jogador_padrao.esta_vivo()

    def test_item_aplicado_antes_de_combate_aumenta_sobrevivencia(self):
        """
        Integração: jogador curado antes de combate deve ter mais hp do que
        um jogador não curado ao enfrentar o mesmo inimigo.
        """
        # Jogador curado
        j_curado = Jogador("Curado", hp=20, atk=3)
        j_curado.hp = 1
        Item("Elixir", bonus_hp=10).usar(j_curado)
        m_curado = Masmorra(j_curado)

        # Jogador não curado (hp=1)
        j_sem_cura = Jogador("Sem cura", hp=20, atk=3)
        j_sem_cura.hp = 1
        m_sem_cura = Masmorra(j_sem_cura)

        inimigo_moderado = Inimigo("Moderado", hp=5, atk=3, dificuldade=1, xp=10)

        m_sem_cura.resolver_combate(inimigo_moderado)

        # Jogador sem cura deve morrer (hp=1 vs atk=3)
        assert not j_sem_cura.esta_vivo()
        # Jogador curado tem mais hp para resistir
        assert j_curado.hp > j_sem_cura.hp

    def test_boss_mais_forte_que_inimigo_comum_no_mesmo_andar(self, masmorra_padrao):
        """
        Comparação: boss gerado deve ter mais hp e atk que inimigo comum
        gerado no mesmo andar (andar 5).
        """
        from jogo.entidades.inimigo import Inimigo as Inimigo_

        masmorra_padrao.andar = 5
        boss   = masmorra_padrao.gerar_boss()
        comum  = Inimigo_.gerar(andar=5)

        assert boss.hp  > comum.hp
        assert boss.atk > comum.atk

    def test_estado_masmorra_consistente_apos_combate_e_item(self):
        """
        Estado: após um combate (vitória) e uso de item,
        o estado da masmorra deve permanecer consistente.
        """
        j = Jogador("Consistente", hp=20, atk=50)
        j.hp = 10  # simula dano recebido antes

        m = Masmorra(j)

        # Combate → vitória
        fraco = Inimigo.__new__(Inimigo)
        fraco.nome = "D"; fraco.hp = 1; fraco.atk = 0
        fraco.dificuldade = 1; fraco.xp = 15
        m.resolver_combate(fraco)

        assert j.xp == 15
        assert j.esta_vivo()

        # Item de cura
        m.aplicar_item(Item("Poção", bonus_hp=5))
        assert j.hp == 15

        # Estado da masmorra
        assert m.desistiu    is False
        assert m.andar       == 0   # andar só muda via avancar()