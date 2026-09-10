# Divisão de tarefas e plano de testes - Sistema de venda de ingressos

## Objetivo da atividade

Implementar as seis user stories do sistema de venda de ingressos de cinema e entregar:

- cinema.py, com as classes, listas, dicionário, funções públicas e funções auxiliares;
- tests.py, com os testes unitários;
- um comentário no início dos arquivos com os nomes de todos os integrantes.

O trabalho deve ser feito usando unittest. Cada pessoa deve implementar a sua história e escrever os testes correspondentes. Depois, todos devem integrar as partes e executar a suíte completa.

## Divisão sugerida

Substituam Pessoa 1, Pessoa 2 etc. pelos nomes do grupo.

| Responsável | User story | Entrega principal |
|---|---|---|
| Pessoa 1 | US01 e US02 | Cadastro de filmes e valores dos ingressos |
| Pessoa 2 | US03 | Cadastro das salas |
| Pessoa 3 | US04 | Cadastro das sessões e criação dos assentos |
| Pessoa 4 | US05 | Consulta de filmes por data |
| Pessoa 5 | US06 | Compra de ingressos e reserva dos assentos |

### Se o grupo tiver quatro integrantes

| Responsável | User story |
|---|---|
| Pessoa 1 | US01 e US02 |
| Pessoa 2 | US03 e US04 |
| Pessoa 3 | US05 |
| Pessoa 4 | US06 |

A pessoa responsável por uma história deve entregar tanto a implementação quanto os testes dela. As histórias que dependem de outras devem ser testadas depois que o cenário básico estiver disponível.

## Contrato comum do projeto

Todos devem combinar e manter os mesmos nomes e estruturas. A estrutura recomendada para o arquivo cinema.py é:

~~~python
filmes = []
salas = []
sessoes = []
tipo_sala = {}
~~~

Os objetos cadastrados devem ser adicionados às listas correspondentes:

- filmes: objetos Filme;
- salas: objetos Sala;
- sessoes: objetos Sessao;
- tipo_sala: dicionário que associa o tipo de sala ao preço, por exemplo {"2D": 40, "3D": 50}.

### Atributos esperados

As classes já estão no modelo. Os responsáveis podem acrescentar os atributos necessários sem alterar a ordem dos parâmetros dos construtores:

~~~python
class Filme:
    def __init__(self, nome=None, data_estreia=None, data_saida=None, duracao=None):
        self.codigo = None
        self.nome = nome
        self.data_estreia = data_estreia
        self.data_saida = data_saida
        self.duracao = duracao

class Sala:
    def __init__(self, numero=None, capacidade=None, tipo=None):
        self.numero = numero
        self.capacidade = capacidade
        self.tipo = tipo

class Sessao:
    def __init__(self, sala=None, filme=None, data=None, hora_inicio=None):
        self.codigo = None
        self.sala = sala
        self.filme = filme
        self.data = data
        self.hora_inicio = hora_inicio
        self.assentos = {}
~~~

Para os assentos, usar um dicionário facilita manter a numeração começando em 1:

~~~python
sessao.assentos = {numero: 0 for numero in range(1, sala.capacidade + 1)}
~~~

Nesse dicionário, 0 significa assento livre e 1 significa assento ocupado.

### Funções auxiliares recomendadas

As funções abaixo não precisam ser chamadas diretamente pelos testes. Elas servem para evitar código repetido:

~~~python
from datetime import datetime

def _data_valida(data):
    try:
        return datetime.strptime(data, "%d/%m/%Y")
    except ValueError:
        return None

def _buscar_filme(codigo):
    for filme in filmes:
        if filme.codigo == codigo:
            return filme
    return None

def _buscar_sala(numero):
    for sala in salas:
        if sala.numero == numero:
            return sala
    return None

def _buscar_sessao(codigo):
    for sessao in sessoes:
        if sessao.codigo == codigo:
            return sessao
    return None
~~~

Os nomes são sugestões. O importante é que todos usem a mesma convenção e não criem funções públicas com assinaturas diferentes das solicitadas.

### Observação importante sobre a US02

O enunciado chama tipo_sala de dicionário, mas também diz que o funcionário informa o tipo 2D ou 3D. Para manter a compatibilidade com as outras histórias, a convenção deste documento é:

- tipo_sala é o dicionário global;
- o primeiro argumento de cadastrar_valor_ingresso é a string "2D" ou "3D";
- o valor é salvo no dicionário global.

Assim, os testes devem usar:

~~~python
cinema.cadastrar_valor_ingresso("2D", 40)
cinema.cadastrar_valor_ingresso("3D", 50)
~~~

Se o professor tiver exigido que o primeiro argumento seja o próprio dicionário, o grupo deve ajustar todos os testes e a implementação de forma conjunta. Não misturem as duas convenções.

## Pessoa 1 - US01: cadastrar filmes

### Função a implementar

~~~python
def cadastrar_filme(nome, data_estreia, data_saida, duracao):
    ...
~~~

### Comportamento esperado

1. Validar data_estreia e data_saida no formato dd/mm/aaaa usando datetime.strptime.
2. Rejeitar datas inexistentes, como 31/02/2026, e formatos incorretos, como 2026-02-01 ou 1/2/2026.
3. Rejeitar data de saída anterior à data de estreia.
4. Rejeitar nome vazio ou formado apenas por espaços.
5. Rejeitar duração menor ou igual a zero.
6. Criar um objeto Filme.
7. Atribuir código sequencial, começando em 1.
8. Adicionar o objeto em filmes.
9. Retornar o objeto criado. Em caso de erro, retornar None e não alterar a lista.

O código pode ser gerado com max, para evitar depender de um contador global:

~~~python
novo_codigo = max((filme.codigo for filme in filmes), default=0) + 1
~~~

### Testes que devem ser feitos em tests.py

Criar uma classe como TestUS01CadastrarFilme(unittest.TestCase).

| Nome sugerido do teste | Situação | Verificações |
|---|---|---|
| test_cadastra_filme_valido | Cadastro correto | Retorno não é None, é Filme, os atributos estão corretos e o objeto foi salvo em cinema.filmes |
| test_primeiro_filme_recebe_codigo_1 | Primeiro cadastro | filme.codigo == 1 |
| test_filmes_recebem_codigos_sequenciais | Dois ou mais cadastros | Códigos 1, 2, 3 na ordem |
| test_rejeita_data_inexistente | 31/02/2026 | Retorna None e não adiciona filme |
| test_rejeita_formato_de_data_incorreto | 2026-02-01, 1/2/2026 ou data vazia | Retorna None |
| test_rejeita_data_saida_anterior | Saída antes da estreia | Retorna None |
| test_rejeita_duracao_zero | Duração 0 | Retorna None |
| test_rejeita_duracao_negativa | Duração menor que zero | Retorna None |
| test_rejeita_nome_vazio | Nome vazio ou somente espaços | Retorna None |

Não é necessário criar testes para tipos incorretos dos parâmetros, pois o enunciado informa que isso pode ser considerado válido como pré-condição.

## Pessoa 1 - US02: cadastrar valores dos ingressos

### Função a implementar

~~~python
def cadastrar_valor_ingresso(tipo_sala, valor_ingresso):
    ...
~~~

### Comportamento esperado

1. Aceitar somente os tipos 2D e 3D.
2. Aceitar somente valor maior que zero.
3. Salvar ou atualizar o valor no dicionário tipo_sala.
4. Retornar True quando o cadastro for realizado.
5. Retornar False para tipo inválido ou valor menor ou igual a zero.
6. Em caso de erro, não inserir uma chave inválida nem alterar preços válidos já cadastrados.

Exemplo:

~~~python
tipo_sala = {}

def cadastrar_valor_ingresso(tipo, valor_ingresso):
    if tipo not in ("2D", "3D") or valor_ingresso <= 0:
        return False
    tipo_sala[tipo] = valor_ingresso
    return True
~~~

### Testes que devem ser feitos

Criar uma classe como TestUS02ValorIngresso(unittest.TestCase).

| Nome sugerido do teste | Situação | Verificações |
|---|---|---|
| test_cadastra_valor_para_sala_2d | Tipo 2D, valor positivo | Retorna True e cinema.tipo_sala["2D"] tem o valor informado |
| test_cadastra_valor_para_sala_3d | Tipo 3D, valor positivo | Retorna True e preço correto |
| test_rejeita_tipo_de_sala_invalido | Tipo diferente de 2D e 3D | Retorna False e dicionário não muda |
| test_rejeita_valor_zero | Valor 0 | Retorna False |
| test_rejeita_valor_negativo | Valor menor que zero | Retorna False |
| test_atualiza_valor_de_tipo_ja_cadastrado | Cadastro repetido do mesmo tipo | Se o grupo adotar atualização, retorna True e prevalece o novo valor |

O teste de atualização deve ser mantido somente se o grupo concordar com essa regra. O enunciado não proíbe substituir um preço já cadastrado.

## Pessoa 2 - US03: cadastrar salas

### Função a implementar

~~~python
def cadastrar_sala(numero, capacidade, tipo_sala):
    ...
~~~

### Comportamento esperado

1. Aceitar número de sala maior que zero.
2. Aceitar capacidade maior que zero.
3. Aceitar somente tipo 2D ou 3D.
4. Verificar se já existe sala com o mesmo número.
5. Criar o objeto Sala, adicionar em salas e retorná-lo.
6. Retornar None sem alterar a lista quando houver erro.
7. Não verificar o preço do ingresso nesta função, pois o enunciado permite assumir que ele já foi cadastrado.

### Testes que devem ser feitos

Criar uma classe como TestUS03CadastrarSala(unittest.TestCase).

| Nome sugerido do teste | Situação | Verificações |
|---|---|---|
| test_cadastra_sala_valida | Número, capacidade e tipo válidos | Retorno é Sala, atributos corretos e objeto está em cinema.salas |
| test_rejeita_numero_zero | Número 0 | Retorna None |
| test_rejeita_numero_negativo | Número menor que zero | Retorna None |
| test_rejeita_capacidade_zero | Capacidade 0 | Retorna None |
| test_rejeita_capacidade_negativa | Capacidade menor que zero | Retorna None |
| test_rejeita_tipo_de_sala_invalido | Tipo diferente de 2D e 3D | Retorna None |
| test_rejeita_numero_de_sala_repetido | Cadastro de duas salas com mesmo número | Segundo retorno é None e a lista continua com uma sala |
| test_permite_mesmo_tipo_em_numeros_diferentes | Duas salas 2D com números diferentes | Ambas são cadastradas |

## Pessoa 3 - US04: cadastrar sessões

### Função a implementar

~~~python
def cadastrar_sessao(numero_sala, codigo_filme, data_sessao, hora_inicio):
    ...
~~~

### Comportamento esperado

1. Localizar a sala pelo número.
2. Localizar o filme pelo código.
3. Validar data_sessao com o formato dd/mm/aaaa.
4. Aceitar hora_inicio entre 0 e 23, inclusive.
5. Impedir duas sessões na mesma sala, no mesmo dia e no mesmo horário.
6. Permitir o mesmo horário em salas diferentes.
7. Criar código sequencial para a sessão, começando em 1.
8. Criar os assentos de 1 até a capacidade da sala.
9. Inicializar todos os assentos com valor 0.
10. Adicionar a sessão em sessoes e retorná-la.
11. Retornar None e não alterar a lista quando não for possível cadastrar.

Estrutura sugerida para verificar conflito:

~~~python
for sessao in sessoes:
    mesma_sala = sessao.sala.numero == sala.numero
    mesma_data = sessao.data == data_sessao
    mesmo_horario = sessao.hora_inicio == hora_inicio
    if mesma_sala and mesma_data and mesmo_horario:
        return None
~~~

Para comparar datas com segurança, o grupo pode guardar a string original depois de validá-la ou guardar também o objeto retornado por datetime.strptime. Todos devem usar a mesma decisão.

É coerente impedir uma sessão fora do período entre estreia e saída do filme. Essa regra não aparece de forma explícita na lista de critérios, portanto o grupo deve confirmar e aplicar em todos os testes caso decida adotá-la.

### Testes que devem ser feitos

Criar uma classe como TestUS04CadastrarSessao(unittest.TestCase). No setUp, cadastrar pelo menos um filme e uma sala.

| Nome sugerido do teste | Situação | Verificações |
|---|---|---|
| test_cadastra_sessao_valida | Sala, filme, data e hora válidos | Retorno é Sessao e atributos corretos |
| test_primeira_sessao_recebe_codigo_1 | Primeiro cadastro | sessao.codigo == 1 |
| test_sessoes_recebem_codigos_sequenciais | Dois ou mais cadastros | Códigos crescentes |
| test_cria_assentos_de_1_ate_capacidade | Sala com capacidade 5 | Chaves são 1, 2, 3, 4, 5 |
| test_inicializa_todos_os_assentos_livres | Sessão recém-criada | Todos os valores de sessao.assentos são 0 |
| test_rejeita_sala_inexistente | Número de sala não cadastrado | Retorna None |
| test_rejeita_filme_inexistente | Código de filme não cadastrado | Retorna None |
| test_rejeita_data_inexistente | Data como 31/02/2026 | Retorna None |
| test_rejeita_hora_menor_que_zero | Hora -1 | Retorna None |
| test_rejeita_hora_maior_que_23 | Hora 24 | Retorna None |
| test_rejeita_conflito_na_mesma_sala | Mesma sala, data e hora | Segundo cadastro retorna None |
| test_permite_mesmo_horario_em_sala_diferente | Salas diferentes, mesma data e hora | Duas sessões são cadastradas |
| test_nao_altera_sessoes_quando_falha | Qualquer entrada inválida | Tamanho de cinema.sessoes permanece igual |

Se o grupo adotar a validação do período de exibição, acrescentar testes para sessão antes da estreia e depois da saída.

## Pessoa 4 - US05: listar filmes por data

### Função a implementar

~~~python
def listar_filmes_por_data(data):
    ...
~~~

### Comportamento esperado

1. Validar a data no formato dd/mm/aaaa.
2. Se a data for inválida, retornar exatamente:

~~~text
Data invalida.
~~~

3. Procurar as sessões do dia informado.
4. Considerar somente sessões que tenham pelo menos um assento livre.
5. Permitir que o mesmo filme apareça em várias sessões no mesmo dia.
6. Montar uma linha para cada sessão no formato:

~~~text
<codigo_sessao>: <nome_filme>, sala <numero_sala> (<tipo_sala>), <hora_inicio>h, <valor> reais.
~~~

7. Separar várias linhas com "\n".
8. Se não houver sessão disponível, retornar exatamente:

~~~text
Nenhum filme no dia escolhido.
~~~

9. Usar o preço correspondente a sessao.sala.tipo no dicionário cinema.tipo_sala.
10. Ordenar pelo código da sessão para que o resultado seja determinístico.

Exemplo de montagem:

~~~python
linhas.append(
    f"{sessao.codigo}: {sessao.filme.nome}, "
    f"sala {sessao.sala.numero} ({sessao.sala.tipo}), "
    f"{sessao.hora_inicio}h, {valor} reais."
)
return "\n".join(linhas)
~~~

### Testes que devem ser feitos

Criar uma classe como TestUS05ListarFilmesPorData(unittest.TestCase).

| Nome sugerido do teste | Situação | Verificações |
|---|---|---|
| test_retorna_data_invalida_para_formato_incorreto | Data com separador errado ou formato incompleto | Retorno exato Data invalida. |
| test_retorna_data_invalida_para_data_inexistente | 31/02/2026 | Retorno exato |
| test_retorna_mensagem_sem_sessoes | Data válida sem sessões | Retorno exato Nenhum filme no dia escolhido. |
| test_lista_sessao_com_assento_livre | Sessão com pelo menos um assento 0 | Texto contém código, filme, sala, tipo, hora e preço |
| test_nao_lista_sessao_com_todos_assentos_ocupados | Todos os assentos são 1 | Sessão não aparece |
| test_lista_varias_sessoes_do_mesmo_filme | Duas sessões do mesmo filme no mesmo dia | As duas linhas aparecem |
| test_nao_lista_sessoes_de_outra_data | Sessão em outro dia | Sessão não aparece |
| test_formata_linha_exatamente | Uma sessão conhecida | assertEqual com a string completa |
| test_lista_sessoes_em_ordem_de_codigo | Sessões cadastradas em sequência | A linha de menor código aparece primeiro |
| test_usa_preco_de_acordo_com_tipo_da_sala | Uma sala 2D e outra 3D | Cada linha apresenta o preço correto |

Para ocupar todos os assentos em um teste:

~~~python
for numero in sessao.assentos:
    sessao.assentos[numero] = 1
~~~

## Pessoa 5 - US06: comprar ingressos

### Função a implementar

~~~python
def comprarIngressos(codigo_sessao, assentos, tipos_ingresso):
    ...
~~~

### Comportamento esperado

1. Localizar a sessão pelo código.
2. Verificar se as listas assentos e tipos_ingresso têm o mesmo tamanho.
3. Verificar se elas não estão vazias.
4. Verificar se cada assento está entre 1 e a capacidade da sala.
5. Verificar se nenhum assento escolhido já está ocupado.
6. Verificar se os assentos não estão repetidos na mesma compra.
7. Verificar se cada tipo de ingresso é 0 ou 1.
8. Tipo 0 cobra o valor integral.
9. Tipo 1 cobra metade do valor da sala.
10. Só alterar os assentos depois que todas as validações passarem.
11. Em compra válida, marcar os assentos como 1 e retornar o valor total.
12. Em qualquer falha, retornar 0, não ocupar nenhum assento e não cobrar parcialmente.

Exemplo de cálculo:

~~~python
valor = tipo_sala[sessao.sala.tipo]
total = 0

for tipo in tipos_ingresso:
    if tipo == 0:
        total += valor
    else:
        total += valor / 2
~~~

O grupo deve manter uma política única para preço ímpar. A implementação com / 2 retorna, por exemplo, 15.0 quando o ingresso custa 30; por isso, assertAlmostEqual é uma opção segura para esse caso.

### Testes que devem ser feitos

Criar uma classe como TestUS06ComprarIngressos(unittest.TestCase).

| Nome sugerido do teste | Situação | Verificações |
|---|---|---|
| test_compra_ingresso_inteiro | Um assento e tipo 0 | Retorna preço integral e assento passa a 1 |
| test_compra_ingresso_meia | Um assento e tipo 1 | Retorna metade do preço e assento passa a 1 |
| test_compra_varios_ingressos | Vários assentos e tipos | Soma correta e todos os assentos ficam ocupados |
| test_assento_e_tipo_sao_associados_pela_mesma_posicao | [2, 4] e [0, 1] | Assento 2 cobra inteira e assento 4 cobra meia |
| test_rejeita_sessao_inexistente | Código inválido | Retorna 0 |
| test_rejeita_lista_de_assentos_vazia | [] | Retorna 0 e nada é ocupado |
| test_rejeita_lista_de_tipos_vazia | [] | Retorna 0 e nada é ocupado |
| test_rejeita_listas_de_tamanhos_diferentes | Quantidades diferentes | Retorna 0 e nada é ocupado |
| test_rejeita_assento_zero | Assento 0 | Retorna 0 |
| test_rejeita_assento_acima_da_capacidade | Número maior que a capacidade | Retorna 0 |
| test_rejeita_assento_ja_ocupado | Assento com valor 1 | Retorna 0 |
| test_rejeita_tipo_de_ingresso_invalido | Tipo diferente de 0 e 1 | Retorna 0 |
| test_rejeita_assento_repetido | [2, 2] | Retorna 0 e assento permanece como estava |
| test_compra_e_atomica | Primeiro assento livre e segundo ocupado | Retorna 0 e o primeiro continua livre |
| test_nao_altera_assentos_em_compra_invalida | Qualquer erro após várias validações | Comparar o dicionário antes e depois com assertEqual |

Teste de atomicidade:

~~~python
estado_antes = sessao.assentos.copy()
resultado = cinema.comprarIngressos(
    sessao.codigo,
    [1, 2],
    [0, 0]
)
self.assertEqual(resultado, 0)
self.assertEqual(sessao.assentos, estado_antes)
~~~

## Modelo de setUp para os testes

Cada classe de testes deve começar de um estado limpo. Não dependam da ordem em que os testes são executados.

~~~python
import unittest
import cinema

class TestBase(unittest.TestCase):

    def setUp(self):
        cinema.filmes.clear()
        cinema.salas.clear()
        cinema.sessoes.clear()
        cinema.tipo_sala.clear()

    def criar_cenario_basico(self):
        cinema.cadastrar_valor_ingresso("2D", 40)
        cinema.cadastrar_valor_ingresso("3D", 50)

        filme = cinema.cadastrar_filme(
            "Filme de teste",
            "01/01/2026",
            "31/12/2026",
            120
        )

        sala = cinema.cadastrar_sala(1, 5, "2D")
        sessao = cinema.cadastrar_sessao(
            sala.numero,
            filme.codigo,
            "10/09/2026",
            14
        )
        return filme, sala, sessao
~~~

Uma alternativa mais simples é colocar apenas setUp em cada classe e criar o cenário necessário dentro de cada teste. O ponto essencial é limpar as listas e o dicionário antes de cada caso.

## Asserções unittest mais usadas

~~~python
self.assertEqual(valor_obtido, valor_esperado)
self.assertNotEqual(valor_obtido, valor_inesperado)
self.assertTrue(condicao)
self.assertFalse(condicao)
self.assertIsNone(valor)
self.assertIsNotNone(valor)
self.assertIsInstance(objeto, cinema.Filme)
self.assertIn(chave, dicionario)
self.assertNotIn(chave, dicionario)
self.assertAlmostEqual(valor_obtido, valor_esperado)
~~~

A ordem correta é sempre valor obtido primeiro e valor esperado depois, por exemplo:

~~~python
self.assertEqual(filme.codigo, 1)
~~~

## Testes de integração que o grupo deve executar no final

Além dos testes separados por história, executar estes fluxos completos:

1. Cadastrar preços 2D e 3D.
2. Cadastrar dois filmes.
3. Cadastrar duas salas, uma 2D e uma 3D.
4. Cadastrar sessões em datas e horários diferentes.
5. Consultar uma data e conferir o texto retornado.
6. Comprar um ingresso inteiro e um meio ingresso.
7. Consultar novamente a mesma data e verificar que a sessão desaparece somente quando todos os assentos estiverem ocupados.
8. Tentar comprar uma combinação com um assento livre e outro ocupado e conferir que nenhum dos dois foi alterado.

## Como executar os testes

Na pasta que contém cinema.py e tests.py, executar:

~~~bash
python -m unittest -v
~~~

Também é possível executar diretamente:

~~~bash
python tests.py
~~~

Todos os testes devem passar antes da entrega. O arquivo tests.py final deve conter os testes de todos os integrantes, e não apenas os testes da última pessoa que fez alterações.

## Checklist antes de enviar

- [ ] Os nomes de todos os integrantes estão no comentário inicial de cinema.py e tests.py.
- [ ] As funções públicas mantêm exatamente os nomes solicitados.
- [ ] As listas e o dicionário globais têm uma convenção única.
- [ ] Os códigos de filmes e sessões começam em 1 e são sequenciais.
- [ ] Datas são validadas com o formato dd/mm/aaaa.
- [ ] Salas não têm números repetidos.
- [ ] Sessões não conflitam na mesma sala, data e hora.
- [ ] Assentos começam em 1, terminam na capacidade e iniciam livres.
- [ ] A consulta retorna exatamente as mensagens exigidas.
- [ ] A compra é atômica: se algum assento falhar, nenhum é reservado.
- [ ] Foram testados valores zero, negativos, vazios, duplicados, inválidos e conflitos.
- [ ] python -m unittest -v termina sem falhas.
