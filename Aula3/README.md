# Cinema — Aula 3

YUHANG FANG 18442107

## Organização MVC

```text
Aula3/
├── controllers/       # Rotas HTTP, um controlador por recurso
│   ├── filmes.py
│   ├── salas.py
│   ├── sessoes.py
│   ├── tipos_ingresso.py
│   └── precos.py
├── models/            # Entidades originais e erros de domínio
│   ├── filme.py
│   ├── sala.py
│   ├── sessao.py
│   ├── tipo_ingresso.py
│   └── errors.py
├── repositories/      # Operações SQLite, um repositório por recurso
│   ├── base.py         # Busca e remoção compartilhadas
│   ├── filmes.py
│   ├── salas.py
│   ├── sessoes.py
│   ├── tipos_ingresso.py
│   └── precos.py
├── schemas.py         # Validação dos dados recebidos pela API
├── database.py        # Conexão, transações e criação das tabelas
├── main.py            # Inicialização e registro dos controladores
├── cinema.py          # Compatibilidade com os imports originais
└── tests.py
```

Os **controllers** recebem as requisições validadas pelos schemas e chamam os
**repositories**, que mantêm as operações e verificações existentes junto ao banco
e retornam as entidades de **models**. O FastAPI serializa os resultados em JSON;
a interface continua sendo o Swagger UI em `/docs`, sem templates HTML próprios.

O `cinema.py` apenas reexporta as entidades e funções para preservar os imports
anteriores. As rotas, respostas, regras, transações e estrutura do banco continuam
iguais; o código da Aula 2 permanece separado.

## Executar

**Com pip e venv:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

**Com [uv](https://docs.astral.sh/uv/getting-started/installation/) instalado:**

```bash
uv venv
uv pip install -r requirements.txt
uv run uvicorn main:app --reload
```

Abra [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) e use **Try it out → Execute**.
O banco `cinema.db` é criado automaticamente e mantém os dados após reiniciar. Encerre com `Ctrl+C`.

## API

| Recurso           | Listar                | Cadastrar              | Editar                         | Remover                           |
| ----------------- | --------------------- | ---------------------- | ------------------------------ | --------------------------------- |
| Filmes            | `GET /filmes`         | `POST /filmes`         | `PUT /filmes/{codigo}`         | `DELETE /filmes/{codigo}`         |
| Salas             | `GET /salas`          | `POST /salas`          | `PUT /salas/{numero}`          | `DELETE /salas/{numero}`          |
| Sessões           | `GET /sessoes`        | `POST /sessoes`        | `PUT /sessoes/{codigo}`        | `DELETE /sessoes/{codigo}`        |
| Tipos de ingresso | `GET /tipos-ingresso` | `POST /tipos-ingresso` | `PUT /tipos-ingresso/{codigo}` | `DELETE /tipos-ingresso/{codigo}` |
| Preços            | `GET /precos`         | `POST /precos`         | `PUT /precos/{tipo_sala}`      | `DELETE /precos/{tipo_sala}`      |

Use **POST** para cadastrar, **GET** para consultar o código e **PUT** para editar um registro existente. Cadastre filmes e salas antes das sessões. Datas na API: `dd/mm/aaaa`.

Testes: `python -m unittest -v`
ou `uv run python -m unittest -v`.
