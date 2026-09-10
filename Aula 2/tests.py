import unittest
from cinema import Filme, cadastrar_filme, filmes

from cinema import cadastrar_valor_ingresso, tipo_sala


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


if __name__ == '__main__':
    unittest.main()
