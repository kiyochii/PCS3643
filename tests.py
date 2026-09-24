import unittest

from cinema import (
    Filme,
    Sala,
    Sessao,
    comprarIngressos,
    cadastrar_filme,
    cadastrar_sala,
    cadastrar_sessao,
    cadastrar_valor_ingresso,
    filmes,
    listar_filmes_por_data,
    removerIngressos,
    salas,
    sessoes,
    tipo_sala,
)


class TestUS02CadastrarValorIngresso(unittest.TestCase):

    def setUp(self):
        tipo_sala.clear()

    def test_cadastrar_valido(self):
        self.assertTrue(cadastrar_valor_ingresso("2D", 30))
        self.assertEqual(tipo_sala["2D"], 30)

        self.assertTrue(cadastrar_valor_ingresso("3D", 50))
        self.assertEqual(tipo_sala["3D"], 50)

    def test_nao_cadastra_valor_zero_ou_negativo(self):
        for valor in (0, -10):
            with self.subTest(valor=valor):
                self.assertFalse(cadastrar_valor_ingresso("2D", valor))
                self.assertNotIn("2D", tipo_sala)
                tipo_sala.clear()

    def test_nao_cadastra_tipo_invalido(self):
        self.assertFalse(cadastrar_valor_ingresso("4D", 30))
        self.assertFalse(cadastrar_valor_ingresso("", 30))
        self.assertNotIn("4D", tipo_sala)
        self.assertNotIn("", tipo_sala)


class TestUS03CadastrarSala(unittest.TestCase):

    def setUp(self):
        salas.clear()

    def test_cadastra_sala_valida(self):
        sala = cadastrar_sala(1, 100, "2D")

        self.assertIsInstance(sala, Sala)
        self.assertEqual(sala.numero, 1)
        self.assertEqual(sala.capacidade, 100)
        self.assertEqual(sala.tipo, "2D")
        self.assertIn(sala, salas)

    def test_rejeita_numero_zero_ou_negativo(self):
        for numero in (0, -1):
            with self.subTest(numero=numero):
                self.assertIsNone(cadastrar_sala(numero, 100, "2D"))
        self.assertEqual(salas, [])

    def test_rejeita_capacidade_zero_ou_negativa(self):
        for capacidade in (0, -1):
            with self.subTest(capacidade=capacidade):
                self.assertIsNone(cadastrar_sala(1, capacidade, "2D"))
        self.assertEqual(salas, [])

    def test_rejeita_tipo_de_sala_invalido(self):
        self.assertIsNone(cadastrar_sala(1, 100, "4D"))
        self.assertEqual(salas, [])

    def test_rejeita_numero_de_sala_repetido(self):
        primeira = cadastrar_sala(1, 100, "2D")
        segunda = cadastrar_sala(1, 200, "3D")

        self.assertIsNotNone(primeira)
        self.assertIsNone(segunda)
        self.assertEqual(len(salas), 1)
        self.assertEqual(salas[0].capacidade, 100)

    def test_permite_mesmo_tipo_em_numeros_diferentes(self):
        primeira = cadastrar_sala(1, 100, "2D")
        segunda = cadastrar_sala(2, 80, "2D")

        self.assertIsNotNone(primeira)
        self.assertIsNotNone(segunda)
        self.assertEqual(len(salas), 2)


class TestUS04CadastrarSessao(unittest.TestCase):

    def setUp(self):
        filmes.clear()
        salas.clear()
        sessoes.clear()

        self.sala = cadastrar_sala(1, 10, "2D")
        self.filme = cadastrar_filme("Filme A", "01/01/2024", "31/01/2024", 120)

    def test_cadastra_sessao_valida(self):
        sessao = cadastrar_sessao(1, 1, "10-03-2024", 18)

        self.assertIsInstance(sessao, Sessao)
        self.assertEqual(sessao.sala.numero, 1)
        self.assertEqual(sessao.filme.codigo, 1)
        self.assertEqual(sessao.data, "10-03-2024")
        self.assertEqual(sessao.hora_inicio, 18)
        self.assertEqual(sessao.codigo, 1)
        self.assertIn(sessao, sessoes)
        self.assertEqual(len(sessao.assentos), self.sala.capacidade)
        self.assertTrue(all(valor == 0 for valor in sessao.assentos.values()))

    def test_rejeita_parametros_invalidos(self):
        casos_invalidos = [
            ("1", 1, "10/03/2024", 18),
            (1, "1", "10/03/2024", 18),
            (1, 1, 20240310, 18),
            (1, 1, "10/03/2024", -1),
            (1, 1, "10/03/2024", 25),
            (99, 1, "10/03/2024", 18),
            (1, 99, "10/03/2024", 18),
        ]

        for caso in casos_invalidos:
            with self.subTest(caso=caso):
                self.assertIsNone(cadastrar_sessao(*caso))

    def test_rejeita_sessao_repetida_na_mesma_sala_data_e_hora(self):
        primeira = cadastrar_sessao(1, 1, "10/03/2024", 18)
        segunda = cadastrar_sessao(1, 1, "10/03/2024", 18)

        self.assertIsNotNone(primeira)
        self.assertIsNone(segunda)
        self.assertEqual(len(sessoes), 1)


class TestUS05ListarFilmesPorData(unittest.TestCase):

    def setUp(self):
        filmes.clear()
        salas.clear()
        sessoes.clear()
        tipo_sala.clear()

        tipo_sala["2D"] = 40
        tipo_sala["3D"] = 50

        self.king_kong = Filme(1, "King Kong", "01/01/2026", "31/12/2026", 120)
        self.star_wars = Filme(2, "Star Wars", "01/01/2026", "31/12/2026", 130)
        filmes.extend([self.king_kong, self.star_wars])

        self.sala_3d = cadastrar_sala(1, 3, "3D")
        self.sala_2d = cadastrar_sala(2, 3, "2D")

    def _nova_sessao(self, codigo, sala, filme, data, hora, ocupados=()):
        sessao = Sessao(sala, filme, data, hora)
        sessao.codigo = codigo
        sessao.assentos = {
            numero: (1 if numero in ocupados else 0)
            for numero in range(1, sala.capacidade + 1)
        }
        sessoes.append(sessao)
        return sessao

    def test_retorna_data_invalida_para_formato_incorreto(self):
        for data in ("2026-09-12", "12/09", ""):
            with self.subTest(data=data):
                self.assertEqual(listar_filmes_por_data(data), "Data invalida.")

        self.assertEqual(listar_filmes_por_data("12-09-2026"), "Nenhum filme no dia escolhido.")

    def test_retorna_data_invalida_para_data_inexistente(self):
        self.assertEqual(listar_filmes_por_data("31/02/2026"), "Data invalida.")

    def test_retorna_mensagem_sem_sessoes(self):
        self.assertEqual(
            listar_filmes_por_data("12/09/2026"),
            "Nenhum filme no dia escolhido.",
        )

    def test_lista_sessao_com_assento_livre(self):
        self._nova_sessao(1, self.sala_3d, self.king_kong, "12/09/2026", 12, ocupados=(2,))

        resultado = listar_filmes_por_data("12/09/2026")

        for trecho in ("1:", "King Kong", "sala 1", "(3D)", "12h", "50 reais."):
            self.assertIn(trecho, resultado)

    def test_nao_lista_sessao_com_todos_assentos_ocupados(self):
        self._nova_sessao(
            1, self.sala_3d, self.king_kong, "12/09/2026", 12, ocupados=(1, 2, 3)
        )

        self.assertEqual(
            listar_filmes_por_data("12/09/2026"),
            "Nenhum filme no dia escolhido.",
        )

    def test_lista_varias_sessoes_do_mesmo_filme(self):
        self._nova_sessao(1, self.sala_3d, self.king_kong, "12/09/2026", 12)
        self._nova_sessao(2, self.sala_3d, self.king_kong, "12/09/2026", 20)

        resultado = listar_filmes_por_data("12/09/2026")

        self.assertEqual(len(resultado.split("\n")), 2)
        self.assertIn("1: King Kong", resultado)
        self.assertIn("2: King Kong", resultado)

    def test_nao_lista_sessoes_de_outra_data(self):
        self._nova_sessao(1, self.sala_3d, self.king_kong, "13/09/2026", 12)

        self.assertEqual(
            listar_filmes_por_data("12/09/2026"),
            "Nenhum filme no dia escolhido.",
        )

    def test_formata_linha_exatamente(self):
        self._nova_sessao(1, self.sala_3d, self.king_kong, "12/09/2026", 12)

        self.assertEqual(
            listar_filmes_por_data("12/09/2026"),
            "1: King Kong, sala 1 (3D), 12h, 50 reais.",
        )

    def test_lista_sessoes_em_ordem_de_codigo(self):
        self._nova_sessao(2, self.sala_2d, self.star_wars, "12/09/2026", 13)
        self._nova_sessao(1, self.sala_3d, self.king_kong, "12/09/2026", 12)

        resultado = listar_filmes_por_data("12/09/2026")

        self.assertEqual(
            resultado,
            "1: King Kong, sala 1 (3D), 12h, 50 reais.\n"
            "2: Star Wars, sala 2 (2D), 13h, 40 reais.",
        )

    def test_usa_preco_de_acordo_com_tipo_da_sala(self):
        self._nova_sessao(1, self.sala_3d, self.king_kong, "12/09/2026", 12)
        self._nova_sessao(2, self.sala_2d, self.star_wars, "12/09/2026", 13)

        linhas = listar_filmes_por_data("12/09/2026").split("\n")

        self.assertTrue(linhas[0].endswith("50 reais."))
        self.assertTrue(linhas[1].endswith("40 reais."))


class TestUS06ComprarIngressos(unittest.TestCase):

    def setUp(self):
        filmes.clear()
        salas.clear()
        sessoes.clear()
        tipo_sala.clear()

        tipo_sala["2D"] = 40
        self.filme = cadastrar_filme("Filme A", "01/01/2026", "31/12/2026", 120)
        self.sala = cadastrar_sala(1, 5, "2D")
        self.sessao = cadastrar_sessao(self.sala.numero, self.filme.codigo, "10/09/2026", 14)

    def test_compra_ingresso_inteiro(self):
        valor = comprarIngressos(self.sessao.codigo, [1], [0])

        self.assertEqual(valor, 40)
        self.assertEqual(self.sessao.assentos[1], 1)

    def test_compra_ingresso_meia(self):
        valor = comprarIngressos(self.sessao.codigo, [2], [1])

        self.assertEqual(valor, 20)
        self.assertEqual(self.sessao.assentos[2], 1)

    def test_compra_varios_ingressos(self):
        valor = comprarIngressos(self.sessao.codigo, [1, 2, 3], [0, 1, 0])

        self.assertEqual(valor, 100)
        self.assertEqual(self.sessao.assentos[1], 1)
        self.assertEqual(self.sessao.assentos[2], 1)
        self.assertEqual(self.sessao.assentos[3], 1)

    def test_assento_e_tipo_sao_associados_pela_mesma_posicao(self):
        valor = comprarIngressos(self.sessao.codigo, [2, 4], [0, 1])

        self.assertEqual(valor, 60)
        self.assertEqual(self.sessao.assentos[2], 1)
        self.assertEqual(self.sessao.assentos[4], 1)

    def test_rejeita_sessao_inexistente(self):
        self.assertEqual(comprarIngressos(999, [1], [0]), 0)

    def test_rejeita_lista_de_assentos_vazia(self):
        self.assertEqual(comprarIngressos(self.sessao.codigo, [], []), 0)

    def test_rejeita_listas_de_tamanhos_diferentes(self):
        estado_antes = self.sessao.assentos.copy()
        valor = comprarIngressos(self.sessao.codigo, [1, 2], [0])

        self.assertEqual(valor, 0)
        self.assertEqual(self.sessao.assentos, estado_antes)

    def test_rejeita_assento_zero(self):
        estado_antes = self.sessao.assentos.copy()
        valor = comprarIngressos(self.sessao.codigo, [0], [0])

        self.assertEqual(valor, 0)
        self.assertEqual(self.sessao.assentos, estado_antes)

    def test_rejeita_assento_acima_da_capacidade(self):
        estado_antes = self.sessao.assentos.copy()
        valor = comprarIngressos(self.sessao.codigo, [6], [0])

        self.assertEqual(valor, 0)
        self.assertEqual(self.sessao.assentos, estado_antes)

    def test_rejeita_assento_ja_ocupado(self):
        self.sessao.assentos[2] = 1
        estado_antes = self.sessao.assentos.copy()

        valor = comprarIngressos(self.sessao.codigo, [2], [0])

        self.assertEqual(valor, 0)
        self.assertEqual(self.sessao.assentos, estado_antes)

    def test_rejeita_tipo_de_ingresso_invalido(self):
        estado_antes = self.sessao.assentos.copy()
        valor = comprarIngressos(self.sessao.codigo, [1], [2])

        self.assertEqual(valor, 0)
        self.assertEqual(self.sessao.assentos, estado_antes)

    def test_rejeita_assento_repetido(self):
        estado_antes = self.sessao.assentos.copy()
        valor = comprarIngressos(self.sessao.codigo, [2, 2], [0, 1])

        self.assertEqual(valor, 0)
        self.assertEqual(self.sessao.assentos, estado_antes)

    def test_compra_e_atomica(self):
        self.sessao.assentos[2] = 1
        estado_antes = self.sessao.assentos.copy()

        valor = comprarIngressos(self.sessao.codigo, [1, 2], [0, 0])

        self.assertEqual(valor, 0)
        self.assertEqual(self.sessao.assentos, estado_antes)

    def test_nao_altera_assentos_em_compra_invalida(self):
        self.sessao.assentos[2] = 1
        estado_antes = self.sessao.assentos.copy()

        valor = comprarIngressos(self.sessao.codigo, [1, 2], [0, 0])

        self.assertEqual(valor, 0)
        self.assertEqual(self.sessao.assentos, estado_antes)

    def test_remove_ingressos_comprados(self):
        comprarIngressos(self.sessao.codigo, [1, 2], [0, 1])

        valor = removerIngressos(self.sessao.codigo, [1])

        self.assertEqual(valor, 1)
        self.assertEqual(self.sessao.assentos[1], 0)
        self.assertEqual(self.sessao.assentos[2], 1)


if __name__ == "__main__":
    unittest.main()

