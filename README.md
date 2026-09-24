# Cinema API

[![Status do workflow](https://github.com/henri/PCS3643/actions/workflows/testes.yml/badge.svg)](https://github.com/henri/PCS3643/actions/workflows/testes.yml)

API REST para gerenciar valores de ingresso, salas, filmes, sessões e vendas de ingressos de um cinema. O projeto usa FastAPI, mantém o estado em memória durante a execução e o persiste em um banco SQLite.

## Tecnologias

- Python 3.10 ou superior
- FastAPI
- Uvicorn
- SQLite
- `unittest`
- `httpx` (para os testes de API com TestClient)

## Estrutura do projeto

```text
.
├── main.py                 # cria a aplicação, inicializa o banco e expõe rotas gerais
├── controller.py           # modelos de entrada e endpoints REST
├── cinema.py               # entidades e regras de negócio
├── database.py             # persistência do estado em SQLite
├── tests.py                # testes unitários das regras de negócio
├── test_programacao.py     # testes de integração da programação e do armazenamento em SQLite
├── .github/workflows/      # workflows de automação do GitHub Actions
├── cinema.db               # banco SQLite da aplicação
├── env/                    # ambiente virtual do projeto
└── Aula 2/                 # materiais e versão anterior da atividade
```

## Instalação

No diretório do projeto, crie um ambiente virtual e instale as dependências:

```bash
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install fastapi uvicorn httpx
```

No Windows PowerShell, a ativação do ambiente é feita com:

```powershell
.\env\Scripts\Activate.ps1
```

## Execução

Com o ambiente virtual ativo:

```bash
python3 -m uvicorn main:app --reload
```

Também é possível iniciar a aplicação com `python3 main.py`. Por padrão, o servidor fica disponível em `http://localhost:8000`.

- `/` redireciona para a documentação interativa.
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Especificação OpenAPI: <http://localhost:8000/openapi.json>

## Endpoints

As rotas de negócio usam o prefixo `/cinema`.

| Método | Rota | Corpo da requisição | Descrição |
|---|---|---|---|
| `POST` | `/cinema/valor-ingresso` | `ValorIngresso` | Cadastra o valor de um tipo de sala. |
| `PUT` | `/cinema/valor-ingresso/update/{tipo_sala_nome}` | `ValorIngresso` | Atualiza um valor existente. |
| `DELETE` | `/cinema/valor-ingresso/{tipo_sala_nome}` | — | Remove o valor de um tipo de sala. |
| `GET` | `/cinema/valor-ingresso` | — | Lista os valores cadastrados. |
| `POST` | `/cinema/salas` | `Sala` | Cadastra uma sala. |
| `PUT` | `/cinema/salas/update/{numero_sala}` | `Sala` | Atualiza uma sala. |
| `DELETE` | `/cinema/salas/{numero_sala}` | — | Remove uma sala. |
| `GET` | `/cinema/salas` | — | Lista as salas. |
| `POST` | `/cinema/filmes` | `Filme` | Cadastra um filme. |
| `PUT` | `/cinema/filmes/update/{codigo_filme}` | `Filme` | Atualiza um filme. |
| `DELETE` | `/cinema/filmes/{codigo_filme}` | — | Remove um filme. |
| `GET` | `/cinema/filmes` | — | Lista os filmes. |
| `GET` | `/cinema/filmes/data/{data}` | — | Lista sessões disponíveis na data informada. |
| `POST` | `/cinema/sessoes` | `Sessao` | Cadastra uma sessão. |
| `PUT` | `/cinema/sessoes/update/{codigo_sessao}` | `Sessao` | Atualiza uma sessão. |
| `DELETE` | `/cinema/sessoes/{codigo_sessao}` | — | Remove uma sessão. |
| `GET` | `/cinema/sessoes` | — | Lista as sessões e seus assentos. |
| `POST` | `/cinema/sessoes/{codigo_sessao}/ingressos` | `CompraIngressos` | Compra ingressos e ocupa os assentos. |
| `DELETE` | `/cinema/sessoes/{codigo_sessao}/ingressos` | `RemocaoIngressos` | Cancela ingressos e libera os assentos. |
| `POST` | `/persist` | — | Força a gravação do estado atual no banco. |

### Formatos dos corpos JSON

`ValorIngresso`:

```json
{
  "tipo_sala": "2D",
  "valor_ingresso": 40
}
```

`Sala`:

```json
{
  "numero": 1,
  "capacidade": 100,
  "tipo_sala": "2D"
}
```

`Filme`:

```json
{
  "nome": "Filme A",
  "data_estreia": "01-09-2026",
  "data_saida": "30-09-2026",
  "duracao": 120
}
```

`Sessao`:

```json
{
  "numero_sala": 1,
  "codigo_filme": 1,
  "data_sessao": "10-09-2026",
  "hora_inicio": 18
}
```

`CompraIngressos`:

```json
{
  "assentos": [1, 2],
  "tipos_ingresso": [0, 1]
}
```

`RemocaoIngressos`:

```json
{
  "assentos": [1, 2]
}
```

## Regras principais

- Os tipos de sala aceitos são `2D` e `3D`, e os valores de ingresso devem ser inteiros positivos.
- Datas podem ser enviadas como `dd-mm-aaaa` ou `dd/mm/aaaa`; a API as armazena no formato `dd-mm-aaaa`.
- A hora inicial de uma sessão é um inteiro entre `0` e `23`.
- Não pode haver duas sessões na mesma sala, data e hora.
- Os assentos são numerados de `1` até a capacidade da sala. Na resposta das sessões, `0` indica assento livre e `1`, ocupado.
- Na compra, `0` representa ingresso inteiro e `1`, meia-entrada. As listas `assentos` e `tipos_ingresso` devem ter o mesmo tamanho e se relacionam pela posição.
- Compras e cancelamentos são atômicos: se um dos assentos for inválido, nenhum deles é alterado.
- Atualizar uma sessão recria o mapa de assentos como livre, de acordo com a capacidade da sala selecionada.
- Remover uma sala ou um filme também remove as sessões associadas.

## Persistência

Na inicialização, a aplicação cria `cinema.db`, caso necessário, e carrega dele o último estado salvo. Toda operação de criação, atualização, remoção ou compra feita pela API salva o estado automaticamente. O endpoint `POST /persist` permite solicitar essa gravação manualmente.

## Testes

Execute a suíte de testes a partir da raiz do projeto:

```bash
python3 -m unittest discover -s . -p "test*.py"
```

Se estiver usando o ambiente virtual do projeto, o comando equivalente é:

```bash
./env/bin/python -m unittest discover -s . -p "test*.py"
```

Os testes cobrem cadastro e validação de valores, salas e sessões, consulta por data, compra e cancelamento de ingressos, além da verificação da programação e do estado persistido em SQLite.

## GitHub Actions / CI

O projeto possui um workflow para rodar os testes automaticamente em cada push e pull request. O arquivo está em [.github/workflows/testes.yml](.github/workflows/testes.yml) e executa a suíte com:

```yaml
- name: Rodando os testes
  run: python -m unittest discover -s . -p "test*.py"
```

A instalação do ambiente de CI inclui também a dependência do `httpx`, necessária para os testes de API via `TestClient`.
