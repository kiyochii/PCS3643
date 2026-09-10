import unittest
from cinema import Filme, cadastrar_filme, filmes

class TestModelo(unittest.TestCase):

#    def setUp(self):

    def test_hello(self):
        self.assertEqual('hello','hello')

    def test_cadastrar_filme(self):
        codigo_esperado = len(filmes) + 1

        filme = cadastrar_filme("Teste", "2002/09/13", "2005/10/21", 60)

        self.assertIsInstance(filme, Filme)
        self.assertEqual(filme.codigo, codigo_esperado)
        self.assertEqual(filme.nome, "Teste")
        self.assertEqual(filme.data_estreia, "2002/09/13")
        self.assertEqual(filme.data_saida, "2005/10/21")
        self.assertEqual(filme.duracao, 60)

#    def tearDown(self):


if __name__ == '__main__':
    unittest.main()
