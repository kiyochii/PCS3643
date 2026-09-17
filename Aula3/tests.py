"""Execute: python -m unittest -v tests."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
import database
from cinema import (Filme, Sala, Sessao, cadastrar_filme, cadastrar_sala,
                    cadastrar_sessao, cadastrar_valor_ingresso,
                    listar_filmes, listar_salas, listar_sessoes, listar_precos)
from main import app

FILME = {"nome": "Central do Brasil", "data_estreia": "01/09/2026",
         "data_saida": "30/09/2026", "duracao": 110}
CAMINHOS = ("/precos", "/tipos-ingresso", "/filmes", "/salas", "/sessoes")


class BancoTemporario(unittest.TestCase):
    def setUp(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        banco = patch.object(database, "DB_PATH", Path(pasta.name) / "cinema.db")
        banco.start()
        self.addCleanup(banco.stop)
        database.criar_tabelas()


class CinemaTests(BancoTemporario):
    def setUp(self):
        super().setUp()
        self.client = TestClient(app)
        self.client.__enter__()
        self.addCleanup(lambda: self.client.__exit__(None, None, None))

    def pedir(self, metodo, url, status, dados=None):
        resposta = self.client.request(metodo, url, json=dados)
        self.assertEqual(resposta.status_code, status, resposta.text)
        return resposta

    def preparar(self):
        self.pedir("POST", "/precos", 201, {"tipo_sala": "2D", "valor_ingresso": 30})
        self.pedir("POST", "/tipos-ingresso", 201, {"codigo": 0, "nome": "Inteira", "percentual": 100})
        self.filme = self.pedir("POST", "/filmes", 201, FILME).json()
        self.pedir("POST", "/salas", 201, {"numero": 1, "capacidade": 2, "tipo_sala": "2D"})
        self.sessao = {"numero_sala": 1, "codigo_filme": self.filme["codigo"],
                       "data_sessao": "17/09/2026", "hora_inicio": 15}

    def test_crud_dos_cinco_recursos(self):
        self.preparar()
        self.pedir("POST", "/precos", 201, {"tipo_sala": "2D", "valor_ingresso": 29})
        self.assertEqual(self.pedir("GET", "/precos", 200).json()[0]["valor_ingresso"], 29)
        sala = self.pedir("PUT", "/salas/1", 200, {"capacidade": 3, "tipo_sala": "2D"}).json()
        sessao = self.pedir("POST", "/sessoes", 201, self.sessao).json()
        alteracoes = [
            ("/precos/2D", {"valor_ingresso": 31}),
            ("/tipos-ingresso/0", {"nome": "Promocional", "percentual": 80}),
            (f"/filmes/{self.filme['codigo']}", {**FILME, "nome": "Novo título"}),
            (f"/sessoes/{sessao['codigo']}", {**self.sessao, "hora_inicio": 18}),
        ]
        esperados = {"/salas": sala}
        for url, dados in alteracoes:
            esperados[url.rsplit("/", 1)[0]] = self.pedir("PUT", url, 200, dados).json()
        for caminho, esperado in esperados.items():
            self.assertEqual(self.pedir("GET", caminho, 200).json(), [esperado])
        self.assertEqual((esperados["/precos"]["valor_ingresso"], esperados["/tipos-ingresso"]["percentual"]), (31, 80))
        self.assertEqual((esperados["/filmes"]["nome"], esperados["/sessoes"]["hora_inicio"]), ("Novo título", 18))
        self.assertEqual(esperados["/sessoes"]["assentos"], {"1": 0, "2": 0, "3": 0})
        self.assertEqual(esperados["/sessoes"]["filme"], esperados["/filmes"])
        ordem = [f"/sessoes/{sessao['codigo']}", "/salas/1",
                 f"/filmes/{self.filme['codigo']}", "/tipos-ingresso/0", "/precos/2D"]
        for url in ordem:
            self.assertEqual(self.pedir("DELETE", url, 204).content, b"")
        for caminho in CAMINHOS:
            self.assertEqual(self.pedir("GET", caminho, 200).json(), [])

    def test_validacao_e_protecao_das_referencias(self):
        self.preparar()
        for campo, valor in (("nome", "  "), ("duracao", True), ("data_estreia", "31/02/2026"),
                             ("data_saida", "31/08/2026")):
            self.pedir("POST", "/filmes", 422, {**FILME, campo: valor})
        self.assertEqual(self.pedir("GET", "/filmes", 200).json(), [self.filme])
        self.pedir("POST", "/sessoes", 400, {**self.sessao, "numero_sala": 999})
        self.pedir("POST", "/sessoes", 201, self.sessao)
        self.pedir("POST", "/sessoes", 400, self.sessao)
        for url in ("/salas/1", f"/filmes/{self.filme['codigo']}"):
            self.pedir("DELETE", url, 409)
        self.pedir("POST", "/salas", 400, {"numero": 1, "capacidade": 2, "tipo_sala": "2D"})
        self.pedir("DELETE", "/precos/2D", 204)
        self.pedir("PUT", "/salas/1", 409, {"capacidade": 5, "tipo_sala": "2D"})
        self.assertEqual(self.pedir("GET", "/sessoes", 200).json()[0]["assentos"], {"1": 0, "2": 0})

    def test_dados_persistem_apos_reiniciar(self):
        self.preparar()
        self.pedir("POST", "/sessoes", 201, self.sessao)
        antes = {caminho: self.pedir("GET", caminho, 200).json() for caminho in CAMINHOS}
        self.client.__exit__(None, None, None)
        self.client = TestClient(app)
        self.client.__enter__()
        for caminho in CAMINHOS:
            self.assertEqual(self.pedir("GET", caminho, 200).json(), antes[caminho])

    def test_paginas_e_recurso_inexistente(self):
        self.assertIn("Cinema", self.pedir("GET", "/", 200).text)
        self.assertIn("/docs", self.pedir("GET", "/", 200).text)
        self.pedir("GET", "/docs", 200)
        self.pedir("PUT", "/filmes/999", 404, FILME)
        self.pedir("DELETE", "/filmes/999", 404)
        for caminho in CAMINHOS:
            self.assertEqual(self.pedir("GET", caminho, 200).json(), [])


def precos():
    return {item["tipo_sala"]: item["valor_ingresso"] for item in listar_precos()}


# Casos da Aula 2, com o banco temporário substituindo as listas globais.
class TestModelo(BancoTemporario):

    def test_cadastrar_valido(self):
        self.assertTrue(cadastrar_valor_ingresso({"tipo": "2D"}, 30))
        self.assertEqual(precos()["2D"], 30)

        self.assertTrue(cadastrar_valor_ingresso({"tipo": "3D"}, 50))
        self.assertEqual(precos()["3D"], 50)
        self.assertTrue(cadastrar_valor_ingresso({"tipo": "2D"}, 31))
        self.assertEqual(precos()["2D"], 31)

    def test_cadastrar_filme(self):
        codigo_esperado = len(listar_filmes()) + 1

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
                self.assertNotIn("2D", precos())

    def test_nao_cadastra_tipo_invalido(self):
        self.assertFalse(cadastrar_valor_ingresso({"tipo": "4D"}, 30))
        self.assertFalse(cadastrar_valor_ingresso({"tipo": ""}, 30))
        self.assertFalse(cadastrar_valor_ingresso({}, 30))
        self.assertNotIn("4D", precos())
        self.assertNotIn("", precos())


class TestUS03CadastrarSala(BancoTemporario):

    def test_cadastra_sala_valida(self):
        sala = cadastrar_sala(1, 100, "2D")

        self.assertIsInstance(sala, Sala)
        self.assertEqual(sala.numero, 1)
        self.assertEqual(sala.capacidade, 100)
        self.assertEqual(sala.tipo, "2D")
        self.assertIn(vars(sala), [vars(item) for item in listar_salas()])
        self.assertEqual(cadastrar_sala(2, 10001, "3D").capacidade, 10001)

    def test_rejeita_numero_zero_ou_negativo(self):
        for numero in (0, -1):
            with self.subTest(numero=numero):
                self.assertIsNone(cadastrar_sala(numero, 100, "2D"))
        self.assertEqual(listar_salas(), [])

    def test_rejeita_capacidade_zero_ou_negativa(self):
        for capacidade in (0, -1):
            with self.subTest(capacidade=capacidade):
                self.assertIsNone(cadastrar_sala(1, capacidade, "2D"))
        self.assertEqual(listar_salas(), [])

    def test_rejeita_tipo_de_sala_invalido(self):
        self.assertIsNone(cadastrar_sala(1, 100, "4D"))
        self.assertEqual(listar_salas(), [])

    def test_rejeita_numero_de_sala_repetido(self):
        primeira = cadastrar_sala(1, 100, "2D")
        segunda = cadastrar_sala(1, 200, "3D")

        self.assertIsNotNone(primeira)
        self.assertIsNone(segunda)
        self.assertEqual(len(listar_salas()), 1)
        self.assertEqual(listar_salas()[0].capacidade, 100)

    def test_permite_mesmo_tipo_em_numeros_diferentes(self):
        primeira = cadastrar_sala(1, 100, "2D")
        segunda = cadastrar_sala(2, 80, "2D")

        self.assertIsNotNone(primeira)
        self.assertIsNotNone(segunda)
        self.assertEqual(len(listar_salas()), 2)


class TestContratoOriginal(BancoTemporario):
    def test_construtores_sem_argumentos(self):
        for objeto, campos in (
            (Filme(), ("codigo", "nome", "data_estreia", "data_saida", "duracao")),
            (Sala(), ("numero", "capacidade", "tipo")),
            (Sessao(), ("sala", "filme", "data", "hora_inicio")),
        ):
            for campo in campos:
                with self.subTest(classe=type(objeto).__name__, campo=campo):
                    self.assertIsNone(getattr(objeto, campo))

    def test_cadastrar_sessao_retorna_objeto_ou_none(self):
        cadastrar_sala(1, 2, "2D")
        filme = cadastrar_filme("Teste", "2002/09/13", "2005/10/21", 60)
        sessao = cadastrar_sessao(1, filme.codigo, "2002/09/13", 15)
        self.assertIsInstance(sessao, Sessao)
        self.assertEqual((sessao.codigo, sessao.sala.numero, sessao.filme.codigo), (1, 1, filme.codigo))
        self.assertEqual((sessao.data, sessao.hora_inicio), ("2002/09/13", 15))
        self.assertEqual(sessao.assentos, {1: 0, 2: 0})
        for sala, codigo, data, hora in (
            (1, filme.codigo, "2002/09/13", 15),
            (999, filme.codigo, "2002/09/13", 16),
            (1, 999, "2002/09/13", 16),
            (True, filme.codigo, "2002/09/13", 16),
            (1, filme.codigo, None, 16),
            (1, filme.codigo, "2002/09/13", -1),
            (1, filme.codigo, "2002/09/13", 24),
        ):
            with self.subTest(sala=sala, codigo=codigo, data=data, hora=hora):
                self.assertIsNone(cadastrar_sessao(sala, codigo, data, hora))
        self.assertEqual(len(listar_sessoes()), 1)


if __name__ == "__main__":
    unittest.main()
