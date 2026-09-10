import unittest
from cinema import Filme, Sala, cadastrar_filme, filmes, salas

from cinema import cadastrar_valor_ingresso, tipo_sala
from cinema import cadastrar_sala


class TestModelo(unittest.TestCase):

    def setUp(self):
        tipo_sala.clear()

    def test_cadastrar_valido(self):
        self.assertTrue(cadastrar_valor_ingresso({"tipo": "2D"}, 30))
        self.assertEqual(tipo_sala["2D"], 30)

        self.assertTrue(cadastrar_valor_ingresso({"tipo": "3D"}, 50))
        self.assertEqual(tipo_sala["3D"], 50)
        
    def test_cadastrar_filme(self):
        codigo_esperado = len(filmes) + 1

        filme = cadastrar_filme("Teste", "2002/09/13", "2005/10/21", 60)

        self.assertIsInstance(filme, Filme)
        self.assertEqual(filme.codigo, codigo_esperado)
        self.assertEqual(filme.nome, "Teste")
        self.assertEqual(filme.data_estreia, "2002/09/13")
        self.assertEqual(filme.data_saida, "2005/10/21")
        self.assertEqual(filme.duracao, 60)

    def test_nao_cadastra_valor_zero_ou_negativo(self):
        for valor in (0, -10):
            with self.subTest(valor=valor):
                payload = {"tipo": "2D"}
                self.assertFalse(cadastrar_valor_ingresso(payload, valor))
                self.assertNotIn("2D", tipo_sala)
                tipo_sala.clear()

    def test_nao_cadastra_tipo_invalido(self):
        self.assertFalse(cadastrar_valor_ingresso({"tipo": "4D"}, 30))
        self.assertFalse(cadastrar_valor_ingresso({"tipo": ""}, 30))
        self.assertFalse(cadastrar_valor_ingresso({}, 30))
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
        


if __name__ == '__main__':
    unittest.main()
