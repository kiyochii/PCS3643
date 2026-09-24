const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const money = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

const state = {
  filmes: [],
  salas: [],
  sessoes: [],
  tipo_sala: {},
  selectedSeats: new Set(),
  ticketTypes: new Map(),
};

function node(tag, text, className) {
  const item = document.createElement(tag);
  if (text !== undefined) item.textContent = text;
  if (className) item.className = className;
  return item;
}

function actionButton(label, action, id, className = '') {
  const button = node('button', label, `icon-button ${className}`.trim());
  button.type = 'button';
  button.dataset.action = action;
  button.dataset.id = id;
  return button;
}

function plural(value, singular, pluralForm = `${singular}s`) {
  return `${value} ${value === 1 ? singular : pluralForm}`;
}

function toApiDate(value) {
  if (!value) return '';
  const [year, month, day] = value.split('-');
  return `${day}-${month}-${year}`;
}

function toInputDate(value) {
  if (!value) return '';
  const [day, month, year] = value.split(/[-/]/);
  return `${year}-${month}-${day}`;
}

function displayDate(value) {
  return value ? value.replaceAll('-', '/') : '—';
}

function toast(message, type = 'success') {
  const item = node('div', message, `toast ${type === 'error' ? 'error' : ''}`.trim());
  $('#toast-region').append(item);
  window.setTimeout(() => item.remove(), 4500);
}

function errorMessage(payload, fallback) {
  if (!payload) return fallback;
  if (typeof payload.detail === 'string') return payload.detail;
  if (Array.isArray(payload.detail)) return payload.detail.map(item => item.msg).join(' ');
  return fallback;
}

async function api(path, options = {}) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 15000);
  const config = { cache: 'no-store', ...options, signal: controller.signal };
  if (config.body) config.headers = { 'Content-Type': 'application/json', ...config.headers };

  try {
    const response = await fetch(path, config);
    const payload = await response.json().catch(() => null);
    if (!response.ok) throw new Error(errorMessage(payload, `A operação falhou (${response.status}).`));
    return payload;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('A API demorou para responder. Tente novamente.');
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

async function loadData({ quiet = false } = {}) {
  const refresh = $('#refresh');
  refresh.disabled = true;
  $('#sync-status').textContent = 'Sincronizando…';
  try {
    const [movies, rooms, sessions, prices] = await Promise.all([
      api('/cinema/filmes'),
      api('/cinema/salas'),
      api('/cinema/sessoes'),
      api('/cinema/valor-ingresso'),
    ]);
    state.filmes = movies.filmes;
    state.salas = rooms.salas;
    state.sessoes = sessions.sessoes;
    state.tipo_sala = prices.tipo_sala;
    renderAll();
    const now = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' }).format(new Date());
    $('#sync-status').textContent = `Sincronizado às ${now}`;
    $('#last-update').textContent = `Dados atualizados às ${now}. As alterações são persistidas automaticamente.`;
    $('.status-dot').style.background = 'var(--success)';
    if (!quiet) toast('Dados atualizados com sucesso.');
  } catch (error) {
    $('#sync-status').textContent = 'Falha na sincronização';
    $('#last-update').textContent = 'Não foi possível consultar a API.';
    $('.status-dot').style.background = 'var(--danger)';
    toast(error.message, 'error');
  } finally {
    refresh.disabled = false;
  }
}

function renderAll() {
  renderStats();
  renderPrices();
  renderRooms();
  renderMovies();
  renderSessions();
  fillRelationSelects();
  renderTicketSessionSelect();
  renderSeatMap();
}

function renderStats() {
  const sold = state.sessoes.reduce(
    (total, session) => total + Object.values(session.assentos || {}).filter(value => value === 1).length,
    0,
  );
  $('#stat-filmes').textContent = state.filmes.length;
  $('#stat-salas').textContent = state.salas.length;
  $('#stat-sessoes').textContent = state.sessoes.length;
  $('#stat-ocupacao').textContent = sold;
}

function emptyRow(columns, message) {
  const row = node('tr', undefined, 'empty-row');
  const cell = node('td', message);
  cell.colSpan = columns;
  row.append(cell);
  return row;
}

function renderPrices() {
  const target = $('#prices-list');
  target.replaceChildren();
  const entries = Object.entries(state.tipo_sala).sort(([a], [b]) => a.localeCompare(b));
  if (!entries.length) target.append(emptyRow(4, 'Nenhum valor cadastrado.'));
  for (const [type, value] of entries) {
    const row = node('tr');
    const formatCell = node('td');
    formatCell.append(node('span', type, 'pill'));
    const actions = node('td', undefined, 'actions');
    actions.append(actionButton('Editar', 'edit-price', type), actionButton('Excluir', 'delete-price', type, 'delete'));
    row.append(formatCell, node('td', money.format(value)), node('td', money.format(value / 2)), actions);
    target.append(row);
  }
}

function renderRooms() {
  const target = $('#rooms-list');
  target.replaceChildren();
  const rooms = [...state.salas].sort((a, b) => a.numero - b.numero);
  $('#rooms-count').textContent = plural(rooms.length, 'sala');
  if (!rooms.length) target.append(emptyRow(4, 'Nenhuma sala cadastrada.'));
  for (const room of rooms) {
    const actions = node('td', undefined, 'actions');
    actions.append(actionButton('Editar', 'edit-room', room.numero), actionButton('Excluir', 'delete-room', room.numero, 'delete'));
    const formatCell = node('td');
    formatCell.append(node('span', room.tipo, 'pill'));
    const row = node('tr');
    row.append(node('td', `Sala ${room.numero}`), formatCell, node('td', plural(room.capacidade, 'lugar', 'lugares')), actions);
    target.append(row);
  }
}

function safePoster(film) {
  if (film.cartaz_url && /^https?:\/\//i.test(film.cartaz_url)) {
    const image = node('img', undefined, 'entity-poster');
    image.src = film.cartaz_url;
    image.alt = '';
    image.loading = 'lazy';
    image.referrerPolicy = 'no-referrer';
    image.addEventListener('error', () => image.replaceWith(node('div', '▷', 'entity-poster poster-fallback')), { once: true });
    return image;
  }
  return node('div', '▷', 'entity-poster poster-fallback');
}

function renderMovies() {
  const target = $('#movies-list');
  target.replaceChildren();
  const movies = [...state.filmes].sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
  $('#movies-count').textContent = plural(movies.length, 'filme');
  if (!movies.length) target.append(node('p', 'Nenhum filme cadastrado.', 'empty-state'));
  for (const film of movies) {
    const row = node('article', undefined, 'entity-row');
    const info = node('div');
    info.append(
      node('strong', film.nome),
      node('p', `${film.duracao} min · ${displayDate(film.data_estreia)} até ${displayDate(film.data_saida)}`),
    );
    const actions = node('div', undefined, 'row-actions');
    actions.append(actionButton('Editar', 'edit-movie', film.codigo), actionButton('Excluir', 'delete-movie', film.codigo, 'delete'));
    row.append(safePoster(film), info, actions);
    target.append(row);
  }
}

function sessionSort(a, b) {
  return toInputDate(a.data).localeCompare(toInputDate(b.data)) || a.hora_inicio - b.hora_inicio;
}

function renderSessions() {
  const target = $('#sessions-list');
  target.replaceChildren();
  const sessions = [...state.sessoes].sort(sessionSort);
  $('#sessions-count').textContent = plural(sessions.length, 'sessão', 'sessões');
  if (!sessions.length) target.append(emptyRow(5, 'Nenhuma sessão cadastrada.'));
  for (const session of sessions) {
    const seats = Object.values(session.assentos || {});
    const occupied = seats.filter(value => value === 1).length;
    const percent = seats.length ? Math.round((occupied / seats.length) * 100) : 0;
    const occupancy = node('td');
    const wrap = node('div', undefined, 'occupancy');
    wrap.append(node('small', `${occupied}/${seats.length} · ${percent}%`));
    const progress = node('div', undefined, 'progress');
    const bar = node('i');
    bar.style.width = `${percent}%`;
    progress.append(bar);
    wrap.append(progress);
    occupancy.append(wrap);

    const actions = node('td', undefined, 'actions');
    actions.append(actionButton('Editar', 'edit-session', session.codigo), actionButton('Excluir', 'delete-session', session.codigo, 'delete'));
    const roomCell = node('td');
    roomCell.append(node('span', `Sala ${session.sala.numero} · ${session.sala.tipo}`, 'pill'));
    const row = node('tr');
    row.append(
      node('td', session.filme.nome),
      node('td', `${displayDate(session.data)} · ${String(session.hora_inicio).padStart(2, '0')}:00`),
      roomCell,
      occupancy,
      actions,
    );
    target.append(row);
  }
}

function replaceOptions(select, items, placeholder, value, label) {
  const selected = select.value;
  select.replaceChildren();
  const first = node('option', placeholder);
  first.value = '';
  select.append(first);
  for (const item of items) {
    const option = node('option', label(item));
    option.value = value(item);
    select.append(option);
  }
  if ([...select.options].some(option => option.value === selected)) select.value = selected;
}

function fillRelationSelects() {
  replaceOptions(
    $('#session-form [name="codigo_filme"]'),
    [...state.filmes].sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR')),
    'Selecione um filme',
    item => item.codigo,
    item => item.nome,
  );
  replaceOptions(
    $('#session-form [name="numero_sala"]'),
    [...state.salas].sort((a, b) => a.numero - b.numero),
    'Selecione uma sala',
    item => item.numero,
    item => `Sala ${item.numero} · ${item.tipo} · ${item.capacidade} lugares`,
  );
}

function renderTicketSessionSelect() {
  replaceOptions(
    $('#ticket-form [name="codigo_sessao"]'),
    [...state.sessoes].sort(sessionSort),
    'Selecione uma sessão',
    item => item.codigo,
    item => `${displayDate(item.data)} · ${String(item.hora_inicio).padStart(2, '0')}:00 · ${item.filme.nome} · Sala ${item.sala.numero}`,
  );
}

function selectedSession() {
  const code = Number($('#ticket-form [name="codigo_sessao"]').value);
  return state.sessoes.find(session => session.codigo === code);
}

function ticketOperation() {
  return $('#ticket-form [name="operation"]:checked').value;
}

function renderSeatMap() {
  const target = $('#seat-map');
  const session = selectedSession();
  const operation = ticketOperation();
  target.replaceChildren();

  if (!session) {
    state.selectedSeats.clear();
    state.ticketTypes.clear();
    target.style.removeProperty('--seat-cols');
    target.append(node('p', 'Nenhuma sessão selecionada.', 'empty-state'));
    $('#seat-hint').textContent = 'Selecione uma sessão para visualizar a sala.';
    renderTicketSummary();
    return;
  }

  const seats = Object.entries(session.assentos || {}).map(([number, occupied]) => [Number(number), occupied]).sort((a, b) => a[0] - b[0]);
  const eligible = new Set(seats.filter(([, occupied]) => operation === 'buy' ? occupied === 0 : occupied === 1).map(([number]) => number));
  state.selectedSeats = new Set([...state.selectedSeats].filter(number => eligible.has(number)));
  for (const number of [...state.ticketTypes.keys()]) if (!state.selectedSeats.has(number)) state.ticketTypes.delete(number);

  const columns = Math.min(10, Math.max(5, Math.ceil(Math.sqrt(Math.max(seats.length, 1)))));
  target.style.setProperty('--seat-cols', columns);
  $('#seat-hint').textContent = `${session.filme.nome} · Sala ${session.sala.numero} · ${plural(seats.length, 'assento')}`;

  for (const [number, occupied] of seats) {
    const button = node('button', number, 'seat');
    button.type = 'button';
    button.dataset.seat = number;
    button.setAttribute('aria-label', `Assento ${number}, ${occupied ? 'ocupado' : 'livre'}`);
    if (occupied) button.classList.add('occupied');
    if (operation === 'cancel' && occupied) button.classList.add('cancelable');
    if (!eligible.has(number)) button.disabled = true;
    if (state.selectedSeats.has(number)) button.classList.add('selected');
    target.append(button);
  }
  renderTicketSummary();
}

function renderTicketSummary() {
  const selected = [...state.selectedSeats].sort((a, b) => a - b);
  const operation = ticketOperation();
  const session = selectedSession();
  $('#selected-seats').textContent = selected.length ? selected.join(', ') : 'Nenhum';
  const typeTarget = $('#ticket-types');
  typeTarget.replaceChildren();

  if (operation === 'buy') {
    for (const seat of selected) {
      const row = node('label', undefined, 'ticket-type-row');
      row.append(node('span', `Assento ${seat}`));
      const select = node('select');
      select.dataset.ticketSeat = seat;
      for (const [value, label] of [['0', 'Inteira'], ['1', 'Meia-entrada']]) {
        const option = node('option', label);
        option.value = value;
        select.append(option);
      }
      select.value = String(state.ticketTypes.get(seat) ?? 0);
      row.append(select);
      typeTarget.append(row);
    }
  }

  const basePrice = session ? Number(state.tipo_sala[session.sala.tipo] || 0) : 0;
  const total = selected.reduce((sum, seat) => sum + basePrice * ((state.ticketTypes.get(seat) ?? 0) === 1 ? .5 : 1), 0);
  $('#estimated-total').textContent = selected.length
    ? operation === 'buy' ? `Total estimado: ${money.format(total)}` : plural(selected.length, 'ingresso para cancelamento', 'ingressos para cancelamento')
    : 'Selecione os lugares no mapa';
  const submit = $('#ticket-form [type="submit"]');
  submit.disabled = !session || !selected.length;
  submit.textContent = operation === 'buy' ? 'Confirmar venda' : 'Confirmar cancelamento';
  submit.classList.toggle('danger', operation === 'cancel');
  submit.classList.toggle('primary', operation === 'buy');
}

function resetPriceForm() {
  const form = $('#price-form');
  form.reset();
  form.elements.original_type.value = '';
  form.elements.tipo_sala.disabled = false;
  $('#price-form-title').textContent = 'Novo valor';
  $('.cancel-edit', form).hidden = true;
}

function resetRoomForm() {
  const form = $('#room-form');
  form.reset();
  form.elements.original_number.value = '';
  form.elements.numero.disabled = false;
  $('#room-form-title').textContent = 'Nova sala';
  $('.cancel-edit', form).hidden = true;
}

function resetMovieForm() {
  const form = $('#movie-form');
  form.reset();
  form.elements.codigo.value = '';
  $('#movie-form-title').textContent = 'Novo filme';
  $('.cancel-edit', form).hidden = true;
}

function resetSessionForm() {
  const form = $('#session-form');
  form.reset();
  form.elements.codigo.value = '';
  $('#session-form-title').textContent = 'Nova sessão';
  $('.cancel-edit', form).hidden = true;
  $('.edit-warning', form).hidden = true;
}

async function submitMutation(form, task, successMessage, reset) {
  const button = $('[type="submit"]', form);
  const original = button.textContent;
  button.disabled = true;
  button.textContent = 'Salvando…';
  try {
    await task();
    reset();
    await loadData({ quiet: true });
    toast(successMessage);
  } catch (error) {
    toast(error.message, 'error');
  } finally {
    button.disabled = false;
    if (button.textContent === 'Salvando…') button.textContent = original;
  }
}

$('#price-form').addEventListener('submit', event => {
  event.preventDefault();
  const form = event.currentTarget;
  const original = form.elements.original_type.value;
  const payload = { tipo_sala: form.elements.tipo_sala.value, valor_ingresso: Number(form.elements.valor_ingresso.value) };
  submitMutation(
    form,
    () => api(original ? `/cinema/valor-ingresso/update/${encodeURIComponent(original)}` : '/cinema/valor-ingresso', { method: original ? 'PUT' : 'POST', body: JSON.stringify(payload) }),
    original ? 'Valor atualizado.' : 'Valor cadastrado.',
    resetPriceForm,
  );
});

$('#room-form').addEventListener('submit', event => {
  event.preventDefault();
  const form = event.currentTarget;
  const original = form.elements.original_number.value;
  const payload = { numero: Number(form.elements.numero.value), capacidade: Number(form.elements.capacidade.value), tipo_sala: form.elements.tipo_sala.value };
  submitMutation(
    form,
    () => api(original ? `/cinema/salas/update/${original}` : '/cinema/salas', { method: original ? 'PUT' : 'POST', body: JSON.stringify(payload) }),
    original ? 'Sala atualizada.' : 'Sala cadastrada.',
    resetRoomForm,
  );
});

$('#movie-form').addEventListener('submit', event => {
  event.preventDefault();
  const form = event.currentTarget;
  const code = form.elements.codigo.value;
  const payload = {
    nome: form.elements.nome.value.trim(),
    data_estreia: toApiDate(form.elements.data_estreia.value),
    data_saida: toApiDate(form.elements.data_saida.value),
    duracao: Number(form.elements.duracao.value),
    cartaz_url: form.elements.cartaz_url.value.trim() || null,
  };
  submitMutation(
    form,
    () => api(code ? `/cinema/filmes/update/${code}` : '/cinema/filmes', { method: code ? 'PUT' : 'POST', body: JSON.stringify(payload) }),
    code ? 'Filme atualizado.' : 'Filme cadastrado.',
    resetMovieForm,
  );
});

$('#session-form').addEventListener('submit', event => {
  event.preventDefault();
  const form = event.currentTarget;
  const code = form.elements.codigo.value;
  if (code) {
    const current = state.sessoes.find(item => item.codigo === Number(code));
    const occupied = current && Object.values(current.assentos || {}).some(value => value === 1);
    if (occupied && !window.confirm('Esta sessão possui ingressos vendidos. Ao atualizar, todos os assentos serão liberados. Deseja continuar?')) return;
  }
  const payload = {
    numero_sala: Number(form.elements.numero_sala.value),
    codigo_filme: Number(form.elements.codigo_filme.value),
    data_sessao: toApiDate(form.elements.data_sessao.value),
    hora_inicio: Number(form.elements.hora_inicio.value),
  };
  submitMutation(
    form,
    () => api(code ? `/cinema/sessoes/update/${code}` : '/cinema/sessoes', { method: code ? 'PUT' : 'POST', body: JSON.stringify(payload) }),
    code ? 'Sessão atualizada.' : 'Sessão cadastrada.',
    resetSessionForm,
  );
});

$('#ticket-form').addEventListener('submit', async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const session = selectedSession();
  const seats = [...state.selectedSeats].sort((a, b) => a - b);
  if (!session || !seats.length) return;
  const operation = ticketOperation();
  const body = operation === 'buy'
    ? { assentos: seats, tipos_ingresso: seats.map(seat => state.ticketTypes.get(seat) ?? 0) }
    : { assentos: seats };
  const button = $('[type="submit"]', form);
  button.disabled = true;
  try {
    const result = await api(`/cinema/sessoes/${session.codigo}/ingressos`, { method: operation === 'buy' ? 'POST' : 'DELETE', body: JSON.stringify(body) });
    state.selectedSeats.clear();
    state.ticketTypes.clear();
    await loadData({ quiet: true });
    toast(operation === 'buy' ? `Venda concluída: ${money.format(result.total)}.` : `${plural(result.assentos_removidos, 'ingresso cancelado', 'ingressos cancelados')}.`);
  } catch (error) {
    toast(error.message, 'error');
  } finally {
    renderTicketSummary();
  }
});

$('#ticket-form [name="codigo_sessao"]').addEventListener('change', () => {
  state.selectedSeats.clear();
  state.ticketTypes.clear();
  renderSeatMap();
});

$$('#ticket-form [name="operation"]').forEach(input => input.addEventListener('change', () => {
  state.selectedSeats.clear();
  state.ticketTypes.clear();
  renderSeatMap();
}));

$('#seat-map').addEventListener('click', event => {
  const button = event.target.closest('[data-seat]');
  if (!button || button.disabled) return;
  const seat = Number(button.dataset.seat);
  if (state.selectedSeats.has(seat)) {
    state.selectedSeats.delete(seat);
    state.ticketTypes.delete(seat);
  } else {
    state.selectedSeats.add(seat);
    state.ticketTypes.set(seat, 0);
  }
  renderSeatMap();
});

$('#ticket-types').addEventListener('change', event => {
  const select = event.target.closest('[data-ticket-seat]');
  if (!select) return;
  state.ticketTypes.set(Number(select.dataset.ticketSeat), Number(select.value));
  renderTicketSummary();
});

document.addEventListener('click', async event => {
  const button = event.target.closest('[data-action]');
  if (!button) return;
  const id = button.dataset.id;
  const action = button.dataset.action;

  if (action === 'edit-price') {
    const form = $('#price-form');
    form.elements.original_type.value = id;
    form.elements.tipo_sala.value = id;
    form.elements.tipo_sala.disabled = true;
    form.elements.valor_ingresso.value = state.tipo_sala[id];
    $('#price-form-title').textContent = `Editar valor ${id}`;
    $('.cancel-edit', form).hidden = false;
    form.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  if (action === 'edit-room') {
    const room = state.salas.find(item => item.numero === Number(id));
    const form = $('#room-form');
    form.elements.original_number.value = room.numero;
    form.elements.numero.value = room.numero;
    form.elements.numero.disabled = true;
    form.elements.capacidade.value = room.capacidade;
    form.elements.tipo_sala.value = room.tipo;
    $('#room-form-title').textContent = `Editar sala ${room.numero}`;
    $('.cancel-edit', form).hidden = false;
    form.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  if (action === 'edit-movie') {
    const film = state.filmes.find(item => item.codigo === Number(id));
    const form = $('#movie-form');
    form.elements.codigo.value = film.codigo;
    form.elements.nome.value = film.nome;
    form.elements.data_estreia.value = toInputDate(film.data_estreia);
    form.elements.data_saida.value = toInputDate(film.data_saida);
    form.elements.duracao.value = film.duracao;
    form.elements.cartaz_url.value = film.cartaz_url || '';
    $('#movie-form-title').textContent = `Editar ${film.nome}`;
    $('.cancel-edit', form).hidden = false;
    form.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  if (action === 'edit-session') {
    const session = state.sessoes.find(item => item.codigo === Number(id));
    const form = $('#session-form');
    form.elements.codigo.value = session.codigo;
    form.elements.codigo_filme.value = session.filme.codigo;
    form.elements.numero_sala.value = session.sala.numero;
    form.elements.data_sessao.value = toInputDate(session.data);
    form.elements.hora_inicio.value = session.hora_inicio;
    $('#session-form-title').textContent = `Editar sessão #${session.codigo}`;
    $('.cancel-edit', form).hidden = false;
    $('.edit-warning', form).hidden = false;
    form.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  const deleteConfig = {
    'delete-price': { message: `Excluir o valor de ingresso ${id}?`, path: `/cinema/valor-ingresso/${encodeURIComponent(id)}`, success: 'Valor excluído.' },
    'delete-room': { message: `Excluir a sala ${id}? As sessões associadas também serão removidas.`, path: `/cinema/salas/${id}`, success: 'Sala excluída.' },
    'delete-movie': { message: 'Excluir este filme? As sessões associadas também serão removidas.', path: `/cinema/filmes/${id}`, success: 'Filme excluído.' },
    'delete-session': { message: 'Excluir esta sessão e todos os ingressos vinculados?', path: `/cinema/sessoes/${id}`, success: 'Sessão excluída.' },
  }[action];

  if (deleteConfig && window.confirm(deleteConfig.message)) {
    button.disabled = true;
    try {
      await api(deleteConfig.path, { method: 'DELETE' });
      await loadData({ quiet: true });
      toast(deleteConfig.success);
    } catch (error) {
      button.disabled = false;
      toast(error.message, 'error');
    }
  }
});

$('.cancel-edit', $('#price-form')).addEventListener('click', resetPriceForm);
$('.cancel-edit', $('#room-form')).addEventListener('click', resetRoomForm);
$('.cancel-edit', $('#movie-form')).addEventListener('click', resetMovieForm);
$('.cancel-edit', $('#session-form')).addEventListener('click', resetSessionForm);
$('#refresh').addEventListener('click', () => loadData());

const sections = $$('.page-section');
const navLinks = $$('.nav-link');
const observer = new IntersectionObserver(entries => {
  const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
  if (!visible) return;
  navLinks.forEach(link => link.classList.toggle('active', link.hash === `#${visible.target.id}`));
}, { rootMargin: '-20% 0px -65%', threshold: [0, .2, .5] });
sections.forEach(section => observer.observe(section));

loadData({ quiet: true });
