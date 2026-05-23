# randongeon/tests/test_inimigo.py — ALTERAÇÕES NECESSÁRIAS
#
# Este arquivo lista APENAS os testes que precisam de alteração.
# Copie cada bloco substituindo o correspondente no test_inimigo.py original.
# O restante do arquivo permanece exatamente igual.
# ─────────────────────────────────────────────────────────────────────────────
#
# RESUMO DAS MUDANÇAS (por que quebraram):
#   1. Elite (dif 2) agora exige andar >= 5 (era >= 3).
#      → Testes com andar=3 para dif 2 precisam usar andar=5.
#   2. Moedas dif 2 agora são 5-10 (eram 6-11).
#      → Assert de range precisa ser atualizado.
#   3. Novos atributos no Inimigo (hp_max, tipo_especial, etc.):
#      → Testes de criação precisam verificar hp_max.


# ── BLOCO: TestGerar — substituir os métodos abaixo ──────────────────────────

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    @patch("jogo.entidades.inimigo.random.choice", return_value="Goblin")
    @patch("jogo.entidades.inimigo.random.randint", side_effect=[5, 2, 15, 3])
    def test_mock_gera_inimigo_dificuldade_1(self, mock_randint, mock_choice, mock_random):
        """
        Mock completo: random.random=0.9 → sem horda (0.9 > 0.10) e sem elite
        (0.9 > 0.25). andar=3 < 5, portanto dificuldade 1.
        side_effect cobre: hp=5, atk=2, xp=15, moedas=3 (4 sorteios).
        Não há mudança neste teste — continua funcionando.
        """
        inimigo = Inimigo.gerar(andar=3)
        assert inimigo.dificuldade == 1
        assert inimigo.nome        == "Goblin"
        assert inimigo.hp          == 5
        assert inimigo.atk         == 2
        assert inimigo.xp          == 15
        assert inimigo.moedas      == 3

    @patch("jogo.entidades.inimigo.random.random", return_value=0.11)
    @patch("jogo.entidades.inimigo.random.choice", return_value="Orc")
    @patch("jogo.entidades.inimigo.random.randint", side_effect=[12, 4, 40, 8])
    def test_mock_gera_inimigo_dificuldade_2(self, mock_randint, mock_choice, mock_random):
        """
        ALTERADO: andar=3 → andar=5 (elite agora exige >= 5).
        random=0.11: horda (< 0.10? Não). Elite (>= 5 E 0.11 < 0.25? Sim).
        Sem especiais disponíveis em andar=5 (primeiro especial é andar 8).
        side_effect cobre: hp=12, atk=4, xp=40, moedas=8.
        """
        inimigo = Inimigo.gerar(andar=5)           # era andar=3
        assert inimigo.dificuldade == 2
        assert inimigo.nome        == "Orc"
        assert inimigo.hp          == 12
        assert inimigo.atk         == 4
        assert inimigo.xp          == 40
        assert inimigo.moedas      == 8

    @patch("jogo.entidades.inimigo.random.random", return_value=0.11)
    def test_elite_nao_aparece_antes_do_andar_5(self, mock_random):
        """
        RENOMEADO: era test_elite_nao_aparece_antes_do_andar_3.
        ALTERADO: threshold subiu para andar 5.
        random=0.11: horda? (0.11 < 0.10? Não). Elite? (andar=4 >= 5? Não).
        Portanto sempre dificuldade 1 antes do andar 5.
        """
        inimigo = Inimigo.gerar(andar=4)           # era andar=2
        assert inimigo.dificuldade == 1

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    def test_dificuldade_1_sem_elite_no_andar_1(self, mock_random):
        """Sem alteração — continua funcionando."""
        assert Inimigo.gerar(andar=1).dificuldade == 1

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    def test_inimigo_dif1_nome_pertence_ao_pool_correto(self, mock_random):
        """Sem alteração — continua funcionando."""
        assert Inimigo.gerar(andar=1).nome in NOMES_DIFICULDADE_1

    @patch("jogo.entidades.inimigo.random.random", return_value=0.11)
    def test_inimigo_dif2_nome_pertence_ao_pool_correto(self, mock_random):
        """
        ALTERADO: andar=3 → andar=5.
        Com random=0.11: sem horda, com elite em andar=5.
        Sem especiais em andar=5, gera elite comum do NOMES_DIFICULDADE_2.
        """
        assert Inimigo.gerar(andar=5).nome in NOMES_DIFICULDADE_2   # era andar=3

    @patch("jogo.entidades.inimigo.random.random", return_value=0.9)
    def test_inimigo_dif1_moedas_dentro_do_range(self, mock_random):
        """
        Sem alteração no assert — range novo é 0-4, mas '0-5' ainda engloba.
        Mas atualizamos para refletir o range real (0-4).
        """
        for _ in range(20):
            i = Inimigo.gerar(andar=1)
            assert 0 <= i.moedas <= 4     # era <= 5; range atual é 0-4

    @patch("jogo.entidades.inimigo.random.random", return_value=0.11)
    def test_inimigo_dif2_moedas_dentro_do_range(self, mock_random):
        """
        ALTERADO: andar=3 → andar=5 e range 6-11 → 5-10.
        """
        for _ in range(20):
            i = Inimigo.gerar(andar=5)    # era andar=3
            assert 5 <= i.moedas <= 10    # era 6 <= ... <= 11


# ── BLOCO: TestEscalonamentoPorAndar — substituir o método abaixo ─────────────

    def test_inimigos_dif2_tem_moedas_maiores_que_dif1_em_media(self):
        """
        ALTERADO: andar=3 → andar=5 para gerar dif 2.
        Médias: dif1 = 0-4 (≈2), dif2 = 5-10 (≈7.5). Dif2 > Dif1. ✓
        """
        with patch("jogo.entidades.inimigo.random.random", return_value=0.9):
            moedas_dif1 = [Inimigo.gerar(andar=1).moedas for _ in range(20)]
        with patch("jogo.entidades.inimigo.random.random", return_value=0.11):
            moedas_dif2 = [Inimigo.gerar(andar=5).moedas for _ in range(20)]   # era andar=3
        assert (sum(moedas_dif2) / 20) > (sum(moedas_dif1) / 20)


# ── BLOCO: TestCriacaoInimigo — adicionar ao final da classe ──────────────────

    def test_hp_max_igual_ao_hp_inicial(self):
        """Novo v3: todo Inimigo criado via __init__ deve ter hp_max == hp inicial."""
        i = Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=15, moedas=5)
        assert i.hp_max == 10

    def test_hp_max_nao_muda_apos_dano(self):
        """Novo v3: hp_max permanece fixo mesmo após receber dano."""
        i = Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=15, moedas=5)
        i.receber_dano(5)
        assert i.hp     == 5
        assert i.hp_max == 10

    def test_curar_restaura_hp_sem_ultrapassar_max(self):
        """Novo v3: curar() restaura HP sem passar do hp_max."""
        vampiro = Inimigo(
            "Vampiro das Sombras", hp=15, atk=5, dificuldade=2,
            xp=40, moedas=10, cura_percentual=0.20
        )
        vampiro.hp = 10
        vampiro.curar(8)
        assert vampiro.hp == 15        # não ultrapassa hp_max

    def test_curar_negativo_levanta_value_error(self):
        """Novo v3: curar() com valor negativo deve lançar ValueError."""
        i = Inimigo("Goblin", hp=10, atk=3, dificuldade=1, xp=10, moedas=2)
        with pytest.raises(ValueError):
            i.curar(-1)

    def test_absorcao_dano_reduz_dano_recebido(self):
        """Novo v3: Golem com absorcao_dano=2 recebe 3 de dano em vez de 5."""
        golem = Inimigo(
            "Golem de Pedra", hp=20, atk=3, dificuldade=2,
            xp=35, moedas=9, absorcao_dano=2
        )
        dano = golem.receber_dano(5)
        assert dano     == 3
        assert golem.hp == 17

    def test_absorcao_maior_que_dano_resulta_zero(self):
        """Novo v3: ataque menor que absorção causa zero dano."""
        golem = Inimigo(
            "Golem de Pedra", hp=20, atk=3, dificuldade=2,
            xp=35, moedas=9, absorcao_dano=2
        )
        dano = golem.receber_dano(1)
        assert dano     == 0
        assert golem.hp == 20

    def test_atributos_especiais_tem_valores_padrao(self):
        """Novo v3: inimigo comum deve ter todos os atributos especiais neutros."""
        i = Inimigo("Goblin", hp=5, atk=2, dificuldade=1, xp=10, moedas=3)
        assert i.modificador_fuga    == 0.0
        assert i.cura_percentual     == 0.0
        assert i.absorcao_dano       == 0
        assert i.bonus_atk_por_turno == 0
        assert i.chance_atordoar     == 0.0
        assert i.tipo_especial       is None

    def test_cura_percentual_invalida_levanta_value_error(self):
        """Novo v3: cura_percentual fora de [0, 1] deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("X", hp=10, atk=2, dificuldade=1, xp=5, moedas=1,
                    cura_percentual=1.5)

    def test_chance_atordoar_invalida_levanta_value_error(self):
        """Novo v3: chance_atordoar fora de [0, 1] deve lançar ValueError."""
        with pytest.raises(ValueError):
            Inimigo("X", hp=10, atk=2, dificuldade=1, xp=5, moedas=1,
                    chance_atordoar=-0.1)