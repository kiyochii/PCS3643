"""Contrato REST da tela e compatibilidade dos cartazes no SQLite."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import cinema
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
        with sqlite3.connect(database.DB_PATH) as connection:
            connection.execute('INSERT INTO app_state VALUES (?, ?)', ('cinema_state', json.dumps(old)))
        self.assertTrue(database.load_state())
        self.assertIsNone(self.client.get('/cinema/filmes').json()['filmes'][0]['cartaz_url'])
