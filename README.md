# API de Cinema

## 1. Instalação

No diretório do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn
```

## 2. Como rodar

```bash
source .venv/bin/activate
python3 -m uvicorn main:app --reload
```

Acesse o Swagger em:
- http://localhost:8000/docs

## 3. Endpoints

Todos os endpoints ficam sob o prefixo:

```text
/cinema
```

### 3.1. Valores de ingresso
- `POST /cinema/valor-ingresso`
- `PUT /cinema/valor-ingresso/update/{tipo_sala_nome}`
- `DELETE /cinema/valor-ingresso/{tipo_sala_nome}`
- `GET /cinema/valor-ingresso`

### 3.2. Salas
- `POST /cinema/salas`
- `PUT /cinema/salas/update/{numero_sala}`
- `DELETE /cinema/salas/{numero_sala}`
- `GET /cinema/salas`

### 3.3. Filmes
- `POST /cinema/filmes`
- `PUT /cinema/filmes/update/{codigo_filme}`
- `DELETE /cinema/filmes/{codigo_filme}`
- `GET /cinema/filmes`
- `GET /cinema/filmes/data/{data}`

### 3.4. Sessões
- `POST /cinema/sessoes`
- `PUT /cinema/sessoes/update/{codigo_sessao}`
- `DELETE /cinema/sessoes/{codigo_sessao}`
- `GET /cinema/sessoes`

### 3.5. Ingressos
- `POST /cinema/sessoes/{codigo_sessao}/ingressos`
- `DELETE /cinema/sessoes/{codigo_sessao}/ingressos`

## 4. Observações

- A aplicação salva tudo em um único banco SQLite: `cinema.db`.
- O Swagger fica em `/docs` e pode ser usado para testar os endpoints no navegador.
- A data deve seguir o formato `dd-mm-aaaa`.
