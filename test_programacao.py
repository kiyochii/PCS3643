"""Contrato REST da tela e compatibilidade dos cartazes no SQLite."""
import json
from contextlib import closing
from io import BytesIO
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

import cinema
import controller
import database
from main import app


class TestProgramacao(unittest.TestCase):
    def setUp(self):
        self.previous = (cinema.filmes[:], cinema.salas[:], cinema.sessoes[:], cinema.tipo_sala.copy())
        for collection in (cinema.filmes, cinema.salas, cinema.sessoes, cinema.tipo_sala):
            collection.clear()
        self.temp = tempfile.TemporaryDirectory()
        self.patch = patch.object(database, 'DB_PATH', Path(self.temp.name) / 'cinema.db')
        self.patch.start()
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.patch.stop()
        self.temp.cleanup()
        cinema.filmes[:], cinema.salas[:], cinema.sessoes[:] = self.previous[:3]
        cinema.tipo_sala.clear()
        cinema.tipo_sala.update(self.previous[3])

    def test_tela_e_recursos(self):
        self.assertIn('Programação do cinema', self.client.get('/').text)
        for path in ('/static/app.js', '/static/style.css', '/cinema/filmes',
                     '/cinema/sessoes', '/cinema/salas', '/cinema/valor-ingresso'):
            self.assertEqual(self.client.get(path).status_code, 200)
        types = self.client.get('/cinema/tipos-ingresso').json()['tipos_ingresso']
        self.assertEqual([(t['codigo'], t['fator']) for t in types], [(0, 1), (1, 0.5)])

    def test_painel_administrativo_e_recursos(self):
        response = self.client.get('/admin')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Painel administrativo', response.text)
        for form_id in ('price-form', 'room-form', 'movie-form', 'session-form', 'ticket-form'):
            self.assertIn(f'id="{form_id}"', response.text)
        for path in ('/static/admin.js', '/static/admin.css'):
            self.assertEqual(self.client.get(path).status_code, 200)

    def test_cartaz_persistido_e_sessao(self):
        payload = dict(nome='Filme teste', data_estreia='01-09-2026',
                       data_saida='30-09-2026', duracao=120,
                       cartaz_url='https://example.com/poster.jpg')
        response = self.client.post('/cinema/filmes', json=payload)
        self.assertEqual(response.status_code, 200)
        code = response.json()['filme']['codigo']
        self.client.post('/cinema/salas', json=dict(numero=1, capacidade=10, tipo_sala='2D'))
        response = self.client.post('/cinema/sessoes', json=dict(numero_sala=1,
            codigo_filme=code, data_sessao='24-09-2026', hora_inicio=18))
        self.assertEqual(response.status_code, 200)
        payload['cartaz_url'] = 'https://example.com/updated.jpg'
        self.assertEqual(self.client.put(f'/cinema/filmes/update/{code}', json=payload).status_code, 200)
        database.load_state()
        film = self.client.get('/cinema/filmes').json()['filmes'][0]
        session = self.client.get('/cinema/sessoes').json()['sessoes'][0]
        self.assertEqual(film['cartaz_url'], payload['cartaz_url'])
        self.assertEqual(session['filme']['cartaz_url'], payload['cartaz_url'])
        payload['cartaz_url'] = 'javascript:alert(1)'
        self.assertEqual(self.client.put(f'/cinema/filmes/update/{code}', json=payload).status_code, 422)

    def test_banco_antigo_sem_cartaz(self):
        old = dict(filmes=[dict(codigo=1, nome='Antigo', data_estreia='01-09-2026',
                   data_saida='30-09-2026', duracao=90)], salas=[], sessoes=[], tipo_sala={})
        with closing(sqlite3.connect(database.DB_PATH)) as connection, connection:
            connection.execute('DROP TABLE cartazes')
            connection.execute('INSERT INTO app_state VALUES (?, ?)', ('cinema_state', json.dumps(old)))
        database.init_db()
        self.assertTrue(database.load_state())
        self.assertIsNone(self.client.get('/cinema/filmes').json()['filmes'][0]['cartaz_url'])

    def criar_filme(self):
        payload = dict(nome='Filme com upload', data_estreia='01-09-2026',
                       data_saida='30-09-2026', duracao=120)
        response = self.client.post('/cinema/filmes', json=payload)
        self.assertEqual(response.status_code, 200)
        return response.json()['filme']

    def test_erro_no_banco_nao_apaga_dados(self):
        broken_path = Path(self.temp.name) / 'banco-invalido.db'
        original = b'conteudo que deve ser preservado para recuperacao'
        broken_path.write_bytes(original)
        with patch.object(database, 'DB_PATH', broken_path):
            for operation in (database.init_db, database.load_state):
                with self.subTest(operation=operation.__name__):
                    with self.assertRaises(sqlite3.DatabaseError):
                        operation()
                    self.assertEqual(broken_path.read_bytes(), original)

    def imagem(self, formato='PNG', cor='red'):
        buffer = BytesIO()
        Image.new('RGB', (8, 12), cor).save(buffer, format=formato)
        return buffer.getvalue()

    def enviar_cartaz(self, code, conteudo, tipo='image/png'):
        return self.client.post(f'/cinema/filmes/{code}/cartaz',
                                files={'arquivo': ('cartaz.png', conteudo, tipo)})

    def test_upload_sobrevive_reinicio_e_aparece_na_sessao(self):
        film = self.criar_filme()
        self.client.post('/cinema/salas', json=dict(numero=1, capacidade=10, tipo_sala='2D'))
        self.client.post('/cinema/sessoes', json=dict(numero_sala=1,
            codigo_filme=film['codigo'], data_sessao='24-09-2026', hora_inicio=18))
        image = self.imagem()
        response = self.enviar_cartaz(film['codigo'], image)
        self.assertEqual(response.status_code, 200)
        url = response.json()['filme']['cartaz_url']
        self.client.__exit__(None, None, None)
        for collection in (cinema.filmes, cinema.salas, cinema.sessoes, cinema.tipo_sala):
            collection.clear()
        self.client = TestClient(app)
        self.client.__enter__()
        restored = self.client.get('/cinema/filmes').json()['filmes'][0]
        session = self.client.get('/cinema/sessoes').json()['sessoes'][0]
        self.assertEqual(restored['cartaz_url'], url)
        self.assertEqual(session['filme']['cartaz_url'], url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, image)
        self.assertEqual(response.headers['content-type'], 'image/png')
        self.assertEqual(response.headers['x-content-type-options'], 'nosniff')

    def test_formatos_sao_detectados_pelo_conteudo(self):
        film = self.criar_filme()
        for formato, tipo in [('PNG', 'image/png'), ('JPEG', 'image/jpeg'), ('WEBP', 'image/webp')]:
            with self.subTest(formato=formato):
                image = self.imagem(formato)
                response = self.enviar_cartaz(film['codigo'], image, 'application/octet-stream')
                self.assertEqual(response.status_code, 200)
                saved = self.client.get(response.json()['filme']['cartaz_url'])
                self.assertEqual(saved.content, image)
                self.assertEqual(saved.headers['content-type'], tipo)

    def test_editar_substituir_e_excluir_cartaz(self):
        film = self.criar_filme()
        film = self.enviar_cartaz(film['codigo'], self.imagem()).json()['filme']
        old_url = film['cartaz_url']
        film['nome'] = 'Nome atualizado'
        response = self.client.put(f'/cinema/filmes/update/{film["codigo"]}', json=film)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['filme']['cartaz_url'], old_url)
        database.load_state()
        self.assertEqual(self.client.get(old_url).status_code, 200)
        response = self.enviar_cartaz(film['codigo'], self.imagem(cor='blue'))
        new_url = response.json()['filme']['cartaz_url']
        self.assertNotEqual(new_url, old_url)
        self.assertEqual(self.client.get(old_url).status_code, 404)
        self.assertEqual(self.client.get(new_url).status_code, 200)
        film['cartaz_url'] = 'https://example.com/poster.jpg'
        self.assertEqual(self.client.put(f'/cinema/filmes/update/{film["codigo"]}', json=film).status_code, 200)
        self.assertEqual(self.client.get(new_url).status_code, 404)
        url = self.enviar_cartaz(film['codigo'], self.imagem()).json()['filme']['cartaz_url']
        self.assertEqual(self.client.delete(f'/cinema/filmes/{film["codigo"]}').status_code, 200)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_upload_invalido_preserva_cartaz_atual(self):
        film = self.criar_filme()
        image = self.imagem()
        url = self.enviar_cartaz(film['codigo'], image).json()['filme']['cartaz_url']
        cases = [(b'', 400), (b'<svg></svg>', 415), (image[:32], 415),
                 (self.imagem('GIF'), 415), (b'x' * (5 * 1024 * 1024 + 1), 413)]
        for content, status in cases:
            with self.subTest(status=status, size=len(content)):
                self.assertEqual(self.enviar_cartaz(film['codigo'], content).status_code, status)
        with patch.object(controller, 'MAX_CARTAZ_PIXELS', 10):
            self.assertEqual(self.enviar_cartaz(film['codigo'], image).status_code, 413)
        self.assertEqual(self.enviar_cartaz(999, image).status_code, 404)
        self.assertEqual(self.client.post(f'/cinema/filmes/{film["codigo"]}/cartaz').status_code, 422)
        self.assertTrue(database.load_state())
        self.assertEqual(self.client.get('/cinema/filmes').json()['filmes'][0]['cartaz_url'], url)
        self.assertEqual(self.client.get(url).content, image)
        with closing(sqlite3.connect(database.DB_PATH)) as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM cartazes').fetchone()[0], 1)

    def test_falha_ao_persistir_reverte_imagem_e_referencia(self):
        film = self.criar_filme()
        image = self.imagem()
        url = self.enviar_cartaz(film['codigo'], image).json()['filme']['cartaz_url']
        with patch.object(database, '_save_state', side_effect=sqlite3.OperationalError('falha simulada')):
            with self.assertRaises(sqlite3.OperationalError):
                self.enviar_cartaz(film['codigo'], self.imagem(cor='blue'))
        self.assertEqual(cinema.filmes[0].cartaz_url, url)
        self.assertTrue(database.load_state())
        self.assertEqual(cinema.filmes[0].cartaz_url, url)
        self.assertEqual(self.client.get(url).content, image)
        with closing(sqlite3.connect(database.DB_PATH)) as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM cartazes').fetchone()[0], 1)
