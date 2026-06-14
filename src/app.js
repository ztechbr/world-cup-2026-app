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

// Internacionalização (XML)
let translations = {};
let activeLang = 'pt';

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
  
  // Detecta o idioma ativo (?language= ou navegador)
  detectLanguage();
  
  // Carrega o arquivo translate.xml
  await loadTranslations();
  
  // Traduz os elementos estáticos do DOM
  translateStaticElements();
  
  initAutoScaling();
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

// Ajusta a escala do relógio para caber no viewport sem cortar (responsabilidade total)
function initAutoScaling() {
  const adjustScale = () => {
    // Dimensões originais de referência do relógio (incluindo bezel e pulseiras com margem de segurança)
    const originalWidth = 440;  // watch-size (380) + bezel padding (40) + respiros (20)
    const originalHeight = 580; // watch-size (380) + bezel padding (40) + straps (160)
    
    // Calcula fatores de escala horizontais e verticais
    const scaleX = window.innerWidth / originalWidth;
    const scaleY = window.innerHeight / originalHeight;
    
    // O fator de escala final será o menor dos dois, limitado a no máximo 1 (não amplia além do tamanho original)
    const scale = Math.min(1, scaleX, scaleY);
    
    document.documentElement.style.setProperty('--watch-scale', scale);
  };
  
  adjustScale();
  window.addEventListener('resize', adjustScale);
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
// INTERNACIONALIZAÇÃO (XML PARSER & HELPER)
// ==========================================================================

// Detecta o idioma a partir da URL (?language=)
function detectLanguage() {
  const urlParams = new URLSearchParams(window.location.search);
  let lang = urlParams.get('language') || urlParams.get('lang');
  
  if (lang) {
    lang = lang.toLowerCase();
    const supported = ['pt', 'en', 'it', 'es', 'fr'];
    if (supported.includes(lang)) {
      activeLang = lang;
      return;
    }
  }
  
  activeLang = 'en'; // Padrão adotado na ausência ou se inválido
}

// Faz o fetch e parse do dicionário XML translate.xml
async function loadTranslations() {
  try {
    const response = await fetch('./translate.xml');
    if (!response.ok) throw new Error('Falha ao obter translate.xml');
    
    const xmlText = await response.text();
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlText, 'application/xml');
    
    const keys = xmlDoc.getElementsByTagName('key');
    for (let i = 0; i < keys.length; i++) {
      const keyName = keys[i].getAttribute('name');
      translations[keyName] = {};
      
      const langs = ['pt', 'en', 'it', 'es', 'fr'];
      langs.forEach(lang => {
        const node = keys[i].getElementsByTagName(lang)[0];
        translations[keyName][lang] = node ? node.textContent.trim() : '';
      });
    }
    console.log('Dicionário de traduções XML inicializado.');
  } catch (error) {
    console.error('Erro no processamento das traduções:', error);
  }
}

// Retorna o valor traduzido para a chave especificada
function t(key, defaultValue = '') {
  if (translations[key] && translations[key][activeLang]) {
    return translations[key][activeLang];
  }
  return defaultValue || key;
}

// Traduz todos os elementos estáticos do HTML marcado com data-translate
function translateStaticElements() {
  // Traduz conteúdo textual
  document.querySelectorAll('[data-translate]').forEach(el => {
    const key = el.getAttribute('data-translate');
    if (key === 'start_sim' || key === 'reset_day') {
      // Mantém os ícones internos do botão
      const span = el.querySelector('span');
      const text = t(key);
      el.innerHTML = '';
      if (span) el.appendChild(span);
      el.appendChild(document.createTextNode(' ' + text));
    } else {
      el.textContent = t(key, el.textContent);
    }
  });

  // Traduz placeholders de input
  document.querySelectorAll('[data-translate-placeholder]').forEach(el => {
    const key = el.getAttribute('data-translate-placeholder');
    el.placeholder = t(key, el.placeholder);
  });
}

// Retorna a palavra "Grupo" traduzida amigavelmente
function getGroupTranslation() {
  return activeLang === 'en' ? 'Group' :
         activeLang === 'it' ? 'Gruppo' :
         activeLang === 'fr' ? 'Groupe' : 'Grupo';
}

// ==========================================================================
// SINCRONIZAÇÃO E CONTROLE DA API
// ==========================================================================
async function syncData(force = false) {
  setApiStatus('pending', t('api_syncing', 'Sincronizando dados...'));
  try {
    matchesState = await loadMatches(force);
    standingsState = calculateStandings(matchesState);
    
    const count = matchesState.length;
    const isOffline = matchesState === apiOfflineFallback();
    
    if (isOffline) {
      setApiStatus('offline', `${t('api_sync_error', 'Offline')} (${count})`);
    } else {
      const connText = activeLang === 'en' ? 'Connected' : activeLang === 'it' ? 'Connesso' : activeLang === 'es' ? 'Conectado' : activeLang === 'fr' ? 'Connecté' : 'Conectado';
      setApiStatus('online', `${connText} - API (${count})`);
    }
  } catch (error) {
    console.error('Erro na sincronização:', error);
    setApiStatus('offline', t('api_sync_error', 'Erro. Usando cache local.'));
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
      const resetMsg = activeLang === 'en' ? 'Reset today\'s simulation? Scores and events will be lost.' :
                        activeLang === 'it' ? 'Ripristinare la simulazione? Risultati e eventi andranno persi.' :
                        activeLang === 'es' ? '¿Reiniciar simulación? Marcadores y eventos se perderán.' :
                        activeLang === 'fr' ? 'Réinitialiser la simulation? Les scores et événements seront perdus.' :
                        'Deseja reiniciar a simulação do dia? Os placares e eventos serão resetados.';
                        
      if (confirm(resetMsg)) {
        setApiStatus('pending', t('api_syncing', 'Resetando estado...'));
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
      const syncMsg = activeLang === 'en' ? 'This will delete the simulation and sync fresh data from the API. Proceed?' :
                      activeLang === 'it' ? 'Questo cancellerà la simulazione e sincronizzerà i dati dall\'API. Procedere?' :
                      activeLang === 'es' ? 'Esto borrará la simulación y sincronizará datos de la API. ¿Proceder?' :
                      activeLang === 'fr' ? 'Cela supprimera la simulation et synchronisera les données API. Procéder?' :
                      'Isso irá apagar a simulação em andamento e sincronizar dados atualizados da API externa. Deseja prosseguir?';
                      
      if (confirm(syncMsg)) {
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
    
    if (Math.abs(diffX) < Math.abs(diffY)) return;
    if (DOM.matchDetailView.classList.contains('active')) return;
    
    const minSwipeDist = 50; // pixels
    if (Math.abs(diffX) > minSwipeDist) {
      if (diffX < 0) {
        const nextPage = Math.min(currentPage + 1, 2);
        navigateToPage(nextPage);
      } else {
        const prevPage = Math.max(currentPage - 1, 0);
        navigateToPage(prevPage);
      }
    }
  }
}

function navigateToPage(pageIndex) {
  currentPage = pageIndex;
  
  if (DOM.carouselViewport) {
    DOM.carouselViewport.style.transform = `translateX(-${currentPage * 100}%)`;
  }
  
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
  
  const groupWord = getGroupTranslation();
  
  const countriesData = Object.keys(TEAM_MAP).map(englishName => {
    const info = getTeamInfo(englishName);
    const stats = getCountryStats(englishName, standingsState);
    const isFavorite = favoritesState.has(englishName);
    
    return {
      englishName,
      translatedName: t(englishName, info.name),
      emoji: info.emoji,
      region: info.region,
      group: stats.group,
      points: stats.points,
      isFavorite,
      isClassified: stats.games >= 3 && isTeamInQualificationZone(englishName, stats.group)
    };
  });
  
  let filtered = countriesData;
  if (countrySearchQuery.trim() !== '') {
    const q = countrySearchQuery.toLowerCase();
    filtered = filtered.filter(c => 
      c.translatedName.toLowerCase().includes(q) || 
      c.englishName.toLowerCase().includes(q)
    );
  }
  
  if (activeCountryFilter !== 'Todos') {
    filtered = filtered.filter(c => c.region === activeCountryFilter);
  }
  
  filtered.sort((a, b) => {
    if (a.isFavorite && !b.isFavorite) return -1;
    if (!a.isFavorite && b.isFavorite) return 1;
    if (b.points !== a.points) return b.points - a.points;
    return a.translatedName.localeCompare(b.translatedName);
  });
  
  if (filtered.length === 0) {
    DOM.countriesList.innerHTML = `<div class="no-events-placeholder">${t('no_country_found', 'Nenhum país encontrado')}</div>`;
    return;
  }
  
  DOM.countriesList.innerHTML = filtered.map(c => {
    const isPlayingLive = isCountryPlayingLive(c.englishName);
    const groupLabel = c.group.replace('Grupo', groupWord);
    
    let statusHTML = '';
    if (isPlayingLive) {
      statusHTML = `<span class="status-badge live">${t('live_badge', 'Ao vivo')}</span>`;
    } else if (c.isClassified) {
      statusHTML = `<span class="status-badge classified">${t('classified_badge', 'Classificado')}</span>`;
    }
    
    return `
      <div class="list-card" onclick="openCountryMatches('${c.englishName}')">
        <div class="card-left">
          <div class="card-flag-wrapper">${c.emoji}</div>
          <div class="card-info">
            <span class="card-title">${c.translatedName}</span>
            <span class="card-subtitle">${groupLabel} • ${c.points} pts</span>
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

function isTeamInQualificationZone(teamName, groupLabel) {
  const groupLetter = groupLabel.replace('Grupo ', '');
  const groupStanding = standingsState[groupLetter];
  if (!groupStanding) return false;
  
  const index = groupStanding.findIndex(t => t.team === teamName);
  return index >= 0 && index <= 1; // 1º ou 2º lugar
}

function isCountryPlayingLive(teamName) {
  return matchesState.some(m => 
    m.status === 'live' && 
    (m.home_team === teamName || m.away_team === teamName)
  );
}

window.openCountryMatches = (countryName) => {
  const todayMatch = matchesState.find(m => 
    m.date === '2026-06-14' && 
    (m.home_team === countryName || m.away_team === countryName)
  );
  
  if (todayMatch) {
    openMatchDetail(todayMatch.id);
  } else {
    const relevantMatch = matchesState.find(m => m.home_team === countryName || m.away_team === countryName);
    if (relevantMatch) {
      openMatchDetail(relevantMatch.id);
    } else {
      const alertMsg = activeLang === 'en' ? 'No matches scheduled for ' :
                       activeLang === 'it' ? 'Nessuna partita per ' :
                       activeLang === 'es' ? 'Sin partidos programados para ' :
                       activeLang === 'fr' ? 'Aucun match programmé pour ' :
                       'Nenhum jogo cadastrado para a seleção: ';
      alert(`${alertMsg}${t(countryName, getTeamInfo(countryName).name)}`);
    }
  }
};

window.toggleFav = (countryName) => {
  toggleFavorite(countryName);
};

// TELA 2: Grupos
function renderGroups() {
  if (!DOM.groupsList) return;
  
  const groupWord = getGroupTranslation();
  let groupsToRender = Object.keys(standingsState).sort();
  
  if (activeGroupFilter !== 'Todos') {
    groupsToRender = [activeGroupFilter];
  }
  
  if (groupsToRender.length === 0 || Object.keys(standingsState).length === 0) {
    DOM.groupsList.innerHTML = `<div class="no-events-placeholder">${t('groups_title', 'Carregando grupos...')}</div>`;
    return;
  }
  
  DOM.groupsList.innerHTML = groupsToRender.map(g => {
    const teams = standingsState[g] || [];
    
    const tableRows = teams.map((st, idx) => {
      const info = getTeamInfo(st.team);
      const dotColor = idx <= 1 ? 'green' : 'gray'; 
      const isFavorite = favoritesState.has(st.team);
      const translatedTeamName = t(st.team, info.name);
      
      return `
        <tr>
          <td class="col-pos">${idx + 1}</td>
          <td class="col-team" onclick="openCountryMatches('${st.team}')" style="cursor:pointer;">
            <span>${info.emoji}</span>
            <span class="col-team-name" style="${isFavorite ? 'color: #ffb703; font-weight: 600;' : ''}">
              ${translatedTeamName}
            </span>
          </td>
          <td class="col-stat">${st.J}</td>
          <td class="col-stat">${st.V}</td>
          <td class="col-pts">${st.P}</td>
          <td style="width: 10px; text-align: right;">
            <span class="status-dot ${dotColor}"></span>
          </td>
        </tr>
      `;
    }).join('');
    
    return `
      <div class="group-section">
        <div class="group-header">
          <span>${groupWord.toUpperCase()} ${g}</span>
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
  
  const todayDate = '2026-06-14';
  const todayMatches = matchesState.filter(m => m.date === todayDate);
  
  if (todayMatches.length === 0) {
    DOM.matchesList.innerHTML = `<div class="no-events-placeholder">${t('no_match_today', 'Nenhum jogo agendado para hoje')}</div>`;
    return;
  }
  
  const liveMatches = todayMatches.filter(m => m.status === 'live');
  const otherMatches = todayMatches.filter(m => m.status !== 'live');
  
  otherMatches.sort((a, b) => a.time.localeCompare(b.time));
  
  let html = '';
  
  if (liveMatches.length > 0) {
    html += `<div class="section-divider">${t('live_badge', 'Ao vivo')}</div>`;
    html += liveMatches.map(m => renderMatchCard(m, true)).join('');
  }
  
  if (otherMatches.length > 0) {
    const hasLive = liveMatches.length > 0;
    html += `<div class="section-divider" style="${hasLive ? 'margin-top:12px;' : ''}">${t('later_section', 'Mais Tarde')}</div>`;
    html += otherMatches.map(m => renderMatchCard(m, false)).join('');
  }
  
  DOM.matchesList.innerHTML = html;
}

function renderMatchCard(m, isLive) {
  const homeInfo = getTeamInfo(m.home_team);
  const awayInfo = getTeamInfo(m.away_team);
  const isFavorite = favoritesState.has(m.home_team) || favoritesState.has(m.away_team);
  const groupWord = getGroupTranslation();
  
  let scoreHTML = '';
  let statusBadgeHTML = '';
  
  if (m.status === 'live') {
    const scoreVal = m.score || '0-0';
    scoreHTML = `<span class="match-score">${scoreVal}</span>`;
    const minStr = simulator ? `${simulator.currentMinute}'` : t('live_badge');
    statusBadgeHTML = `<span class="match-badge-inline" style="background-color:#ef4444; color:#fff;">${minStr}</span>`;
  } else if (m.status === 'finished') {
    const scoreVal = m.score || '0-0';
    scoreHTML = `<span class="match-score" style="color: var(--color-text-secondary);">${scoreVal}</span>`;
    statusBadgeHTML = `<span class="status-badge time-badge">${t('end_badge', 'Fim')}</span>`;
  } else {
    scoreHTML = `<span class="match-score" style="color: var(--color-text-muted); font-size: 0.75rem; font-weight: 500;">${m.time}</span>`;
    statusBadgeHTML = `<span class="status-badge time-badge">${t('scheduled_badge', 'Agendado')}</span>`;
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
        <span style="font-size: 0.6rem; color: var(--color-text-muted);">${groupWord} ${m.group} • ${m.city}</span>
      </div>
    </div>
  `;
}

// TELA 4: Detalhes do Jogo & Linha do Tempo
function renderMatchDetail(m) {
  if (!DOM.detailScoreCard || !DOM.matchTimeline) return;
  
  const homeInfo = getTeamInfo(m.home_team);
  const awayInfo = getTeamInfo(m.away_team);
  const groupWord = getGroupTranslation();
  
  let statusText = t('scheduled_badge').toUpperCase();
  let badgeClass = 'scheduled';
  
  if (m.status === 'live') {
    const minVal = simulator ? `${simulator.currentMinute}' ` : '';
    statusText = `${minVal}${t('live_badge').toUpperCase()}`;
    badgeClass = 'simulated';
  } else if (m.status === 'finished') {
    statusText = t('end_badge').toUpperCase();
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
      <div class="detail-meta-badge">${groupWord} ${m.group}</div>
      <div class="detail-meta-badge location">📍 ${m.city}</div>
    </div>
  `;
  
  let events = [];
  if (m.status === 'finished') {
    events = generateEventsForFinishedMatch(m);
  } else {
    events = m.events || [];
  }
  
  if (events.length === 0) {
    DOM.matchTimeline.innerHTML = `<div class="no-events-placeholder">${t('waiting_match', 'Aguardando início da partida')}</div>`;
    return;
  }
  
  const sortedEvents = [...events].sort((a, b) => b.minute - a.minute);
  
  DOM.matchTimeline.innerHTML = sortedEvents.map(e => {
    let icon = '⚽';
    let typeClass = 'goal';
    let label = t('goal_label', 'Gol!');
    
    if (e.type === 'card_yellow') {
      icon = '🟨';
      typeClass = 'card_yellow';
      label = t('card_yellow', 'Cartão Amarelo');
    } else if (e.type === 'card_red') {
      icon = '🟥';
      typeClass = 'card_red';
      label = t('card_red', 'Cartão Vermelho');
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
    DOM.favListContainer.innerHTML = `<span class="fav-tag-empty">${t('no_favorites')}</span>`;
    return;
  }
  
  DOM.favListContainer.innerHTML = [...favoritesState].map(fav => {
    const info = getTeamInfo(fav);
    const translatedName = t(fav, info.name);
    return `
      <div class="fav-tag" onclick="focusOnCountry('${fav}')">
        <span>${info.emoji}</span>
        <span>${translatedName}</span>
      </div>
    `;
  }).join('');
}

// Clicar em um favorito no painel lateral foca na tela 1 e busca o país
window.focusOnCountry = (countryName) => {
  navigateToPage(0); // vai para a tela de países
  
  if (DOM.countrySearch) {
    const pName = t(countryName, getTeamInfo(countryName).name);
    DOM.countrySearch.value = pName;
    countrySearchQuery = pName;
    
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
    const notStartedWord = activeLang === 'en' ? 'Not Started' :
                          activeLang === 'it' ? 'Non Iniziato' :
                          activeLang === 'es' ? 'No Iniciado' :
                          activeLang === 'fr' ? 'Pas Commencé' :
                          'Não Iniciado';
    DOM.simMinute.textContent = simulator.currentMinute > 0 ? `${simulator.currentMinute}'` : `0' (${notStartedWord})`;
  }
  
  // Status texto
  if (DOM.simStatus) {
    if (simulator.isSimulating) {
      const inProgressWord = activeLang === 'en' ? 'In Progress' :
                            activeLang === 'it' ? 'In Corso' :
                            activeLang === 'es' ? 'En Progreso' :
                            activeLang === 'fr' ? 'En Cours' :
                            'Em Andamento';
      DOM.simStatus.textContent = inProgressWord;
      DOM.simStatus.className = 'status-val active';
      DOM.btnStartSim.innerHTML = `<span>⏸</span> ${t('pause_sim')}`;
      DOM.btnStartSim.classList.remove('btn-primary');
      DOM.btnStartSim.classList.add('btn-danger');
    } else {
      const pausedWord = activeLang === 'en' ? 'Paused' :
                         activeLang === 'it' ? 'In Pausa' :
                         activeLang === 'es' ? 'Pausado' :
                         activeLang === 'fr' ? 'En Pause' :
                         'Pausado';
      DOM.simStatus.textContent = simulator.currentMinute === 90 ? t('end_badge').toUpperCase() : pausedWord;
      DOM.simStatus.className = 'status-val';
      DOM.btnStartSim.innerHTML = `<span>▶</span> ${t('start_sim')}`;
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
