import { loadMatches, saveMatchesState, resetMatchesState } from './api.js';
import { calculateStandings, getCountryStats, getTeamInfo, TEAM_MAP } from './utils.js';
import { MatchSimulator, generateEventsForFinishedMatch } from './simulator.js';

// ==========================================================================
// ESTADO GLOBAL DA APLICAÇÃO
// ==========================================================================
let matchesState = [];
let standingsState = {};
let favoritesState = new Set();
let currentPage = 2; // 0: Países, 1: Grupos, 2: Jogos do Dia
let selectedMatchId = null;

let countrySearchQuery = '';
let activeCountryFilter = 'Todos';
let activeGroupFilter = 'Todos';

let simulator = null;

// ==========================================================================
// DOM ELEMENTS CACHE
// ==========================================================================
const DOM = {
  clock: document.getElementById('watch-clock'),
  carouselViewport: document.getElementById('carousel-viewport'),
  dots: document.querySelectorAll('.indicator-dot'),
  watchCrownBtn: document.getElementById('watch-crown-btn'),
  watchScreen: document.getElementById('watch-screen'),
  
  // Tela 1: Países
  countrySearch: document.getElementById('country-search'),
  countryFilters: document.getElementById('country-filters'),
  countriesList: document.getElementById('countries-list'),
  
  // Tela 2: Grupos
  groupFilters: document.getElementById('group-filters'),
  groupsList: document.getElementById('groups-list'),
  
  // Tela 3: Jogos do Dia
  matchesList: document.getElementById('matches-list'),
  
  // Tela 4: Detalhes do Jogo
  matchDetailView: document.getElementById('match-detail-view'),
  detailBackBtn: document.getElementById('detail-back-btn'),
  detailClock: document.getElementById('detail-header-clock'),
  detailScoreCard: document.getElementById('detail-score-card'),
  matchTimeline: document.getElementById('match-timeline'),
  
  // Painel de Controle (Direita)
  simStatus: document.getElementById('sim-status'),
  simMinute: document.getElementById('sim-minute'),
  btnStartSim: document.getElementById('btn-start-sim'),
  btnResetSim: document.getElementById('btn-reset-sim'),
  simSpeed: document.getElementById('sim-speed'),
  speedIndicator: document.getElementById('speed-indicator'),
  favListContainer: document.getElementById('fav-list-container'),
  apiStatusDot: document.getElementById('api-status-dot'),
  apiStatusText: document.getElementById('api-status-text'),
  btnForceSync: document.getElementById('btn-force-sync'),
  simDate: document.getElementById('sim-date')
};

// ==========================================================================
// INICIALIZAÇÃO E EVENTOS
// ==========================================================================
document.addEventListener('DOMContentLoaded', async () => {
  initClock();
  initSwipeGestures();
  loadFavorites();
  
  // Verifica se está rodando no modo embed (esconde controle lateral e atualiza via API)
  const urlParams = new URLSearchParams(window.location.search);
  const isEmbed = urlParams.get('embed') === 'true' || urlParams.get('watch-only') === 'true';
  
  if (isEmbed) {
    document.body.classList.add('embed-mode');
  }
  
  // Carrega jogos
  await syncData(false);
  
  // Configura Simulador
  initSimulator();
  
  // Configura Listeners de Navegação/Filtro
  setupUIEventListeners();
  
  // Renderiza Views Iniciais
  renderAll();

  // Inicia sempre na aba Jogos do Dia (Aba 2 do carrossel) para todas as inicializações
  navigateToPage(2);
  
  // Abre automaticamente os detalhes se houver alguma partida ocorrendo no momento (live)
  const liveMatch = matchesState.find(m => m.status === 'live');
  if (liveMatch) {
    openMatchDetail(liveMatch.id);
  }

  // Se estiver no modo embed, ativa o pull da API minuto a minuto (60s)
  if (isEmbed) {
    setInterval(async () => {
      console.log('Modo Embed: Atualizando dados a partir da API...');
      // Busca dados limpos da API e atualiza o estado
      await syncData(true);
      
      // Re-renderiza as telas ativas
      renderAll();
      
      if (selectedMatchId) {
        const match = matchesState.find(m => m.id === selectedMatchId);
        if (match) {
          renderMatchDetail(match);
        } else {
          closeMatchDetail();
        }
      } else {
        // Se nenhuma partida estava aberta, mas agora começou um jogo ao vivo, abre automaticamente!
        const liveMatch = matchesState.find(m => m.status === 'live');
        if (liveMatch) {
          openMatchDetail(liveMatch.id);
        }
      }
    }, 60000);
  }
});

// Atualiza o relógio do smartwatch em tempo real
function initClock() {
  const updateTime = () => {
    const now = new Date();
    const hrs = String(now.getHours()).padStart(2, '0');
    const mins = String(now.getMinutes()).padStart(2, '0');
    const timeStr = `${hrs}:${mins}`;
    
    if (DOM.clock) DOM.clock.textContent = timeStr;
    if (DOM.detailClock) DOM.detailClock.textContent = timeStr;
  };
  
  updateTime();
  setInterval(updateTime, 30000);
}

// Configura o motor de simulação
function initSimulator() {
  simulator = new MatchSimulator(matchesState, (updatedMatches) => {
    // Callback acionado a cada tick do simulador
    matchesState = updatedMatches;
    saveMatchesState(matchesState);
    standingsState = calculateStandings(matchesState);
    
    // Re-renderiza views
    renderCountries();
    renderGroups();
    renderMatches();
    
    if (selectedMatchId) {
      const match = matchesState.find(m => m.id === selectedMatchId);
      if (match) renderMatchDetail(match);
    }
    
    updateSimulatorPanel();
  });
  
  // Inicializa jogos de hoje (14 de Junho de 2026 na base de dados)
  simulator.initTodayMatches('2026-06-14');
  updateSimulatorPanel();
}

// ==========================================================================
// SINCRONIZAÇÃO E CONTROLE DA API
// ==========================================================================
async function syncData(force = false) {
  setApiStatus('pending', 'Sincronizando dados...');
  try {
    const isMock = force ? false : localStorage.getItem('copa26_matches_state') === null;
    matchesState = await loadMatches(force);
    standingsState = calculateStandings(matchesState);
    
    const count = matchesState.length;
    
    // Verifica se os dados vieram da API ou offline
    const isOffline = matchesState === apiOfflineFallback(); 
    if (isOffline) {
      setApiStatus('offline', `Offline (${count} jogos carregados)`);
    } else {
      setApiStatus('online', `Conectado - API (${count} jogos)`);
    }
  } catch (error) {
    console.error('Erro na sincronização:', error);
    setApiStatus('offline', 'Erro. Usando cache local.');
  }
}

function setApiStatus(status, text) {
  if (!DOM.apiStatusDot || !DOM.apiStatusText) return;
  
  DOM.apiStatusText.textContent = text;
  DOM.apiStatusDot.className = 'api-dot';
  
  if (status === 'online') {
    DOM.apiStatusDot.style.backgroundColor = '#00ff87';
  } else if (status === 'offline') {
    DOM.apiStatusDot.style.backgroundColor = '#ffb703';
  } else {
    DOM.apiStatusDot.style.backgroundColor = '#64748b'; // pending
  }
}

function apiOfflineFallback() {
  // Apenas utilitário para comparação de referência
  return null;
}

// ==========================================================================
// GESTÃO DE FAVORITOS
// ==========================================================================
function loadFavorites() {
  const saved = localStorage.getItem('copa26_favorites');
  if (saved) {
    try {
      favoritesState = new Set(JSON.parse(saved));
    } catch (e) {
      favoritesState = new Set();
    }
  }
}

function toggleFavorite(countryName) {
  if (favoritesState.has(countryName)) {
    favoritesState.delete(countryName);
  } else {
    favoritesState.add(countryName);
  }
  
  localStorage.setItem('copa26_favorites', JSON.stringify([...favoritesState]));
  renderCountries();
  renderFavoritesPanel();
}

// ==========================================================================
// EVENTOS E EVENT LISTENERS DO USUÁRIO
// ==========================================================================
function setupUIEventListeners() {
  // Controle da Busca de Países
  if (DOM.countrySearch) {
    DOM.countrySearch.addEventListener('input', (e) => {
      countrySearchQuery = e.target.value;
      renderCountries();
    });
  }
  
  // Filtros de Continentes
  if (DOM.countryFilters) {
    DOM.countryFilters.addEventListener('click', (e) => {
      const btn = e.target.closest('.filter-pill');
      if (!btn) return;
      
      DOM.countryFilters.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCountryFilter = btn.dataset.filter;
      renderCountries();
    });
  }
  
  // Filtros de Grupos
  if (DOM.groupFilters) {
    DOM.groupFilters.addEventListener('click', (e) => {
      const btn = e.target.closest('.filter-pill');
      if (!btn) return;
      
      DOM.groupFilters.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeGroupFilter = btn.dataset.filter;
      renderGroups();
    });
  }
  
  // Clique nas bolinhas de navegação
  DOM.dots.forEach(dot => {
    dot.addEventListener('click', () => {
      const pageIndex = parseInt(dot.dataset.page, 10);
      navigateToPage(pageIndex);
    });
  });
  
  // Botão Físico do Relógio (Coroa)
  if (DOM.watchCrownBtn) {
    DOM.watchCrownBtn.addEventListener('click', () => {
      // Se estiver em detalhes do jogo, volta
      if (DOM.matchDetailView && DOM.matchDetailView.classList.contains('active')) {
        closeMatchDetail();
      } else {
        // Senão, circula entre as páginas principais 0 -> 1 -> 2 -> 0
        const nextPage = (currentPage + 1) % 3;
        navigateToPage(nextPage);
      }
    });
  }
  
  // Botão Voltar Detalhes
  if (DOM.detailBackBtn) {
    DOM.detailBackBtn.addEventListener('click', closeMatchDetail);
  }
  
  // Botões de Simulação (Direita)
  if (DOM.btnStartSim) {
    DOM.btnStartSim.addEventListener('click', () => {
      if (simulator.isSimulating) {
        simulator.stop();
      } else {
        simulator.start();
      }
      updateSimulatorPanel();
    });
  }
  
  if (DOM.btnResetSim) {
    DOM.btnResetSim.addEventListener('click', async () => {
      if (confirm('Deseja reiniciar a simulação do dia? Os placares e eventos serão resetados.')) {
        setApiStatus('pending', 'Resetando estado...');
        matchesState = await resetMatchesState();
        standingsState = calculateStandings(matchesState);
        initSimulator();
        renderAll();
      }
    });
  }
  
  // Controle de Velocidade
  if (DOM.simSpeed) {
    DOM.simSpeed.addEventListener('input', (e) => {
      const ms = parseInt(e.target.value, 10);
      simulator.setSpeed(ms);
      updateSimulatorPanel();
    });
  }
  
  // Sincronização API Manual
  if (DOM.btnForceSync) {
    DOM.btnForceSync.addEventListener('click', async () => {
      if (confirm('Isso irá apagar a simulação em andamento e sincronizar dados atualizados da API externa. Deseja prosseguir?')) {
        simulator.stop();
        await syncData(true);
        initSimulator();
        renderAll();
      }
    });
  }
}

// Gestão de swipe na tela circular
function initSwipeGestures() {
  let touchStartX = 0;
  let touchEndX = 0;
  let touchStartY = 0;
  let touchEndY = 0;
  
  DOM.watchScreen.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
    touchStartY = e.changedTouches[0].screenY;
  }, { passive: true });
  
  DOM.watchScreen.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    touchEndY = e.changedTouches[0].screenY;
    handleSwipe();
  }, { passive: true });
  
  function handleSwipe() {
    const diffX = touchEndX - touchStartX;
    const diffY = touchEndY - touchStartY;
    
    // Ignora swipes predominantemente verticais para permitir scroll de listas
    if (Math.abs(diffX) < Math.abs(diffY)) return;
    
    // Se o detalhe do jogo estiver ativo, não faz swipe lateral das páginas principais
    if (DOM.matchDetailView.classList.contains('active')) return;
    
    const minSwipeDist = 50; // pixels
    if (Math.abs(diffX) > minSwipeDist) {
      if (diffX < 0) {
        // Swipe Esquerda (Avançar Página)
        const nextPage = Math.min(currentPage + 1, 2);
        navigateToPage(nextPage);
      } else {
        // Swipe Direita (Voltar Página)
        const prevPage = Math.max(currentPage - 1, 0);
        navigateToPage(prevPage);
      }
    }
  }
}

function navigateToPage(pageIndex) {
  currentPage = pageIndex;
  
  // Transiciona o carrossel
  if (DOM.carouselViewport) {
    DOM.carouselViewport.style.transform = `translateX(-${currentPage * 100}%)`;
  }
  
  // Atualiza os dots
  DOM.dots.forEach((dot, index) => {
    if (index === currentPage) {
      dot.classList.add('active');
    } else {
      dot.classList.remove('active');
    }
  });
}

// Abertura/Fechamento da Tela 4: Detalhes
function openMatchDetail(matchId) {
  selectedMatchId = matchId;
  const match = matchesState.find(m => m.id === matchId);
  if (match) {
    renderMatchDetail(match);
    DOM.matchDetailView.classList.add('active');
  }
}

function closeMatchDetail() {
  DOM.matchDetailView.classList.remove('active');
  selectedMatchId = null;
}

// ==========================================================================
// RENDERIZADORES DE LAYOUT DO RELÓGIO (CIRCULAR)
// ==========================================================================
function renderAll() {
  renderCountries();
  renderGroups();
  renderMatches();
  renderFavoritesPanel();
}

// TELA 1: Países
function renderCountries() {
  if (!DOM.countriesList) return;
  
  // Mapeia todas as 48 seleções para obter seus pontos e grupo nos standings
  const countriesData = Object.keys(TEAM_MAP).map(englishName => {
    const info = getTeamInfo(englishName);
    const stats = getCountryStats(englishName, standingsState);
    const isFavorite = favoritesState.has(englishName);
    
    return {
      englishName,
      portugueseName: info.name,
      emoji: info.emoji,
      region: info.region,
      group: stats.group,
      points: stats.points,
      isFavorite,
      // Status de classificado simplificado (top 2 do grupo com jogos finalizados)
      isClassified: stats.games >= 3 && isTeamInQualificationZone(englishName, stats.group)
    };
  });
  
  // Filtro por busca
  let filtered = countriesData;
  if (countrySearchQuery.trim() !== '') {
    const q = countrySearchQuery.toLowerCase();
    filtered = filtered.filter(c => 
      c.portugueseName.toLowerCase().includes(q) || 
      c.englishName.toLowerCase().includes(q)
    );
  }
  
  // Filtro por continente
  if (activeCountryFilter !== 'Todos') {
    filtered = filtered.filter(c => c.region === activeCountryFilter);
  }
  
  // Ordenação: Favoritos primeiro, depois por pontos desc, e nome asc
  filtered.sort((a, b) => {
    if (a.isFavorite && !b.isFavorite) return -1;
    if (!a.isFavorite && b.isFavorite) return 1;
    if (b.points !== a.points) return b.points - a.points;
    return a.portugueseName.localeCompare(b.portugueseName);
  });
  
  // Renderiza HTML
  if (filtered.length === 0) {
    DOM.countriesList.innerHTML = `<div class="no-events-placeholder">Nenhum país encontrado</div>`;
    return;
  }
  
  DOM.countriesList.innerHTML = filtered.map(c => {
    const isPlayingLive = isCountryPlayingLive(c.englishName);
    
    let statusHTML = '';
    if (isPlayingLive) {
      statusHTML = `<span class="status-badge live">Ao vivo</span>`;
    } else if (c.isClassified) {
      statusHTML = `<span class="status-badge classified">Classificado</span>`;
    }
    
    return `
      <div class="list-card" onclick="openCountryMatches('${c.englishName}')">
        <div class="card-left">
          <div class="card-flag-wrapper">${c.emoji}</div>
          <div class="card-info">
            <span class="card-title">${c.portugueseName}</span>
            <span class="card-subtitle">${c.group} • ${c.points} pts</span>
          </div>
        </div>
        <div class="card-right">
          ${statusHTML}
          <button class="favorite-btn ${c.isFavorite ? 'active' : ''}" 
                  onclick="event.stopPropagation(); window.toggleFav('${c.englishName}')">
            ★
          </button>
        </div>
      </div>
    `;
  }).join('');
}

// Helper para descobrir se o time está na zona de classificação (top 2)
function isTeamInQualificationZone(teamName, groupLabel) {
  const groupLetter = groupLabel.replace('Grupo ', '');
  const groupStanding = standingsState[groupLetter];
  if (!groupStanding) return false;
  
  // Encontra o índice da seleção nos standings ordenados
  const index = groupStanding.findIndex(t => t.team === teamName);
  return index >= 0 && index <= 1; // 1º ou 2º lugar
}

// Helper para verificar se a seleção está jogando ao vivo
function isCountryPlayingLive(teamName) {
  return matchesState.some(m => 
    m.status === 'live' && 
    (m.home_team === teamName || m.away_team === teamName)
  );
}

// Abrir lista de jogos de um país específico (redireciona para Jogos do Dia ou foca)
window.openCountryMatches = (countryName) => {
  // Encontra o jogo de "hoje" dessa seleção ou abre a tela de detalhes se tiver jogo ao vivo
  const todayMatch = matchesState.find(m => 
    m.date === '2026-06-14' && 
    (m.home_team === countryName || m.away_team === countryName)
  );
  
  if (todayMatch) {
    openMatchDetail(todayMatch.id);
  } else {
    // Busca qualquer jogo ativo ou último jogo jogado por esse país
    const relevantMatch = matchesState.find(m => m.home_team === countryName || m.away_team === countryName);
    if (relevantMatch) {
      openMatchDetail(relevantMatch.id);
    } else {
      alert(`Nenhum jogo cadastrado para a seleção: ${getTeamInfo(countryName).name}`);
    }
  }
};

window.toggleFav = (countryName) => {
  toggleFavorite(countryName);
};

// TELA 2: Grupos
function renderGroups() {
  if (!DOM.groupsList) return;
  
  let groupsToRender = Object.keys(standingsState).sort();
  
  if (activeGroupFilter !== 'Todos') {
    groupsToRender = [activeGroupFilter];
  }
  
  if (groupsToRender.length === 0 || Object.keys(standingsState).length === 0) {
    DOM.groupsList.innerHTML = `<div class="no-events-placeholder">Carregando grupos...</div>`;
    return;
  }
  
  DOM.groupsList.innerHTML = groupsToRender.map(g => {
    const teams = standingsState[g] || [];
    
    const tableRows = teams.map((t, idx) => {
      const info = getTeamInfo(t.team);
      const dotColor = idx <= 1 ? 'green' : 'gray'; // top 2 classificados
      const isFavorite = favoritesState.has(t.team);
      
      return `
        <tr>
          <td class="col-pos">${idx + 1}</td>
          <td class="col-team" onclick="openCountryMatches('${t.team}')" style="cursor:pointer;">
            <span>${info.emoji}</span>
            <span class="col-team-name" style="${isFavorite ? 'color: #ffb703; font-weight: 600;' : ''}">
              ${info.name}
            </span>
          </td>
          <td class="col-stat">${t.J}</td>
          <td class="col-stat">${t.V}</td>
          <td class="col-pts">${t.P}</td>
          <td style="width: 10px; text-align: right;">
            <span class="status-dot ${dotColor}"></span>
          </td>
        </tr>
      `;
    }).join('');
    
    return `
      <div class="group-section">
        <div class="group-header">
          <span>GRUPO ${g}</span>
          <span style="font-size: 0.6rem; color: var(--color-text-muted);">J  V  P</span>
        </div>
        <table class="group-table">
          <thead>
            <tr style="display:none;">
              <th class="col-pos">#</th>
              <th class="col-team">Time</th>
              <th>J</th>
              <th>V</th>
              <th>P</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            ${tableRows}
          </tbody>
        </table>
      </div>
    `;
  }).join('');
}

// TELA 3: Jogos do Dia
function renderMatches() {
  if (!DOM.matchesList) return;
  
  // Filtra jogos para o dia de simulação ativa (14/06/2026)
  const todayDate = '2026-06-14';
  const todayMatches = matchesState.filter(m => m.date === todayDate);
  
  if (todayMatches.length === 0) {
    DOM.matchesList.innerHTML = `<div class="no-events-placeholder">Nenhum jogo agendado para hoje</div>`;
    return;
  }
  
  // Divide em Ao Vivo e Mais Tarde (incluindo finalizados de hoje)
  const liveMatches = todayMatches.filter(m => m.status === 'live');
  const otherMatches = todayMatches.filter(m => m.status !== 'live');
  
  // Ordena os outros jogos por hora
  otherMatches.sort((a, b) => a.time.localeCompare(b.time));
  
  let html = '';
  
  // Bloco Ao Vivo
  if (liveMatches.length > 0) {
    html += `<div class="section-divider">Ao vivo</div>`;
    html += liveMatches.map(m => renderMatchCard(m, true)).join('');
  }
  
  // Bloco Mais Tarde / Finalizados
  if (otherMatches.length > 0) {
    const hasLive = liveMatches.length > 0;
    html += `<div class="section-divider" style="${hasLive ? 'margin-top:12px;' : ''}">Mais Tarde</div>`;
    html += otherMatches.map(m => renderMatchCard(m, false)).join('');
  }
  
  DOM.matchesList.innerHTML = html;
}

// Helper para renderizar um mini-card de jogo
function renderMatchCard(m, isLive) {
  const homeInfo = getTeamInfo(m.home_team);
  const awayInfo = getTeamInfo(m.away_team);
  const isFavorite = favoritesState.has(m.home_team) || favoritesState.has(m.away_team);
  
  // Placar ou Horário
  let scoreHTML = '';
  let statusBadgeHTML = '';
  
  if (m.status === 'live') {
    const scoreVal = m.score || '0-0';
    scoreHTML = `<span class="match-score">${scoreVal}</span>`;
    
    // Obtém o minuto simulado do relógio global
    const minStr = simulator ? `${simulator.currentMinute}'` : 'Ao vivo';
    statusBadgeHTML = `<span class="match-badge-inline" style="background-color:#ef4444; color:#fff;">${minStr}</span>`;
  } else if (m.status === 'finished') {
    const scoreVal = m.score || '0-0';
    scoreHTML = `<span class="match-score" style="color: var(--color-text-secondary);">${scoreVal}</span>`;
    statusBadgeHTML = `<span class="status-badge time-badge">Fim</span>`;
  } else {
    // Scheduled
    scoreHTML = `<span class="match-score" style="color: var(--color-text-muted); font-size: 0.75rem; font-weight: 500;">${m.time}</span>`;
    statusBadgeHTML = `<span class="status-badge time-badge">Agendado</span>`;
  }
  
  return `
    <div class="list-card match-card" onclick="openMatchDetail(${m.id})">
      <div class="match-card-main">
        <div class="card-left">
          <span class="match-teams">${homeInfo.emoji} ${homeInfo.code} × ${awayInfo.code} ${awayInfo.emoji}</span>
        </div>
        <div class="card-right">
          ${scoreHTML}
          <button class="favorite-btn ${isFavorite ? 'active' : ''}" style="pointer-events: none;">
            ★
          </button>
        </div>
      </div>
      <div class="match-card-meta">
        ${statusBadgeHTML}
        <span style="font-size: 0.6rem; color: var(--color-text-muted);">Grupo ${m.group} • ${m.city}</span>
      </div>
    </div>
  `;
}

// TELA 4: Detalhes do Jogo & Linha do Tempo
function renderMatchDetail(m) {
  if (!DOM.detailScoreCard || !DOM.matchTimeline) return;
  
  const homeInfo = getTeamInfo(m.home_team);
  const awayInfo = getTeamInfo(m.away_team);
  
  // Renders Card superior do placar
  let statusText = 'AGENDADO';
  let badgeClass = 'scheduled';
  
  if (m.status === 'live') {
    const minVal = simulator ? `${simulator.currentMinute}' ` : '';
    statusText = `${minVal}AO VIVO`;
    badgeClass = 'simulated';
  } else if (m.status === 'finished') {
    statusText = 'FINALIZADO';
    badgeClass = '';
  }
  
  const scoreText = m.score !== null ? m.score : '×';
  const scoreClass = m.score !== null ? '' : 'scheduled';
  
  DOM.detailScoreCard.innerHTML = `
    <div class="detail-live-indicator ${badgeClass}">${statusText}</div>
    <div class="detail-teams-row">
      <div class="detail-team-block">
        <span class="detail-flag">${homeInfo.emoji}</span>
        <span class="detail-team-code">${homeInfo.code}</span>
      </div>
      <div class="detail-score-display ${scoreClass}">${scoreText}</div>
      <div class="detail-team-block">
        <span class="detail-flag">${awayInfo.emoji}</span>
        <span class="detail-team-code">${awayInfo.code}</span>
      </div>
    </div>
    <div class="detail-meta-row">
      <div class="detail-meta-badge">Grupo ${m.group}</div>
      <div class="detail-meta-badge location">📍 ${m.city}</div>
    </div>
  `;
  
  // Renders Linha do tempo de Eventos
  let events = [];
  if (m.status === 'finished') {
    // Gera eventos estáticos fictícios se for jogo finalizado do histórico
    events = generateEventsForFinishedMatch(m);
  } else {
    // Jogos ao vivo ou agendados usam a lista dinâmica do simulador
    events = m.events || [];
  }
  
  if (events.length === 0) {
    DOM.matchTimeline.innerHTML = `<div class="no-events-placeholder">Aguardando início da partida</div>`;
    return;
  }
  
  // Renderiza eventos invertidos (mais recentes no topo)
  const sortedEvents = [...events].sort((a, b) => b.minute - a.minute);
  
  DOM.matchTimeline.innerHTML = sortedEvents.map(e => {
    let icon = '⚽';
    let typeClass = 'goal';
    let label = 'Gol!';
    
    if (e.type === 'card_yellow') {
      icon = '🟨';
      typeClass = 'card_yellow';
      label = 'Cartão Amarelo';
    } else if (e.type === 'card_red') {
      icon = '🟥';
      typeClass = 'card_red';
      label = 'Cartão Vermelho';
    }
    
    const teamCode = e.team === 'home' ? homeInfo.code : awayInfo.code;
    const scoreSuff = e.type === 'goal' ? ` (${e.score})` : '';
    
    return `
      <div class="timeline-item ${typeClass}">
        <div class="timeline-dot"></div>
        <div class="timeline-item-meta">
          <span class="timeline-minute">${e.minute}'</span>
          <span class="timeline-event-title">${icon} ${teamCode} - ${label}${scoreSuff}</span>
        </div>
        <span class="timeline-event-desc">${e.player}</span>
      </div>
    `;
  }).join('');
}

// ==========================================================================
// RENDERIZADORES DO PAINEL LATERAL (GLASSMORPHIC)
// ==========================================================================
function renderFavoritesPanel() {
  if (!DOM.favListContainer) return;
  
  if (favoritesState.size === 0) {
    DOM.favListContainer.innerHTML = `<span class="fav-tag-empty">Nenhuma seleção favoritada. Toque na estrela no relógio!</span>`;
    return;
  }
  
  DOM.favListContainer.innerHTML = [...favoritesState].map(fav => {
    const info = getTeamInfo(fav);
    return `
      <div class="fav-tag" onclick="focusOnCountry('${fav}')">
        <span>${info.emoji}</span>
        <span>${info.name}</span>
      </div>
    `;
  }).join('');
}

// Clicar em um favorito no painel lateral foca na tela 1 e busca o país
window.focusOnCountry = (countryName) => {
  navigateToPage(0); // vai para a tela de países
  
  // Limpa filtros e busca pelo nome
  if (DOM.countrySearch) {
    const pName = getTeamInfo(countryName).name;
    DOM.countrySearch.value = pName;
    countrySearchQuery = pName;
    
    // Reseta botões de filtro continental para active = Todos
    DOM.countryFilters.querySelectorAll('.filter-pill').forEach(b => {
      if (b.dataset.filter === 'Todos') b.classList.add('active');
      else b.classList.remove('active');
    });
    activeCountryFilter = 'Todos';
    
    renderCountries();
  }
};

function updateSimulatorPanel() {
  if (!simulator) return;
  
  // Data de hoje formatada
  if (DOM.simDate) DOM.simDate.textContent = '14/06/2026';
  
  // Minuto
  if (DOM.simMinute) {
    DOM.simMinute.textContent = simulator.currentMinute > 0 ? `${simulator.currentMinute}'` : '0\' (Não Iniciado)';
  }
  
  // Status texto
  if (DOM.simStatus) {
    if (simulator.isSimulating) {
      DOM.simStatus.textContent = 'Em Andamento';
      DOM.simStatus.className = 'status-val active';
      DOM.btnStartSim.innerHTML = '<span>⏸</span> Pausar Simulação';
      DOM.btnStartSim.classList.remove('btn-primary');
      DOM.btnStartSim.classList.add('btn-danger');
    } else {
      DOM.simStatus.textContent = simulator.currentMinute === 90 ? 'Finalizado' : 'Pausado';
      DOM.simStatus.className = 'status-val';
      DOM.btnStartSim.innerHTML = '<span>▶</span> Iniciar Simulação';
      DOM.btnStartSim.classList.remove('btn-danger');
      DOM.btnStartSim.classList.add('btn-primary');
    }
  }
  
  // Desabilita iniciar se chegou ao fim (90')
  if (simulator.currentMinute === 90) {
    DOM.btnStartSim.disabled = true;
  } else {
    DOM.btnStartSim.disabled = false;
  }
  
  // Atualiza rótulo de velocidade
  if (DOM.speedIndicator && DOM.simSpeed) {
    const speed = DOM.simSpeed.value;
    DOM.speedIndicator.textContent = `${speed}ms / min`;
  }
}
