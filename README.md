# Cinema API

API REST para gerenciar valores de ingresso, salas, filmes, sessões e vendas de ingressos de um cinema. O projeto usa FastAPI, mantém o estado em memória durante a execução e o persiste em um banco SQLite.

## Tecnologias

- Python 3.10 ou superior
- FastAPI
- Uvicorn
- SQLite
- `unittest`

## Estrutura do projeto

```text
.
├── main.py             # cria a aplicação, inicializa o banco e expõe as telas
├── controller.py       # modelos de entrada e endpoints REST
├── cinema.py           # entidades e regras de negócio
├── database.py         # persistência do estado em SQLite
├── static/
│   ├── index.html      # programação pública
│   ├── app.js          # integração da programação com a API
│   ├── style.css       # estilos da programação
│   ├── admin.html      # painel administrativo
│   ├── admin.js        # operações administrativas pela API
│   └── admin.css       # estilos do painel administrativo
├── tests.py            # testes unitários das regras de negócio
├── test_programacao.py # testes de integração das telas e da API
├── cinema.db           # banco SQLite da aplicação
└── Aula 2/             # materiais e versão anterior da atividade
```

## Instalação

No diretório do projeto, crie um ambiente virtual e instale as dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install fastapi uvicorn httpx2
```

`httpx2` é usado apenas pelo cliente de testes de integração do FastAPI.

No Windows PowerShell, a ativação do ambiente é feita com:

```powershell
.venv\Scripts\Activate.ps1
```

## Execução

Com o ambiente virtual ativo:

```bash
python3 -m uvicorn main:app --reload
```

Também é possível iniciar a aplicação com `python3 main.py`. Por padrão, o servidor fica disponível em `http://localhost:8000`.

- Programação pública: <http://localhost:8000/>
- Painel administrativo: <http://localhost:8000/admin>
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
| `GET` | `/cinema/tipos-ingresso` | — | Lista inteira, meia-entrada e seus fatores de preço. |
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
  "duracao": 120,
  "cartaz_url": "https://exemplo.com/cartaz.jpg"
}
```

O campo `cartaz_url` é opcional e aceita URLs HTTP ou HTTPS.

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

## Painel administrativo

O painel em `/admin` consome os mesmos endpoints REST e não exige autenticação. Por ele é possível:

- cadastrar, editar e excluir valores, salas, filmes e sessões;
- visualizar os totais e a ocupação das sessões;
- vender ingressos inteiros ou de meia-entrada por assento;
- cancelar ingressos e liberar assentos ocupados;
- abrir a programação pública ou a documentação da API.

Como solicitado, esta versão não implementa login nem controle de acesso. Em uma publicação na internet, a rota deve ser protegida antes do uso em produção.

## Testes

Execute a suíte de testes unitários a partir da raiz do projeto:

```bash
python3 -m unittest -v
```

Os testes cobrem cadastro e validação de valores, salas e sessões, consulta por data, compra e cancelamento de ingressos.
