import { TEAM_MAP } from './utils.js';

// Lista de principais jogadores por seleção para simulações realistas
const PLAYER_ROSTERS = {
  'Brazil': ['Vini Jr.', 'Rodrygo', 'Neymar', 'Raphinha', 'Bruno Guimarães', 'Lucas Paquetá', 'Marquinhos', 'Casemiro', 'Gabriel Magalhães'],
  'Argentina': ['Lionel Messi', 'Lautaro Martínez', 'Julián Álvarez', 'Enzo Fernández', 'Rodrigo De Paul', 'Alexis Mac Allister', 'Ángel Di María', 'Otamendi'],
  'Germany': ['Jamal Musiala', 'Florian Wirtz', 'Kai Havertz', 'Thomas Müller', 'İlkay Gündoğan', 'Leroy Sané', 'Joshua Kimmich', 'Toni Kroos'],
  'France': ['Kylian Mbappé', 'Antoine Griezmann', 'Ousmane Dembélé', 'Olivier Giroud', 'Eduardo Camavinga', 'Aurélien Tchouaméni', 'William Saliba'],
  'Netherlands': ['Memphis Depay', 'Cody Gakpo', 'Xavi Simons', 'Frenkie de Jong', 'Virgil van Dijk', 'Matthijs de Ligt', 'Denzel Dumfries'],
  'Spain': ['Lamine Yamal', 'Nico Williams', 'Álvaro Morata', 'Pedri', 'Gavi', 'Rodri', 'Dani Carvajal', 'Dani Olmo'],
  'Portugal': ['Cristiano Ronaldo', 'Bruno Fernandes', 'Bernardo Silva', 'Rafael Leão', 'João Félix', 'Diogo Jota', 'Rúben Dias'],
  'England': ['Harry Kane', 'Jude Bellingham', 'Bukayo Saka', 'Phil Foden', 'Declan Rice', 'John Stones', 'Marcus Rashford', 'Kyle Walker'],
  'Mexico': ['Santiago Giménez', 'Hirving Lozano', 'Edson Álvarez', 'Uriel Antuna', 'Luis Chávez', 'Guillermo Ochoa'],
  'USA': ['Christian Pulisic', 'Timothy Weah', 'Weston McKennie', 'Gio Reyna', 'Folarin Balogun', 'Tyler Adams'],
  'Canada': ['Alphonso Davies', 'Jonathan David', 'Cyle Larin', 'Tajon Buchanan', 'Stephen Eustáquio'],
  'Curaçao': ['Juninho Bacuna', 'Leandro Bacuna', 'Gervane Kastaneer', 'Rangelo Janga'],
  'Ivory Coast': ['Sébastien Haller', 'Franck Kessié', 'Simon Adingra', 'Oumar Diakité', 'Seko Fofana'],
  'Ecuador': ['Enner Valencia', 'Moises Caicedo', 'Piero Hincapié', 'Kendry Páez', 'Pervis Estupiñán'],
  'Japan': ['Kaoru Mitoma', 'Takefusa Kubo', 'Wataru Endo', 'Ritsu Doan', 'Takumi Minamino', 'Ayase Ueda'],
  'Sweden': ['Viktor Gyökeres', 'Alexander Isak', 'Dejan Kulusevski', 'Emil Forsberg', 'Victor Lindelöf'],
  'Tunisia': ['Youssef Msakni', 'Montassar Talbi', 'Aissa Laidouni', 'Ellyes Skhiri']
};

// Sobrenomes comuns por região para gerar jogadores genéricos caso a seleção não esteja mapeada
const REGIONAL_NAMES = {
  'África': ['Keita', 'Mensah', 'Traoré', 'Diallo', 'Touré', 'Sow', 'Diop', 'Bamba', 'Kone', 'Okeke'],
  'Ásia': ['Kim', 'Lee', 'Park', 'Tanaka', 'Sato', 'Nguyen', 'Al-Dawsari', 'Al-Ghamdi', 'Chen', 'Wang'],
  'Europa': ['Smith', 'Müller', 'Dupont', 'Rossi', 'Silva', 'Hansen', 'Novak', 'Andersson', 'Ivanov', 'Gruber'],
  'Sul-Am.': ['Gomez', 'Rodriguez', 'Fernandez', 'Lopez', 'Diaz', 'Martinez', 'Sanchez', 'Perez', 'Silva', 'Torres'],
  'Caribe/C': ['Smith', 'Johnson', 'Hernandez', 'Gonzalez', 'Flores', 'Martinez', 'Davies', 'Larin', 'Richards'],
  'Oceania': ['Smith', 'Williams', 'Brown', 'Taylor', 'Jones', 'Wood', 'Tuilagi', 'Singh', 'Tuivasa']
};

function getRandomPlayer(teamName) {
  const roster = PLAYER_ROSTERS[teamName];
  if (roster && roster.length > 0) {
    return roster[Math.floor(Math.random() * roster.length)];
  }

  // Gera nome genérico baseado na confederação/região do país
  const teamInfo = TEAM_MAP[teamName];
  const region = teamInfo ? teamInfo.region : 'Europa';
  const namesList = REGIONAL_NAMES[region] || REGIONAL_NAMES['Europa'];
  const lastName = namesList[Math.floor(Math.random() * namesList.length)];
  const shirtNumber = Math.floor(Math.random() * 18) + 2;

  return `${lastName} (Nº ${shirtNumber})`;
}

// Gera uma linha do tempo estática de eventos para jogos terminados
export function generateEventsForFinishedMatch(match) {
  if (match.events && match.events.length > 0) return match.events;

  const events = [];
  if (!match.score || match.status !== 'finished') return [];

  const scores = match.score.split('-').map(Number);
  if (scores.length !== 2 || isNaN(scores[0]) || isNaN(scores[1])) return [];

  const homeGoals = scores[0];
  const awayGoals = scores[1];

  let currentHome = 0;
  let currentAway = 0;

  // Gerar minutos únicos para os gols e ordenar
  const goalMinutes = [];
  const totalGoals = homeGoals + awayGoals;
  while (goalMinutes.length < totalGoals) {
    const min = Math.floor(Math.random() * 88) + 2; // entre 2' e 89'
    if (!goalMinutes.some(g => g.minute === min)) {
      // decide de quem é o gol baseado na quantidade restante
      const isHome = goalMinutes.filter(g => g.isHome).length < homeGoals;
      goalMinutes.push({ minute: min, isHome });
    }
  }

  // Ordena os minutos dos gols
  goalMinutes.sort((a, b) => a.minute - b.minute);

  // Adiciona os gols aos eventos
  goalMinutes.forEach(goal => {
    if (goal.isHome) {
      currentHome++;
    } else {
      currentAway++;
    }

    const teamScored = goal.isHome ? match.home_team : match.away_team;
    const scorer = getRandomPlayer(teamScored);

    events.push({
      minute: goal.minute,
      type: 'goal',
      team: goal.isHome ? 'home' : 'away',
      player: scorer,
      score: `${currentHome}-${currentAway}`,
      description: `Gol! ${scorer}`
    });
  });

  // Adiciona alguns cartões aleatórios
  const totalCards = Math.floor(Math.random() * 4) + 1; // 1 a 4 cartões
  for (let i = 0; i < totalCards; i++) {
    const cardMin = Math.floor(Math.random() * 89) + 1;
    const isHome = Math.random() > 0.5;
    const team = isHome ? match.home_team : match.away_team;
    const player = getRandomPlayer(team);
    const isRed = Math.random() > 0.85; // 15% de chance de ser vermelho

    events.push({
      minute: cardMin,
      type: isRed ? 'card_red' : 'card_yellow',
      team: isHome ? 'home' : 'away',
      player: player,
      description: isRed ? `Cartão Vermelho direto!` : `Cartão Amarelo`
    });
  }

  // Ordena todos os eventos pelo minuto
  events.sort((a, b) => a.minute - b.minute);
  match.events = events;
  return events;
}

// Classe que gerencia a simulação em tempo real dos jogos de "hoje"
export class MatchSimulator {
  constructor(matches, onUpdateCallback) {
    this.allMatches = matches;
    this.onUpdate = onUpdateCallback;
    this.timerId = null;
    this.currentMinute = 0;
    this.speedMs = 500; // velocidade padrão: 500ms por minuto simulado
    this.isSimulating = false;
    this.todayMatches = [];
  }

  // Inicializa os jogos de hoje para simulação
  initTodayMatches(targetDate = '2026-06-14') {
    this.todayMatches = this.allMatches.filter(m => m.date === targetDate);
    
    // Se nenhum estiver em simulação, reseta para iniciar
    const hasLive = this.todayMatches.some(m => m.status === 'live');
    const hasFinished = this.todayMatches.every(m => m.status === 'finished');
    
    if (!hasLive || hasFinished) {
      this.currentMinute = 0;
      this.todayMatches.forEach(m => {
        m.status = 'scheduled';
        m.score = null;
        m.events = [];
      });
    } else {
      // Se já houver jogo live, descobre o minuto atual com base nos eventos existentes
      let maxMin = 0;
      this.todayMatches.forEach(m => {
        if (m.events) {
          m.events.forEach(e => {
            if (e.minute > maxMin) maxMin = e.minute;
          });
        }
      });
      this.currentMinute = maxMin > 0 ? maxMin : 1;
    }
  }

  // Define a velocidade da simulação (ms por minuto simulado)
  setSpeed(ms) {
    this.speedMs = ms;
    if (this.isSimulating) {
      this.stop();
      this.start();
    }
  }

  // Inicia ou retoma a simulação
  start() {
    if (this.isSimulating) return;
    this.isSimulating = true;

    // Se começou do zero, marca jogos de hoje como "live" com placar 0-0
    if (this.currentMinute === 0) {
      this.currentMinute = 1;
      this.todayMatches.forEach(m => {
        m.status = 'live';
        m.score = '0-0';
        m.events = [];
      });
      if (this.onUpdate) this.onUpdate(this.allMatches);
    }

    this.timerId = setInterval(() => {
      this.tick();
    }, this.speedMs);
  }

  // Pausa a simulação
  stop() {
    if (this.timerId) {
      clearInterval(this.timerId);
      this.timerId = null;
    }
    this.isSimulating = false;
  }

  // Avança 1 minuto simulado
  tick() {
    if (this.currentMinute >= 90) {
      this.stop();
      this.currentMinute = 90;
      // Finaliza todos os jogos de hoje
      this.todayMatches.forEach(m => {
        m.status = 'finished';
      });
      if (this.onUpdate) this.onUpdate(this.allMatches);
      return;
    }

    this.currentMinute += 1;

    // Simula probabilidade de gols e cartões para cada jogo em andamento
    this.todayMatches.forEach(m => {
      if (m.status !== 'live') return;

      const scores = m.score.split('-').map(Number);
      let homeScore = scores[0];
      let awayScore = scores[1];
      m.events = m.events || [];

      // 1. Chance de gol (2.0% de chance para o mandante, 1.8% para o visitante por minuto)
      const homeGoalRoll = Math.random();
      const awayGoalRoll = Math.random();

      if (homeGoalRoll < 0.020) {
        homeScore += 1;
        const scorer = getRandomPlayer(m.home_team);
        m.score = `${homeScore}-${awayScore}`;
        m.events.push({
          minute: this.currentMinute,
          type: 'goal',
          team: 'home',
          player: scorer,
          score: m.score,
          description: `Gol! ${scorer}`
        });
      } else if (awayGoalRoll < 0.018) {
        awayScore += 1;
        const scorer = getRandomPlayer(m.away_team);
        m.score = `${homeScore}-${awayScore}`;
        m.events.push({
          minute: this.currentMinute,
          type: 'goal',
          team: 'away',
          player: scorer,
          score: m.score,
          description: `Gol! ${scorer}`
        });
      }

      // 2. Chance de cartão (1.5% de chance por minuto no jogo)
      if (Math.random() < 0.015) {
        const isHome = Math.random() > 0.5;
        const team = isHome ? m.home_team : m.away_team;
        const player = getRandomPlayer(team);
        const isRed = Math.random() > 0.90; // 10% de chance de vermelho

        m.events.push({
          minute: this.currentMinute,
          type: isRed ? 'card_red' : 'card_yellow',
          team: isHome ? 'home' : 'away',
          player: player,
          description: isRed ? `Cartão Vermelho direto!` : `Cartão Amarelo`
        });
      }
    });

    if (this.onUpdate) {
      this.onUpdate(this.allMatches);
    }
  }

  // Reseta todos os jogos de hoje para agendados (limpando o estado da simulação)
  reset() {
    this.stop();
    this.currentMinute = 0;
    this.todayMatches.forEach(m => {
      m.status = 'scheduled';
      m.score = null;
      m.events = [];
    });
    if (this.onUpdate) this.onUpdate(this.allMatches);
  }
}
