const $ = (selector) => document.querySelector(selector);
const money = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
let catalog = null;
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function dateKey(value) { return value.split(/[-/]/).reverse().join('-'); }
function displayDate(value) { return value.replaceAll('-', '/'); }
function empty(target, message) { target.append(element('p', message, 'empty')); }
function renderMovies() {
  if (!catalog) return;
  const query = $('#search').value.trim().toLocaleLowerCase('pt-BR');
  const date = $('#date').value;
  const movies = catalog.filmes.filter(film => film.nome.toLocaleLowerCase('pt-BR').includes(query)
    && (!date || catalog.sessoes.some(s => s.filme.codigo === film.codigo && dateKey(s.data) === date)));
  $('#movies').replaceChildren();
  $('#count').textContent = `${movies.length} filme${movies.length === 1 ? '' : 's'}`;
  if (!movies.length) empty($('#movies'), catalog.filmes.length ? 'Nenhum filme encontrado para esses filtros.' : 'Nenhum filme cadastrado. A programação aparecerá aqui quando estiver disponível.');
  for (const film of movies) {
    const card = element('article', undefined, 'movie');
    const fallback = () => element('div', 'Cartaz indisponível', 'poster poster-placeholder');
    let poster = fallback();
    if (film.cartaz_url && (/^https?:\/\//i.test(film.cartaz_url) || /^\/cinema\/cartazes\/[0-9a-f]{32}$/.test(film.cartaz_url))) {
      poster = element('img', undefined, 'poster');
      poster.alt = `Cartaz de ${film.nome}`;
      poster.loading = 'lazy';
      poster.referrerPolicy = 'no-referrer';
      poster.addEventListener('error', () => poster.replaceWith(fallback()), { once: true });
      poster.src = film.cartaz_url;
    }
    const details = element('div');
    details.append(element('h3', film.nome), element('p', `${film.duracao} min · De ${displayDate(film.data_estreia)} a ${displayDate(film.data_saida)}`, 'movie-meta'));
    const sessions = element('div', undefined, 'sessions');
    const matching = catalog.sessoes.filter(s => s.filme.codigo === film.codigo && (!date || dateKey(s.data) === date))
      .sort((a, b) => dateKey(a.data).localeCompare(dateKey(b.data)) || a.hora_inicio - b.hora_inicio);
    for (const session of matching) {
      const item = element('div', undefined, 'session');
      const available = Object.values(session.assentos).filter(value => value === 0).length;
      item.append(element('span', displayDate(session.data)), element('strong', `${String(session.hora_inicio).padStart(2, '0')}:00`),
        element('span', `Sala ${session.sala.numero} · ${session.sala.tipo}`), element('span', available ? `${available} lugares livres` : 'Sessão esgotada'));
      sessions.append(item);
    }
    if (!matching.length) sessions.append(element('p', 'Sem sessões cadastradas.', 'muted'));
    details.append(sessions);
    card.append(poster, details);
    $('#movies').append(card);
  }
}
function renderInfo() {
  $('#rooms').replaceChildren();
  $('#tickets').replaceChildren();
  for (const room of catalog.salas) {
    const row = element('div', undefined, 'room');
    const info = element('div', `Sala ${room.numero}`);
    info.append(element('small', `${room.capacidade} lugares`));
    row.append(info, element('span', room.tipo, 'badge'));
    $('#rooms').append(row);
  }
  if (!catalog.salas.length) empty($('#rooms'), 'Nenhuma sala cadastrada.');
  const prices = Object.entries(catalog.tipo_sala);
  if (!prices.length) {
    for (const type of catalog.tipos_ingresso) $('#tickets').append(element('p', type.nome));
    empty($('#tickets'), 'Valores ainda não cadastrados.');
  }
  for (const [format, value] of prices) {
    const group = element('div', undefined, 'price-group');
    group.append(element('h3', `Sala ${format}`));
    for (const type of catalog.tipos_ingresso) {
      const row = element('div', undefined, 'price');
      row.append(element('span', type.nome), element('strong', money.format(value * type.fator)));
      group.append(row);
    }
    $('#tickets').append(group);
  }
}
async function load() {
  $('#reload').disabled = true;
  $('#movies').setAttribute('aria-busy', 'true');
  $('#status').textContent = 'Carregando a programação…';
  try {
    const results = await Promise.all(['filmes', 'sessoes', 'salas', 'valor-ingresso', 'tipos-ingresso'].map(async resource => {
      const response = await fetch(`/cinema/${resource}`, { signal: AbortSignal.timeout(15000), cache: 'no-store' });
      if (!response.ok) throw new Error('Falha ao consultar a programação');
      return response.json();
    }));
    catalog = Object.assign({}, ...results);
    renderMovies();
    renderInfo();
    $('#status').textContent = 'Programação atualizada. Use os filtros para encontrar uma sessão.';
  } catch {
    $('#status').textContent = catalog
      ? 'Não foi possível atualizar. Os dados anteriores continuam visíveis. Tente novamente em Atualizar.'
      : 'Não foi possível carregar a programação. Verifique sua conexão e tente novamente em Atualizar.';
  } finally {
    $('#reload').disabled = false;
    $('#movies').setAttribute('aria-busy', 'false');
  }
}
$('#filters').addEventListener('submit', event => event.preventDefault());
$('#search').addEventListener('input', renderMovies);
$('#date').addEventListener('change', renderMovies);
$('#filters').addEventListener('reset', () => setTimeout(renderMovies, 0));
$('#reload').addEventListener('click', load);
load();
