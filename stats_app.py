import streamlit as st
import pandas as pd
import requests
import json
import re
import random
import os
import xml.etree.ElementTree as ET

# ---------------------------------------------------------
# INTERNACIONALIZAÇÃO (QUERY PARAMS & XML MAPPING)
# ---------------------------------------------------------
# Obter parâmetros da URL (Streamlit > 1.30.0 st.query_params)
query_params = st.query_params
lang = query_params.get("language", "en")
if isinstance(lang, list):
    lang = lang[0]
lang = lang.lower()
if lang not in ['pt', 'en', 'it', 'es', 'fr']:
    lang = 'en'

# Carregar dicionário XML de traduções do projeto principal
translations = {}
xml_path = "public/translate.xml"
if os.path.exists(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for key_node in root.findall("key"):
            key_name = key_node.attrib.get("name")
            translations[key_name] = {}
            for l in ['pt', 'en', 'it', 'es', 'fr']:
                ln = key_node.find(l)
                translations[key_name][l] = ln.text.strip() if (ln is not None and ln.text) else ""
    except Exception as e:
        print("Erro ao analisar translate.xml no streamlit:", e)

# Dicionário de traduções locais para os rótulos do dashboard
LOCAL_STRINGS = {
    'dashboard_title': {
        'pt': "📊 Análise e Estatísticas - Copa do Mundo 2026",
        'en': "📊 Analysis and Statistics - World Cup 2026",
        'it': "📊 Analisi e Statistiche - Coppa del Mondo 2026",
        'es': "📊 Análisis y Estadísticas - Copa del Mundo 2026",
        'fr': "📊 Analyse et Statistiques - Coupe du Monde 2026"
    },
    'dashboard_subtitle': {
        'pt': "Dashboard analítico de desempenho das partidas concluídas do torneio.",
        'en': "Analytical dashboard of the completed matches of the tournament.",
        'it': "Pannello analitico delle partite completate del torneo.",
        'es': "Tablero analítico de los partidos completados del torneo.",
        'fr': "Tableau de bord analytique des matchs terminés du tournoi."
    },
    'no_finished_matches': {
        'pt': "Nenhuma partida finalizada disponível para estatísticas no momento.",
        'en': "No finished matches available for statistics at the moment.",
        'it': "Nessuna partita completata disponibile al momento.",
        'es': "No hay partidos finalizados disponibles para estadísticas en este momento.",
        'fr': "Aucun match terminé disponible pour les statistiques pour le moment."
    },
    'finished_matches': {
        'pt': "Partidas Concluídas",
        'en': "Completed Matches",
        'it': "Partite Completate",
        'es': "Partidos Concluidos",
        'fr': "Matchs Terminés"
    },
    'total_goals': {
        'pt': "Total de Gols",
        'en': "Total Goals",
        'it': "Gol Totali",
        'es': "Total de Goles",
        'fr': "Total des Buts"
    },
    'avg_goals': {
        'pt': "Média de Gols",
        'en': "Average Goals",
        'it': "Media Gol",
        'es': "Promedio de Goles",
        'fr': "Moyenne de Buts"
    },
    'avg_fouls': {
        'pt': "Média de Faltas",
        'en': "Average Fouls",
        'it': "Media Falli",
        'es': "Promedio de Faltas",
        'fr': "Moyenne des Fautes"
    },
    'cards': {
        'pt': "Cartões",
        'en': "Cards",
        'it': "Cartellini",
        'es': "Tarjetas",
        'fr': "Cartons"
    },
    'top_scorers': {
        'pt': "🎯 Artilharia do Torneio (Top Scorers)",
        'en': "🎯 Tournament Top Scorers",
        'it': "🎯 Capocannonieri del Torneo",
        'es': "🎯 Goleadores del Torneo",
        'fr': "🎯 Meilleurs Buteurs du Tournoi"
    },
    'player': {
        'pt': "Jogador",
        'en': "Player",
        'it': "Giocatore",
        'es': "Jugador",
        'fr': "Joueur"
    },
    'goals': {
        'pt': "Gols",
        'en': "Goals",
        'it': "Gol",
        'es': "Goles",
        'fr': "Buts"
    },
    'no_goals': {
        'pt': "Sem gols registrados.",
        'en': "No goals registered.",
        'it': "Nessun gol registrato.",
        'es': "No hay goles registrados.",
        'fr': "Aucun but enregistré."
    },
    'match_results': {
        'pt': "🔥 Resultados das Partidas",
        'en': "🔥 Match Results",
        'it': "🔥 Risultati delle Partite",
        'es': "🔥 Resultados de los Partidos",
        'fr': "🔥 Résultats des Matchs"
    },
    'outcome': {
        'pt': "Resultado",
        'en': "Outcome",
        'it': "Risultato",
        'es': "Resultado",
        'fr': "Résultat"
    },
    'quantity': {
        'pt': "Quantidade",
        'en': "Quantity",
        'it': "Quantità",
        'es': "Cantidad",
        'fr': "Quantité"
    },
    'home_wins': {
        'pt': "Vitórias Mandante",
        'en': "Home Wins",
        'it': "Vittorie Casa",
        'es': "Victorias Local",
        'fr': "Victoires Domicile"
    },
    'draws': {
        'pt': "Empates",
        'en': "Draws",
        'it': "Pareggi",
        'es': "Empates",
        'fr': "Nuls"
    },
    'away_wins': {
        'pt': "Vitórias Visitante",
        'en': "Away Wins",
        'it': "Vittorie Trasferta",
        'es': "Victorias Visitante",
        'fr': "Victoires Extérieur"
    },
    'efficient_attacks': {
        'pt': "⚽ Ataques Mais Eficientes (Gols por Seleção)",
        'en': "⚽ Most Efficient Attacks (Goals by Team)",
        'it': "⚽ Attacchi Più Efficienti (Gol per Squadra)",
        'es': "⚽ Ataques Más Eficientes (Goles por Selección)",
        'fr': "⚽ Attaques les Plus Efficaces (Buts par Équipe)"
    },
    'team': {
        'pt': "Time",
        'en': "Team",
        'it': "Squadra",
        'es': "Equipo",
        'fr': "Équipe"
    },
    'goals_scored': {
        'pt': "Gols Marcados",
        'en': "Goals Scored",
        'it': "Gol Segnati",
        'es': "Goles Marcados",
        'fr': "Buts Marqués"
    },
    'recent_matches': {
        'pt': "📋 Últimas Partidas Concluídas",
        'en': "📋 Last Completed Matches",
        'it': "📋 Ultime Partite Completate",
        'es': "📋 Últimos Partidos Concluidos",
        'fr': "📋 Derniers Matchs Terminés"
    },
    'match': {
        'pt': "Partida",
        'en': "Match",
        'it': "Partita",
        'es': "Partido",
        'fr': "Match"
    },
    'phase': {
        'pt': "Fase",
        'en': "Phase",
        'it': "Fase",
        'es': "Fase",
        'fr': "Phase"
    },
    'stadium': {
        'pt': "Estádio",
        'en': "Stadium",
        'it': "Stadio",
        'es': "Estadio",
        'fr': "Stade"
    },
    'per_game': {
        'pt': "/ jogo",
        'en': "/ game",
        'it': "/ partita",
        'es': "/ partido",
        'fr': "/ match"
    },
    'total_label': {
        'pt': "Total",
        'en': "Total",
        'it': "Totale",
        'es': "Total",
        'fr': "Total"
    },
    'group': {
        'pt': "Grupo",
        'en': "Group",
        'it': "Gruppo",
        'es': "Grupo",
        'fr': "Groupe"
    }
}

def t(key, default=None):
    if default is None:
        default = key
    # Tenta chave local
    if key in LOCAL_STRINGS:
        return LOCAL_STRINGS[key].get(lang, default)
    # Tenta chave XML (ex: nomes de países)
    if key in translations:
        val = translations[key].get(lang)
        if val:
            return val
    return default

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title=t('dashboard_title'),
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injeção de CSS customizado para manter a identidade visual neon green
st.markdown("""
<style>
    .main {
        background-color: #09090b;
    }
    div[data-testid="stMetricValue"] {
        color: #00ff87 !important;
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }
    .stProgress > div > div > div > div {
        background-color: #00ff87;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif;
    }
    div[data-testid="stCard"] {
        background-color: #141416;
        border: 1px solid #27272a;
        border-radius: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Elenco de jogadores por país para simular artilheiros realistas
PLAYERS = {
    'Brazil': ['Vini Jr.', 'Rodrygo', 'Neymar', 'Raphinha', 'Bruno Guimarães', 'Gabriel Martinelli'],
    'Argentina': ['Lionel Messi', 'Lautaro Martínez', 'Julián Álvarez', 'Di María', 'Enzo Fernández'],
    'Germany': ['Jamal Musiala', 'Florian Wirtz', 'Kai Havertz', 'Thomas Müller', 'Leroy Sané'],
    'France': ['Kylian Mbappé', 'Antoine Griezmann', 'Ousmane Dembélé', 'Olivier Giroud'],
    'Netherlands': ['Cody Gakpo', 'Memphis Depay', 'Xavi Simons', 'Frenkie de Jong'],
    'Spain': ['Lamine Yamal', 'Nico Williams', 'Alvaro Morata', 'Dani Olmo'],
    'Portugal': ['Cristiano Ronaldo', 'Bruno Fernandes', 'Bernardo Silva', 'Rafael Leão'],
    'England': ['Harry Kane', 'Jude Bellingham', 'Bukayo Saka', 'Phil Foden'],
    'Mexico': ['Santiago Giménez', 'Hirving Lozano', 'Edson Álvarez'],
    'USA': ['Christian Pulisic', 'Timothy Weah', 'Weston McKennie'],
    'Canada': ['Alphonso Davies', 'Jonathan David', 'Cyle Larin'],
    'South Korea': ['Heung-min Son', 'Hwang Hee-chan', 'Lee Kang-in'],
    'Ecuador': ['Enner Valencia', 'Moises Caicedo', 'Kendry Páez']
}

def get_random_scorer(team):
    roster = PLAYERS.get(team, ['Nº 9', 'Nº 10', 'Nº 11', 'Nº 8'])
    # Usa o nome do time como semente para manter os artilheiros consistentes por rodada
    random.seed(len(team) + 42)
    return random.choice(roster)

# Função para carregar jogos da API com fallback local
def get_data():
    api_url = "https://ai-worldcup26.jd0rwz.easypanel.host/matches"
    headers = {"X-Token": "COPA26!"}
    
    try:
        # Tenta requisição direta
        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Falha ao buscar da API, usando fallback local:", e)
        
    # Fallback: Parse do arquivo de JS fallback
    try:
        with open("src/fallback-matches.js", "r", encoding="utf-8") as f:
            content = f.read()
            json_str = re.sub(r"^export\s+const\s+FALLBACK_MATCHES\s*=\s*", "", content)
            json_str = re.sub(r";\s*$", "", json_str)
            return json.loads(json_str)
    except Exception as e:
        print("Erro crítico ao carregar fallback matches no streamlit:", e)
        return []

# Carrega e filtra dados
all_matches = get_data()
finished_matches = [m for m in all_matches if m.get('status') == 'finished' and m.get('score')]

st.title(t('dashboard_title'))
st.markdown(t('dashboard_subtitle'))

if not finished_matches:
    st.info(t('no_finished_matches'))
else:
    # ---------------------------------------------------------
    # PROCESSAMENTO DE DADOS DE ANÁLISE
    # ---------------------------------------------------------
    total_games = len(finished_matches)
    total_goals = 0
    home_wins = 0
    away_wins = 0
    draws = 0
    
    team_goals = {}
    top_scorers = {}
    total_fouls = 0
    total_yellow_cards = 0
    total_red_cards = 0

    for idx, match in enumerate(finished_matches):
        home_team = match['home_team']
        away_team = match['away_team']
        score = match['score']
        
        scores = [int(s) for s in score.split('-')]
        home_score, away_score = scores[0], scores[1]
        
        total_goals += (home_score + away_score)
        
        # Resultados
        if home_score > away_score:
            home_wins += 1
        elif home_score < away_score:
            away_wins += 1
        else:
            draws += 1
            
        # Gols por time
        team_goals[home_team] = team_goals.get(home_team, 0) + home_score
        team_goals[away_team] = team_goals.get(away_team, 0) + away_score
        
        # Simula estatísticas de faltas e cartões baseadas no ID para consistência
        random.seed(match['id'])
        match_fouls = random.randint(18, 32)
        match_yellows = random.randint(1, 6)
        match_reds = 1 if random.random() > 0.85 else 0
        
        total_fouls += match_fouls
        total_yellow_cards += match_yellows
        total_red_cards += match_reds
        
        # Simulação de Goleadores (Artilharia)
        # Gols do mandante
        for _ in range(home_score):
            scorer = get_random_scorer(home_team)
            top_scorers[scorer] = top_scorers.get(scorer, 0) + 1
        # Gols do visitante
        for _ in range(away_score):
            scorer = get_random_scorer(away_team)
            top_scorers[scorer] = top_scorers.get(scorer, 0) + 1

    avg_goals = total_goals / total_games
    avg_fouls = total_fouls / total_games

    # ---------------------------------------------------------
    # GRÁFICOS E MÉTRICAS
    # ---------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t('finished_matches'), f"{total_games}")
    col2.metric(t('total_goals'), f"{total_goals}", f"{avg_goals:.2f} {t('per_game')}")
    col3.metric(t('avg_fouls'), f"{avg_fouls:.1f}", f"{t('total_label')}: {total_fouls}")
    col4.metric(t('cards'), f"🟨 {total_yellow_cards} | 🟥 {total_red_cards}")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader(t('top_scorers'))
        df_scorers = pd.DataFrame(
            list(top_scorers.items()), 
            columns=[t('player'), t('goals')]
        ).sort_values(by=t('goals'), ascending=False).head(8)
        
        if not df_scorers.empty:
            st.bar_chart(data=df_scorers.set_index(t('player')), color="#00ff87")
        else:
            st.write(t('no_goals'))

    with col_right:
        st.subheader(t('match_results'))
        outcomes = {
            t('outcome'): [t('home_wins'), t('draws'), t('away_wins')],
            t('quantity'): [home_wins, draws, away_wins]
        }
        df_outcomes = pd.DataFrame(outcomes)
        st.bar_chart(data=df_outcomes.set_index(t('outcome')), color="#64748b")

    st.markdown("---")
    
    col_bottom_left, col_bottom_right = st.columns(2)
    
    with col_bottom_left:
        st.subheader(t('efficient_attacks'))
        # Mapeia e traduz nomes de seleções
        translated_teams = [(t(team), goals) for team, goals in team_goals.items()]
        df_teams = pd.DataFrame(
            translated_teams,
            columns=[t('team'), t('goals_scored')]
        ).sort_values(by=t('goals_scored'), ascending=False).head(10)
        
        st.dataframe(
            df_teams,
            column_config={
                t("team"): st.column_config.TextColumn(t("team")),
                t("goals_scored"): st.column_config.NumberColumn(t("goals"), format="%d ⚽")
            },
            hide_index=True,
            use_container_width=True
        )
        
    with col_bottom_right:
        st.subheader(t('recent_matches'))
        recent_list = []
        for m in finished_matches[-5:]:
            recent_list.append({
                t("match"): f"{t(m['home_team'])} {m['score']} {t(m['away_team'])}",
                t("phase"): f"{t('group')} {m['group']}" if len(m['group']) == 1 else m['group'],
                t("stadium"): m['stadium']
            })
            
        st.table(pd.DataFrame(recent_list))
