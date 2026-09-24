import requests
import unittest
from unittest import mock

BASE_URL = 'http://localhost:8000'

SALA = {
    'numero': 1,
    'capacidade': 50,
    'tipo': '2D',
}

FILME = {
    'codigo': 1,
    'nome': 'Duna',
    'data_estreia': '01-01-2026',
    'data_saida': '31-01-2026',
    'duracao': 155,
}

SESSAO = {
    'codigo': 1,
    'sala': SALA,
    'filme': FILME,
    'data': '10-01-2026',
    'hora_inicio': 20,
    'assentos': {'1': 0, '2': 0, '3': 0},
}


class CinemaAPI:

    # Ingressos
    def cadastrar_valor_ingresso(self, dados):
        response = requests.post(f'{BASE_URL}/cinema/valor-ingresso', json=dados)
        return response.json()

    def atualizar_valor_ingresso(self, tipo_sala, dados):
        response = requests.put(f'{BASE_URL}/cinema/valor-ingresso/update/{tipo_sala}', json=dados)
        return response.json()

    def remover_valor_ingresso(self, tipo_sala):
        response = requests.delete(f'{BASE_URL}/cinema/valor-ingresso/{tipo_sala}')
        return response.json()

    def listar_valores_ingresso(self):
        response = requests.get(f'{BASE_URL}/cinema/valor-ingresso')
        return response.json()

    # salas

    def cadastrar_sala(self, dados):
        response = requests.post(f'{BASE_URL}/cinema/salas', json=dados)
        return response.json()

    def atualizar_sala(self, numero_sala, dados):
        response = requests.put(f'{BASE_URL}/cinema/salas/update/{numero_sala}', json=dados)
        return response.json()

    def remover_sala(self, numero_sala):
        response = requests.delete(f'{BASE_URL}/cinema/salas/{numero_sala}')
        return response.json()

    def listar_salas(self):
        response = requests.get(f'{BASE_URL}/cinema/salas')
        return response.json()

    # filmes

    def cadastrar_filme(self, dados):
        response = requests.post(f'{BASE_URL}/cinema/filmes', json=dados)
        return response.json()

    def atualizar_filme(self, codigo_filme, dados):
        response = requests.put(f'{BASE_URL}/cinema/filmes/update/{codigo_filme}', json=dados)
        return response.json()

    def remover_filme(self, codigo_filme):
        response = requests.delete(f'{BASE_URL}/cinema/filmes/{codigo_filme}')
        return response.json()

    def listar_filmes(self):
        response = requests.get(f'{BASE_URL}/cinema/filmes')
        return response.json()

    def listar_filmes_por_data(self, data):
        response = requests.get(f'{BASE_URL}/cinema/filmes/data/{data}')
        return response.json()

    # sessoes

    def cadastrar_sessao(self, dados):
        response = requests.post(f'{BASE_URL}/cinema/sessoes', json=dados)
        return response.json()

    def atualizar_sessao(self, codigo_sessao, dados):
        response = requests.put(f'{BASE_URL}/cinema/sessoes/update/{codigo_sessao}', json=dados)
        return response.json()

    def remover_sessao(self, codigo_sessao):
        response = requests.delete(f'{BASE_URL}/cinema/sessoes/{codigo_sessao}')
        return response.json()

    def listar_sessoes(self):
        response = requests.get(f'{BASE_URL}/cinema/sessoes')
        return response.json()

    # ingressos

    def comprar_ingressos(self, codigo_sessao, dados):
        response = requests.post(f'{BASE_URL}/cinema/sessoes/{codigo_sessao}/ingressos', json=dados)
        return response.json()

    def remover_ingressos(self, codigo_sessao, dados):
        response = requests.delete(f'{BASE_URL}/cinema/sessoes/{codigo_sessao}/ingressos', json=dados)
        return response.json()


    def acessar_raiz(self):
        response = requests.get(f'{BASE_URL}/')
        return response.status_code

    def persistir_estado(self):
        response = requests.post(f'{BASE_URL}/persist')
        return response.json()


class MockResponse:

    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mocked_requests_post(*args, **kwargs):
    if args[0] == f'{BASE_URL}/cinema/valor-ingresso':
        return MockResponse({'success': True, 'tipo_sala': '2D', 'valor_ingresso': 30}, 200)

    if args[0] == f'{BASE_URL}/cinema/salas':
        return MockResponse({'success': True, 'sala': SALA}, 200)

    if args[0] == f'{BASE_URL}/cinema/filmes':
        return MockResponse({'success': True, 'filme': FILME}, 200)

    if args[0] == f'{BASE_URL}/cinema/sessoes':
        return MockResponse({'success': True, 'sessao': SESSAO}, 200)

    if args[0] == f'{BASE_URL}/cinema/sessoes/1/ingressos':
        return MockResponse({
            'success': True,
            'codigo_sessao': 1,
            'total': 45.0,
            'assentos': [1, 2],
            'tipos_ingresso': [0, 1],
        }, 200)

    if args[0] == f'{BASE_URL}/persist':
        return MockResponse({'success': True, 'message': 'Estado salvo com sucesso.'}, 200)

    return MockResponse(None, 404)

def mocked_requests_put(*args, **kwargs):
    if args[0] == f'{BASE_URL}/cinema/valor-ingresso/update/2D':
        return MockResponse({'success': True, 'tipo_sala': '2D', 'valor_ingresso': 35}, 200)

    if args[0] == f'{BASE_URL}/cinema/salas/update/1':
        return MockResponse({'success': True, 'sala': {'numero': 1, 'capacidade': 80, 'tipo': '3D'}}, 200)

    if args[0] == f'{BASE_URL}/cinema/filmes/update/1':
        return MockResponse({'success': True, 'filme': {
            'codigo': 1,
            'nome': 'Duna: Parte 2',
            'data_estreia': '01-01-2026',
            'data_saida': '28-02-2026',
            'duracao': 166,
        }}, 200)

    if args[0] == f'{BASE_URL}/cinema/sessoes/update/1':
        return MockResponse({'success': True, 'sessao': {
            'codigo': 1,
            'sala': SALA,
            'filme': FILME,
            'data': '11-01-2026',
            'hora_inicio': 22,
            'assentos': {'1': 0, '2': 0, '3': 0},
        }}, 200)

    return MockResponse(None, 404)

def mocked_requests_delete(*args, **kwargs):
    if args[0] == f'{BASE_URL}/cinema/valor-ingresso/2D':
        return MockResponse({'success': True, 'tipo_sala': '2D'}, 200)

    if args[0] == f'{BASE_URL}/cinema/salas/1':
        return MockResponse({'success': True, 'numero_sala': 1}, 200)

    if args[0] == f'{BASE_URL}/cinema/filmes/1':
        return MockResponse({'success': True, 'codigo_filme': 1}, 200)

    if args[0] == f'{BASE_URL}/cinema/sessoes/1':
        return MockResponse({'success': True, 'codigo_sessao': 1}, 200)

    if args[0] == f'{BASE_URL}/cinema/sessoes/1/ingressos':
        return MockResponse({
            'success': True,
            'codigo_sessao': 1,
            'assentos_removidos': 2,
            'assentos': [1, 2],
        }, 200)

    return MockResponse(None, 404)


def mocked_requests_get(*args, **kwargs):
    if args[0] == f'{BASE_URL}/cinema/valor-ingresso':
        return MockResponse({'tipo_sala': {'2D': 30, '3D': 50}}, 200)

    if args[0] == f'{BASE_URL}/cinema/salas':
        return MockResponse({'salas': [SALA]}, 200)

    if args[0] == f'{BASE_URL}/cinema/filmes':
        return MockResponse({'filmes': [FILME]}, 200)

    if args[0] == f'{BASE_URL}/cinema/sessoes':
        return MockResponse({'sessoes': [SESSAO]}, 200)

    if args[0] == f'{BASE_URL}/cinema/filmes/data/10-01-2026':
        return MockResponse({
            'data': '10-01-2026',
            'resultado': '1: Duna, sala 1 (2D), 20h, 30 reais.',
        }, 200)

    if args[0] == f'{BASE_URL}/':
        return MockResponse(None, 200)

    return MockResponse(None, 404)


class TestValorIngresso(unittest.TestCase):

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_cadastrar_valor_ingresso(self, mock_post):
        api = CinemaAPI()
        dados = {'tipo_sala': '2D', 'valor_ingresso': 30}

        resposta = api.cadastrar_valor_ingresso(dados)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['tipo_sala'], '2D')
        self.assertEqual(resposta['valor_ingresso'], 30)
        mock_post.assert_called_once_with(f'{BASE_URL}/cinema/valor-ingresso', json=dados)

    @mock.patch('requests.put', side_effect=mocked_requests_put)
    def test_atualizar_valor_ingresso(self, mock_put):
        api = CinemaAPI()
        dados = {'tipo_sala': '2D', 'valor_ingresso': 35}

        resposta = api.atualizar_valor_ingresso('2D', dados)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['valor_ingresso'], 35)
        mock_put.assert_called_once_with(f'{BASE_URL}/cinema/valor-ingresso/update/2D', json=dados)

    @mock.patch('requests.delete', side_effect=mocked_requests_delete)
    def test_remover_valor_ingresso(self, mock_delete):
        api = CinemaAPI()

        resposta = api.remover_valor_ingresso('2D')

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['tipo_sala'], '2D')
        mock_delete.assert_called_once_with(f'{BASE_URL}/cinema/valor-ingresso/2D')

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_listar_valores_ingresso(self, mock_get):
        api = CinemaAPI()

        resposta = api.listar_valores_ingresso()

        self.assertIsInstance(resposta['tipo_sala'], dict)
        self.assertEqual(resposta['tipo_sala']['2D'], 30)
        self.assertEqual(resposta['tipo_sala']['3D'], 50)
        mock_get.assert_called_once_with(f'{BASE_URL}/cinema/valor-ingresso')


class TestSalas(unittest.TestCase):

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_cadastrar_sala(self, mock_post):
        api = CinemaAPI()
        dados = {'numero': 1, 'capacidade': 50, 'tipo_sala': '2D'}

        resposta = api.cadastrar_sala(dados)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['sala']['numero'], 1)
        self.assertEqual(resposta['sala']['capacidade'], 50)
        self.assertEqual(resposta['sala']['tipo'], '2D')
        mock_post.assert_called_once_with(f'{BASE_URL}/cinema/salas', json=dados)

    @mock.patch('requests.put', side_effect=mocked_requests_put)
    def test_atualizar_sala(self, mock_put):
        api = CinemaAPI()
        dados = {'numero': 1, 'capacidade': 80, 'tipo_sala': '3D'}

        resposta = api.atualizar_sala(1, dados)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['sala']['capacidade'], 80)
        self.assertEqual(resposta['sala']['tipo'], '3D')
        mock_put.assert_called_once_with(f'{BASE_URL}/cinema/salas/update/1', json=dados)

    @mock.patch('requests.delete', side_effect=mocked_requests_delete)
    def test_remover_sala(self, mock_delete):
        api = CinemaAPI()

        resposta = api.remover_sala(1)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['numero_sala'], 1)
        mock_delete.assert_called_once_with(f'{BASE_URL}/cinema/salas/1')

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_listar_salas(self, mock_get):
        api = CinemaAPI()

        resposta = api.listar_salas()

        self.assertIsInstance(resposta['salas'], list)
        self.assertEqual(len(resposta['salas']), 1)
        self.assertEqual(resposta['salas'][0]['numero'], 1)
        mock_get.assert_called_once_with(f'{BASE_URL}/cinema/salas')


class TestFilmes(unittest.TestCase):

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_cadastrar_filme(self, mock_post):
        api = CinemaAPI()
        dados = {
            'nome': 'Duna',
            'data_estreia': '01-01-2026',
            'data_saida': '31-01-2026',
            'duracao': 155,
        }

        resposta = api.cadastrar_filme(dados)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['filme']['codigo'], 1)
        self.assertEqual(resposta['filme']['nome'], 'Duna')
        self.assertEqual(resposta['filme']['duracao'], 155)
        mock_post.assert_called_once_with(f'{BASE_URL}/cinema/filmes', json=dados)

    @mock.patch('requests.put', side_effect=mocked_requests_put)
    def test_atualizar_filme(self, mock_put):
        api = CinemaAPI()
        dados = {
            'nome': 'Duna: Parte 2',
            'data_estreia': '01-01-2026',
            'data_saida': '28-02-2026',
            'duracao': 166,
        }

        resposta = api.atualizar_filme(1, dados)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['filme']['nome'], 'Duna: Parte 2')
        self.assertEqual(resposta['filme']['data_saida'], '28-02-2026')
        mock_put.assert_called_once_with(f'{BASE_URL}/cinema/filmes/update/1', json=dados)

    @mock.patch('requests.delete', side_effect=mocked_requests_delete)
    def test_remover_filme(self, mock_delete):
        api = CinemaAPI()

        resposta = api.remover_filme(1)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['codigo_filme'], 1)
        mock_delete.assert_called_once_with(f'{BASE_URL}/cinema/filmes/1')

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_listar_filmes(self, mock_get):
        api = CinemaAPI()

        resposta = api.listar_filmes()

        self.assertIsInstance(resposta['filmes'], list)
        self.assertEqual(len(resposta['filmes']), 1)
        self.assertEqual(resposta['filmes'][0]['nome'], 'Duna')
        mock_get.assert_called_once_with(f'{BASE_URL}/cinema/filmes')

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_listar_filmes_por_data(self, mock_get):
        api = CinemaAPI()

        resposta = api.listar_filmes_por_data('10-01-2026')

        self.assertEqual(resposta['data'], '10-01-2026')
        self.assertIn('Duna', resposta['resultado'])
        self.assertIn('30 reais', resposta['resultado'])
        mock_get.assert_called_once_with(f'{BASE_URL}/cinema/filmes/data/10-01-2026')


class TestSessoes(unittest.TestCase):

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_cadastrar_sessao(self, mock_post):
        api = CinemaAPI()
        dados = {
            'numero_sala': 1,
            'codigo_filme': 1,
            'data_sessao': '10-01-2026',
            'hora_inicio': 20,
        }

        resposta = api.cadastrar_sessao(dados)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['sessao']['codigo'], 1)
        self.assertEqual(resposta['sessao']['sala']['numero'], 1)
        self.assertEqual(resposta['sessao']['filme']['nome'], 'Duna')
        self.assertEqual(resposta['sessao']['hora_inicio'], 20)
        mock_post.assert_called_once_with(f'{BASE_URL}/cinema/sessoes', json=dados)

    @mock.patch('requests.put', side_effect=mocked_requests_put)
    def test_atualizar_sessao(self, mock_put):
        api = CinemaAPI()
        dados = {
            'numero_sala': 1,
            'codigo_filme': 1,
            'data_sessao': '11-01-2026',
            'hora_inicio': 22,
        }

        resposta = api.atualizar_sessao(1, dados)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['sessao']['data'], '11-01-2026')
        self.assertEqual(resposta['sessao']['hora_inicio'], 22)
        mock_put.assert_called_once_with(f'{BASE_URL}/cinema/sessoes/update/1', json=dados)

    @mock.patch('requests.delete', side_effect=mocked_requests_delete)
    def test_remover_sessao(self, mock_delete):
        api = CinemaAPI()

        resposta = api.remover_sessao(1)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['codigo_sessao'], 1)
        mock_delete.assert_called_once_with(f'{BASE_URL}/cinema/sessoes/1')

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_listar_sessoes(self, mock_get):
        api = CinemaAPI()

        resposta = api.listar_sessoes()

        self.assertIsInstance(resposta['sessoes'], list)
        self.assertEqual(len(resposta['sessoes']), 1)
        self.assertEqual(resposta['sessoes'][0]['codigo'], 1)
        self.assertIn('1', resposta['sessoes'][0]['assentos'])
        mock_get.assert_called_once_with(f'{BASE_URL}/cinema/sessoes')


class TestIngressos(unittest.TestCase):

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_comprar_ingressos(self, mock_post):
        api = CinemaAPI()
        dados = {'assentos': [1, 2], 'tipos_ingresso': [0, 1]}

        resposta = api.comprar_ingressos(1, dados)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['codigo_sessao'], 1)
        self.assertEqual(resposta['total'], 45.0)
        self.assertEqual(resposta['assentos'], [1, 2])
        mock_post.assert_called_once_with(f'{BASE_URL}/cinema/sessoes/1/ingressos', json=dados)

    @mock.patch('requests.delete', side_effect=mocked_requests_delete)
    def test_remover_ingressos(self, mock_delete):
        api = CinemaAPI()
        dados = {'assentos': [1, 2]}

        resposta = api.remover_ingressos(1, dados)

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['codigo_sessao'], 1)
        self.assertEqual(resposta['assentos_removidos'], 2)
        mock_delete.assert_called_once_with(f'{BASE_URL}/cinema/sessoes/1/ingressos', json=dados)


class TestAplicacao(unittest.TestCase):

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_acessar_raiz(self, mock_get):
        api = CinemaAPI()

        status = api.acessar_raiz()

        self.assertEqual(status, 200)
        mock_get.assert_called_once_with(f'{BASE_URL}/')

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_persistir_estado(self, mock_post):
        api = CinemaAPI()

        resposta = api.persistir_estado()

        self.assertTrue(resposta['success'])
        self.assertEqual(resposta['message'], 'Estado salvo com sucesso.')
        mock_post.assert_called_once_with(f'{BASE_URL}/persist')


if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=2, exit=False)
