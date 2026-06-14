// Mapeamento completo das 48 seleções da Copa do Mundo 2026
// Contém: Tradução para o português, flag emoji, confederação/região e código de 3 letras
export const TEAM_MAP = {
  'Algeria': { name: 'Argélia', emoji: '🇩🇿', code: 'ALG', region: 'África' },
  'Argentina': { name: 'Argentina', emoji: '🇦🇷', code: 'ARG', region: 'Sul-Am.' },
  'Australia': { name: 'Austrália', emoji: '🇦🇺', code: 'AUS', region: 'Ásia' },
  'Austria': { name: 'Áustria', emoji: '🇦🇹', code: 'AUT', region: 'Europa' },
  'Belgium': { name: 'Bélgica', emoji: '🇧🇪', code: 'BEL', region: 'Europa' },
  'Bosnia and Herzegovina': { name: 'Bósnia e Herz.', emoji: '🇧🇦', code: 'BIH', region: 'Europa' },
  'Brazil': { name: 'Brasil', emoji: '🇧🇷', code: 'BRA', region: 'Sul-Am.' },
  'Canada': { name: 'Canadá', emoji: '🇨🇦', code: 'CAN', region: 'Caribe/C' },
  'Cape Verde': { name: 'Cabo Verde', emoji: '🇨🇻', code: 'CPV', region: 'África' },
  'Colombia': { name: 'Colômbia', emoji: '🇨🇴', code: 'COL', region: 'Sul-Am.' },
  'Croatia': { name: 'Croácia', emoji: '🇭🇷', code: 'CRO', region: 'Europa' },
  'Curaçao': { name: 'Curaçao', emoji: '🇨🇼', code: 'CUW', region: 'Caribe/C' },
  'Czech Republic': { name: 'Rep. Tcheca', emoji: '🇨🇿', code: 'CZE', region: 'Europa' },
  'DR Congo': { name: 'RD Congo', emoji: '🇨🇩', code: 'COD', region: 'África' },
  'Ecuador': { name: 'Equador', emoji: '🇪🇨', code: 'ECU', region: 'Sul-Am.' },
  'Egypt': { name: 'Egito', emoji: '🇪🇬', code: 'EGY', region: 'África' },
  'England': { name: 'Inglaterra', emoji: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', code: 'ENG', region: 'Europa' },
  'France': { name: 'França', emoji: '🇫🇷', code: 'FRA', region: 'Europa' },
  'Germany': { name: 'Alemanha', emoji: '🇩🇪', code: 'GER', region: 'Europa' },
  'Ghana': { name: 'Gana', emoji: '🇬🇭', code: 'GHA', region: 'África' },
  'Haiti': { name: 'Haiti', emoji: '🇭🇹', code: 'HAI', region: 'Caribe/C' },
  'Iran': { name: 'Irã', emoji: '🇮🇷', code: 'IRN', region: 'Ásia' },
  'Iraq': { name: 'Iraque', emoji: '🇮🇶', code: 'IRQ', region: 'Ásia' },
  'Ivory Coast': { name: 'Costa do Marfim', emoji: '🇨🇮', code: 'CIV', region: 'África' },
  'Japan': { name: 'Japão', emoji: '🇯🇵', code: 'JPN', region: 'Ásia' },
  'Jordan': { name: 'Jordânia', emoji: '🇯🇴', code: 'JOR', region: 'Ásia' },
  'Mexico': { name: 'México', emoji: '🇲🇽', code: 'MEX', region: 'Caribe/C' },
  'Morocco': { name: 'Marrocos', emoji: '🇲🇦', code: 'MAR', region: 'África' },
  'Netherlands': { name: 'Holanda', emoji: '🇳🇱', code: 'NED', region: 'Europa' },
  'New Zealand': { name: 'Nova Zelândia', emoji: '🇳🇿', code: 'NZL', region: 'Oceania' },
  'Norway': { name: 'Noruega', emoji: '🇳🇴', code: 'NOR', region: 'Europa' },
  'Panama': { name: 'Panamá', emoji: '🇵🇦', code: 'PAN', region: 'Caribe/C' },
  'Paraguay': { name: 'Paraguai', emoji: '🇵🇾', code: 'PAR', region: 'Sul-Am.' },
  'Portugal': { name: 'Portugal', emoji: '🇵🇹', code: 'POR', region: 'Europa' },
  'Qatar': { name: 'Catar', emoji: '🇶🇦', code: 'QAT', region: 'Ásia' },
  'Saudi Arabia': { name: 'Arábia Saudita', emoji: '🇸🇦', code: 'KSA', region: 'Ásia' },
  'Scotland': { name: 'Escócia', emoji: '🏴󠁧󠁢󠁳󠁣󠁴󠁿', code: 'SCO', region: 'Europa' },
  'Senegal': { name: 'Senegal', emoji: '🇸🇳', code: 'SEN', region: 'África' },
  'South Africa': { name: 'África do Sul', emoji: '🇿🇦', code: 'RSA', region: 'África' },
  'South Korea': { name: 'Coreia do Sul', emoji: '🇰🇷', code: 'KOR', region: 'Ásia' },
  'Spain': { name: 'Espanha', emoji: '🇪🇸', code: 'ESP', region: 'Europa' },
  'Sweden': { name: 'Suécia', emoji: '🇸🇪', code: 'SWE', region: 'Europa' },
  'Switzerland': { name: 'Suíça', emoji: '🇨🇭', code: 'SUI', region: 'Europa' },
  'Tunisia': { name: 'Tunísia', emoji: '🇹🇳', code: 'TUN', region: 'África' },
  'Turkey': { name: 'Turquia', emoji: '🇹🇷', code: 'TUR', region: 'Europa' },
  'Uruguay': { name: 'Uruguai', emoji: '🇺🇾', code: 'URU', region: 'Sul-Am.' },
  'USA': { name: 'EUA', emoji: '🇺🇸', code: 'USA', region: 'Caribe/C' },
  'Uzbekistan': { name: 'Uzbequistão', emoji: '🇺🇿', code: 'UZB', region: 'Ásia' }
};

// Retorna dados amigáveis de uma seleção
export function getTeamInfo(englishName) {
  return TEAM_MAP[englishName] || {
    name: englishName,
    emoji: '🏳️',
    code: englishName.slice(0, 3).toUpperCase(),
    region: 'Outros'
  };
}

// Calcula dinamicamente a classificação dos grupos com base nos jogos
export function calculateStandings(matches) {
  const standings = {};

  // Inicializa estrutura para cada grupo encontrado
  matches.forEach(match => {
    // Apenas partidas da fase de grupos possuem letras simples (A, B, C... L)
    const groupName = match.group;
    if (!groupName || groupName.length > 1) return; // ignora mata-mata

    if (!standings[groupName]) {
      standings[groupName] = {};
    }

    const initTeam = (team) => {
      if (!standings[groupName][team]) {
        standings[groupName][team] = {
          team,
          J: 0,
          V: 0,
          E: 0,
          D: 0,
          GP: 0,
          GC: 0,
          SG: 0,
          P: 0
        };
      }
    };

    initTeam(match.home_team);
    initTeam(match.away_team);

    // Se o jogo terminou ou está ao vivo (e tem placar), processa os pontos
    if ((match.status === 'finished' || match.status === 'live') && match.score) {
      const scores = match.score.split('-').map(Number);
      if (scores.length === 2 && !isNaN(scores[0]) && !isNaN(scores[1])) {
        const homeScore = scores[0];
        const awayScore = scores[1];

        // Atualiza jogos jogados
        standings[groupName][match.home_team].J += 1;
        standings[groupName][match.away_team].J += 1;

        // Gols Pró e Contra
        standings[groupName][match.home_team].GP += homeScore;
        standings[groupName][match.home_team].GC += awayScore;
        standings[groupName][match.away_team].GP += awayScore;
        standings[groupName][match.away_team].GC += homeScore;

        // Resultado
        if (homeScore > awayScore) {
          standings[groupName][match.home_team].V += 1;
          standings[groupName][match.home_team].P += 3;
          standings[groupName][match.away_team].D += 1;
        } else if (homeScore < awayScore) {
          standings[groupName][match.away_team].V += 1;
          standings[groupName][match.away_team].P += 3;
          standings[groupName][match.home_team].D += 1;
        } else {
          standings[groupName][match.home_team].E += 1;
          standings[groupName][match.home_team].P += 1;
          standings[groupName][match.away_team].E += 1;
          standings[groupName][match.away_team].P += 1;
        }

        // Saldo de Gols
        standings[groupName][match.home_team].SG = standings[groupName][match.home_team].GP - standings[groupName][match.home_team].GC;
        standings[groupName][match.away_team].SG = standings[groupName][match.away_team].GP - standings[groupName][match.away_team].GC;
      }
    }
  });

  // Ordena e formata cada grupo como array
  const sortedStandings = {};
  Object.keys(standings).forEach(groupName => {
    const teamsArray = Object.values(standings[groupName]);
    teamsArray.sort((a, b) => {
      if (b.P !== a.P) return b.P - a.P;         // Pontos
      if (b.SG !== a.SG) return b.SG - a.SG;     // Saldo de gols
      if (b.GP !== a.GP) return b.GP - a.GP;     // Gols marcados
      if (b.V !== a.V) return b.V - a.V;         // Vitórias
      return a.team.localeCompare(b.team);       // Nome do time
    });
    sortedStandings[groupName] = teamsArray;
  });

  return sortedStandings;
}

// Retorna os pontos acumulados e a fase/grupo de um país específico
export function getCountryStats(countryName, standings) {
  let foundGroup = null;
  let foundStats = null;

  for (const groupName of Object.keys(standings)) {
    const stats = standings[groupName].find(t => t.team === countryName);
    if (stats) {
      foundGroup = `Grupo ${groupName}`;
      foundStats = stats;
      break;
    }
  }

  // Se o país não foi encontrado nos grupos (pode ser mata-mata apenas, o que é raro na fase inicial)
  return {
    group: foundGroup || 'N/A',
    points: foundStats ? foundStats.P : 0,
    games: foundStats ? foundStats.J : 0,
    wins: foundStats ? foundStats.V : 0,
    qualified: false // Calculado dinamicamente no app.js com base na posição
  };
}
