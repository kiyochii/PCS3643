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

## 5. Tela única: Programação do cinema

Abra http://localhost:8000/ após iniciar o servidor. A interface usa HTML,
CSS e JavaScript, servidos pelo próprio FastAPI, sem etapa de build.

Organização da tela:

- Cabeçalho e filtros: busca por nome e data da sessão, limpar e atualizar.
- Área principal: filmes com cartaz, nome, duração, período de exibição e
  sessões com data, horário, sala, formato e quantidade de lugares livres.
- Área lateral: todas as salas, suas capacidades e formatos; tipos de ingresso
  (inteira e meia-entrada) e preços por formato de sala.
- Em celulares, as informações laterais ficam abaixo dos filmes.

Todos os dados são consultados via `fetch` nos endpoints REST existentes e no
novo `GET /cinema/tipos-ingresso`. A página é de consulta, sem fluxo de compra
ou telas de cadastro. Os cadastros existentes continuam disponíveis em `/docs`.

### Cartazes

Os endpoints POST e PUT de filmes aceitam o campo opcional `cartaz_url`
com uma URL HTTP ou HTTPS da imagem. Ele é devolvido nas consultas e persistido
no SQLite. Exemplo de corpo (substitua a URL pela imagem real do filme):

```json
{
  "nome": "Meu filme",
  "data_estreia": "01-09-2026",
  "data_saida": "30-09-2026",
  "duracao": 120,
  "cartaz_url": "https://example.com/cartaz.jpg"
}
```

Registros antigos continuam funcionando. Quando não há URL ou a imagem não
carrega, a tela mostra “Cartaz indisponível”. Não são inseridos dados fictícios
no banco. Cadastre filmes, salas, valores e sessões pela API para preencher a tela.

### Verificação

```bash
python3 -m unittest tests test_programacao
```

Os testes da API exigem também `pip install httpx` e usam um banco temporário.
