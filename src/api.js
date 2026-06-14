import { FALLBACK_MATCHES } from './fallback-matches.js';

const API_PROXY_URL = '/api/matches';
const API_DIRECT_URL = 'https://ai-worldcup26.jd0rwz.easypanel.host/matches';
const API_TOKEN = 'COPA26!';
const LOCAL_STORAGE_KEY = 'copa26_matches_state';

// Busca os jogos da API com estratégias de fallback
export async function fetchMatchesFromAPI() {
  // 1. Tenta usar o proxy local do Vite (desenvolvimento)
  try {
    const response = await fetch(API_PROXY_URL);
    if (response.ok) {
      const data = await response.json();
      console.log('Dados carregados com sucesso através do proxy Vite.');
      return data;
    }
  } catch (error) {
    console.warn('Falha ao buscar via proxy (pode estar em produção ou sem dev server):', error);
  }

  // 2. Tenta fazer requisição direta para a API externa (caso CORS seja permitido ou extensão esteja habilitada)
  try {
    const response = await fetch(API_DIRECT_URL, {
      headers: {
        'X-Token': API_TOKEN
      }
    });
    if (response.ok) {
      const data = await response.json();
      console.log('Dados carregados com sucesso diretamente da API externa.');
      return data;
    }
  } catch (error) {
    console.warn('Falha na requisição direta da API externa (provável restrição de CORS):', error);
  }

  // 3. Fallback final: Usa os dados estáticos locais pré-sincronizados
  console.log('Usando base de dados local de fallback (offline mode).');
  return FALLBACK_MATCHES;
}

// Carrega os jogos (lê do localStorage se houver simulação ativa, senão busca da API)
export async function loadMatches(forceRefresh = false) {
  if (!forceRefresh) {
    const cached = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (cached) {
      try {
        const parsed = JSON.parse(cached);
        if (parsed && parsed.length > 0) {
          console.log('Carregando jogos a partir do estado salvo no localStorage.');
          return parsed;
        }
      } catch (e) {
        console.error('Erro ao ler cache de jogos do localStorage:', e);
      }
    }
  }

  // Se for forceRefresh ou não houver cache local, busca novos dados
  const freshData = await fetchMatchesFromAPI();
  saveMatchesState(freshData);
  return freshData;
}

// Salva o estado atual dos jogos (útil para persistir simulações em tempo real)
export function saveMatchesState(matches) {
  try {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(matches));
  } catch (e) {
    console.error('Erro ao salvar estado de jogos no localStorage:', e);
  }
}

// Reseta o estado para os dados limpos da API
export async function resetMatchesState() {
  localStorage.removeItem(LOCAL_STORAGE_KEY);
  return await loadMatches(true);
}
