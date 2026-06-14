import streamlit as st
import pandas as pd
import requests
import json
import re
import random
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------------------------------------
# INTERNACIONALIZAÇÃO
# ---------------------------------------------------------
query_params = st.query_params
lang = query_params.get("language", "en")
if isinstance(lang, list):
    lang = lang[0]
lang = lang.lower()
if lang not in ['pt', 'en', 'it', 'es', 'fr']:
    lang = 'en'

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
        print("Erro ao analisar translate.xml:", e)

LOCAL_STRINGS = {
    'dashboard_title': {'pt': "Copa do Mundo FIFA 2026", 'en': "FIFA World Cup 2026", 'it': "Coppa del Mondo FIFA 2026", 'es': "Copa del Mundo FIFA 2026", 'fr': "Coupe du Monde FIFA 2026"},
    'dashboard_subtitle': {'pt': "Estatísticas e resultados completos do torneio", 'en': "Complete tournament statistics and results", 'it': "Statistiche e risultati completi del torneo", 'es': "Estadísticas y resultados completos del torneo", 'fr': "Statistiques et résultats complets du tournoi"},
    'tab_overview': {'pt': "Visão Geral", 'en': "Overview", 'it': "Panoramica", 'es': "Vista General", 'fr': "Aperçu"},
    'tab_calendar': {'pt': "Calendário", 'en': "Calendar", 'it': "Calendario", 'es': "Calendario", 'fr': "Calendrier"},
    'tab_scorers': {'pt': "Artilharia", 'en': "Top Scorers", 'it': "Capocannonieri", 'es': "Goleadores", 'fr': "Buteurs"},
    'tab_teams': {'pt': "Classificação", 'en': "Standings", 'it': "Classifica", 'es': "Clasificación", 'fr': "Classement"},
    'tab_xg': {'pt': "xG & Eficiência", 'en': "xG & Efficiency", 'it': "xG & Efficienza", 'es': "xG & Eficiencia", 'fr': "xG & Efficacité"},
    'tab_timeline': {'pt': "Gols por Minuto", 'en': "Goals by Minute", 'it': "Gol per Minuto", 'es': "Goles por Minuto", 'fr': "Buts par Minute"},
    'tab_discipline': {'pt': "Disciplina", 'en': "Discipline", 'it': "Disciplina", 'es': "Disciplina", 'fr': "Discipline"},
    'tab_compare': {'pt': "Comparador", 'en': "Comparison", 'it': "Confronto", 'es': "Comparador", 'fr': "Comparateur"},
    'no_finished_matches': {'pt': "Nenhuma partida finalizada disponível.", 'en': "No finished matches available.", 'it': "Nessuna partita completata disponibile.", 'es': "No hay partidos finalizados.", 'fr': "Aucun match terminé disponible."},
    'finished_matches': {'pt': "Partidas Disputadas", 'en': "Matches Played", 'it': "Partite Disputate", 'es': "Partidos Disputados", 'fr': "Matchs Joués"},
    'total_goals': {'pt': "Gols Marcados", 'en': "Goals Scored", 'it': "Gol Segnati", 'es': "Goles Marcados", 'fr': "Buts Marqués"},
    'avg_goals': {'pt': "Média por Jogo", 'en': "Average per Game", 'it': "Media per Partita", 'es': "Promedio por Partido", 'fr': "Moyenne par Match"},
    'yellow_cards': {'pt': "Amarelos", 'en': "Yellow Cards", 'it': "Gialli", 'es': "Amarillas", 'fr': "Jaunes"},
    'red_cards': {'pt': "Vermelhos", 'en': "Red Cards", 'it': "Rossi", 'es': "Rojas", 'fr': "Rouges"},
    'top_scorers_title': {'pt': "Artilharia do Torneio", 'en': "Tournament Top Scorers", 'it': "Capocannonieri del Torneo", 'es': "Goleadores del Torneo", 'fr': "Meilleurs Buteurs"},
    'player': {'pt': "Jogador", 'en': "Player", 'it': "Giocatore", 'es': "Jugador", 'fr': "Joueur"},
    'goals': {'pt': "Gols", 'en': "Goals", 'it': "Gol", 'es': "Goles", 'fr': "Buts"},
    'country': {'pt': "Seleção", 'en': "Country", 'it': "Nazione", 'es': "Selección", 'fr': "Pays"},
    'match_results': {'pt': "Distribuição dos Resultados", 'en': "Results Distribution", 'it': "Distribuzione Risultati", 'es': "Distribución de Resultados", 'fr': "Distribution des Résultats"},
    'outcome': {'pt': "Resultado", 'en': "Outcome", 'it': "Risultato", 'es': "Resultado", 'fr': "Résultat"},
    'quantity': {'pt': "Qtd", 'en': "Count", 'it': "Quantità", 'es': "Cantidad", 'fr': "Quantité"},
    'home_wins': {'pt': "Vitórias Mandante", 'en': "Home Wins", 'it': "Vittorie Casa", 'es': "Victorias Local", 'fr': "Victoires Domicile"},
    'draws': {'pt': "Empates", 'en': "Draws", 'it': "Pareggi", 'es': "Empates", 'fr': "Nuls"},
    'away_wins': {'pt': "Vitórias Visitante", 'en': "Away Wins", 'it': "Vittorie Trasferta", 'es': "Victorias Visitante", 'fr': "Victoires Extérieur"},
    'goals_by_team': {'pt': "Gols por Seleção", 'en': "Goals by Team", 'it': "Gol per Squadra", 'es': "Goles por Selección", 'fr': "Buts par Équipe"},
    'team': {'pt': "Seleção", 'en': "Team", 'it': "Squadra", 'es': "Equipo", 'fr': "Équipe"},
    'goals_scored': {'pt': "Gols", 'en': "Goals", 'it': "Gol", 'es': "Goles", 'fr': "Buts"},
    'match': {'pt': "Partida", 'en': "Match", 'it': "Partita", 'es': "Partido", 'fr': "Match"},
    'phase': {'pt': "Fase", 'en': "Phase", 'it': "Fase", 'es': "Fase", 'fr': "Phase"},
    'stadium': {'pt': "Estádio", 'en': "Stadium", 'it': "Stadio", 'es': "Estadio", 'fr': "Stade"},
    'city': {'pt': "Cidade", 'en': "City", 'it': "Città", 'es': "Ciudad", 'fr': "Ville"},
    'group': {'pt': "Grupo", 'en': "Group", 'it': "Gruppo", 'es': "Grupo", 'fr': "Groupe"},
    'per_game': {'pt': "/ jogo", 'en': "/ game", 'it': "/ partita", 'es': "/ partido", 'fr': "/ match"},
    'select_day': {'pt': "Selecione o dia", 'en': "Select a day", 'it': "Seleziona un giorno", 'es': "Selecciona un día", 'fr': "Sélectionnez un jour"},
    'match_detail': {'pt': "Estatísticas da Partida", 'en': "Match Statistics", 'it': "Statistiche della Partita", 'es': "Estadísticas del Partido", 'fr': "Statistiques du Match"},
    'fouls': {'pt': "Faltas", 'en': "Fouls", 'it': "Falli", 'es': "Faltas", 'fr': "Fautes"},
    'shots': {'pt': "Chutes", 'en': "Shots", 'it': "Tiri", 'es': "Disparos", 'fr': "Tirs"},
    'shots_on_target': {'pt': "Chutes no Alvo", 'en': "Shots on Target", 'it': "Tiri in Porta", 'es': "Tiros a Puerta", 'fr': "Tirs Cadrés"},
    'possession': {'pt': "Posse de Bola", 'en': "Ball Possession", 'it': "Possesso Palla", 'es': "Posesión", 'fr': "Possession"},
    'corners': {'pt': "Escanteios", 'en': "Corners", 'it': "Calci d'angolo", 'es': "Córneres", 'fr': "Corners"},
    'offsides': {'pt': "Impedimentos", 'en': "Offsides", 'it': "Fuorigioco", 'es': "Fuera de Juego", 'fr': "Hors-Jeu"},
    'saves': {'pt': "Defesas do Goleiro", 'en': "Goalkeeper Saves", 'it': "Parate", 'es': "Atajadas", 'fr': "Arrêts"},
    'pass_accuracy': {'pt': "Precisão de Passe", 'en': "Pass Accuracy", 'it': "Precisione Passaggi", 'es': "Precisión de Pase", 'fr': "Précision des Passes"},
    'status_finished': {'pt': "Finalizada", 'en': "Finished", 'it': "Terminata", 'es': "Finalizado", 'fr': "Terminé"},
    'status_scheduled': {'pt': "Agendada", 'en': "Scheduled", 'it': "Programmata", 'es': "Programado", 'fr': "Programmé"},
    'status_live': {'pt': "Ao Vivo", 'en': "Live", 'it': "In Diretta", 'es': "En Vivo", 'fr': "En Direct"},
    'no_goals_text': {'pt': "Sem gols registrados.", 'en': "No goals registered.", 'it': "Nessun gol registrato.", 'es': "Sin goles registrados.", 'fr': "Aucun but enregistré."},
    'all_days': {'pt': "Todos os dias", 'en': "All days", 'it': "Tutti i giorni", 'es': "Todos los días", 'fr': "Tous les jours"},
    'scorers_match': {'pt': "Artilheiros", 'en': "Goal Scorers", 'it': "Marcatori", 'es': "Goleadores", 'fr': "Buteurs"},
    'home': {'pt': "Mandante", 'en': "Home", 'it': "Casa", 'es': "Local", 'fr': "Domicile"},
    'away': {'pt': "Visitante", 'en': "Away", 'it': "Trasferta", 'es': "Visitante", 'fr': "Extérieur"},
    'winner': {'pt': "Vencedor", 'en': "Winner", 'it': "Vincitore", 'es': "Ganador", 'fr': "Vainqueur"},
    'draw_result': {'pt': "Empate", 'en': "Draw", 'it': "Pareggio", 'es': "Empate", 'fr': "Match Nul"},
    'tournament_progress': {'pt': "Progresso do Torneio", 'en': "Tournament Progress", 'it': "Avanzamento del Torneo", 'es': "Progreso del Torneo", 'fr': "Avancement du Tournoi"},
    'xg_title': {'pt': "Expected Goals (xG) por Seleção", 'en': "Expected Goals (xG) by Team", 'it': "Expected Goals (xG) per Squadra", 'es': "Expected Goals (xG) por Selección", 'fr': "Expected Goals (xG) par Équipe"},
    'xg_label': {'pt': "xG (Gols Esperados)", 'en': "xG (Expected Goals)", 'it': "xG (Gol Attesi)", 'es': "xG (Goles Esperados)", 'fr': "xG (Buts Attendus)"},
    'real_goals': {'pt': "Gols Reais", 'en': "Real Goals", 'it': "Gol Reali", 'es': "Goles Reales", 'fr': "Buts Réels"},
    'conversion': {'pt': "Conversão %", 'en': "Conversion %", 'it': "Conversione %", 'es': "Conversión %", 'fr': "Conversion %"},
    'overperformer': {'pt': "Acima do xG — converteu mais que o esperado", 'en': "Overperformer — scored more than expected", 'it': "Sopra l'xG — ha segnato più del previsto", 'es': "Por encima del xG — marcó más de lo esperado", 'fr': "Au-dessus du xG — a marqué plus que prévu"},
    'underperformer': {'pt': "Abaixo do xG — precisa melhorar aproveitamento", 'en': "Underperformer — missed opportunities", 'it': "Sotto l'xG — ha perso opportunità", 'es': "Por debajo del xG — perdió oportunidades", 'fr': "Sous le xG — a raté des occasions"},
    'goals_by_minute': {'pt': "Gols por Intervalo de Tempo", 'en': "Goals by Time Interval", 'it': "Gol per Intervallo di Tempo", 'es': "Goles por Intervalo de Tiempo", 'fr': "Buts par Intervalle de Temps"},
    'minute': {'pt': "Minuto", 'en': "Minute", 'it': "Minuto", 'es': "Minuto", 'fr': "Minute"},
    'discipline_title': {'pt': "Tabela de Disciplina por Seleção", 'en': "Discipline Table by Team", 'it': "Tabella Disciplina per Squadra", 'es': "Tabla de Disciplina por Selección", 'fr': "Tableau de Discipline par Équipe"},
    'total_cards': {'pt': "Total de Cartões", 'en': "Total Cards", 'it': "Cartellini Totali", 'es': "Tarjetas Totales", 'fr': "Cartons Totaux"},
    'fouls_total': {'pt': "Total de Faltas", 'en': "Total Fouls", 'it': "Falli Totali", 'es': "Faltas Totales", 'fr': "Fautes Totales"},
    'clean_sheets': {'pt': "Jogos Sem Sofrer Gol", 'en': "Clean Sheets", 'it': "Porte Inviolate", 'es': "Porterías a Cero", 'fr': "Clean Sheets"},
    'compare_title': {'pt': "Comparador de Seleções", 'en': "Team Comparison", 'it': "Confronto tra Squadre", 'es': "Comparador de Selecciones", 'fr': "Comparateur d'Équipes"},
    'select_home': {'pt': "Seleção A", 'en': "Team A", 'it': "Squadra A", 'es': "Selección A", 'fr': "Équipe A"},
    'select_away': {'pt': "Seleção B", 'en': "Team B", 'it': "Squadra B", 'es': "Selección B", 'fr': "Équipe B"},
    'radar_attack': {'pt': "Ataque", 'en': "Attack", 'it': "Attacco", 'es': "Ataque", 'fr': "Attaque"},
    'radar_defense': {'pt': "Defesa", 'en': "Defense", 'it': "Difesa", 'es': "Defensa", 'fr': "Défense"},
    'radar_possession': {'pt': "Posse", 'en': "Possession", 'it': "Possesso", 'es': "Posesión", 'fr': "Possession"},
    'radar_discipline': {'pt': "Disciplina", 'en': "Discipline", 'it': "Disciplina", 'es': "Disciplina", 'fr': "Discipline"},
    'radar_xg': {'pt': "xG", 'en': "xG", 'it': "xG", 'es': "xG", 'fr': "xG"},
    'radar_efficiency': {'pt': "Eficiência", 'en': "Efficiency", 'it': "Efficienza", 'es': "Eficiencia", 'fr': "Efficacité"},
    'biggest_win': {'pt': "Maior Goleada", 'en': "Biggest Win", 'it': "Maggiore Vittoria", 'es': "Mayor Goleada", 'fr': "Plus Grand Écart"},
    'highest_scoring': {'pt': "Jogo com Mais Gols", 'en': "Highest Scoring Match", 'it': "Partita con Più Gol", 'es': "Partido con Más Goles", 'fr': "Match le Plus Prolifique"},
    'most_efficient': {'pt': "Ataque Mais Eficiente", 'en': "Most Efficient Attack", 'it': "Attacco Più Efficiente", 'es': "Ataque Más Eficiente", 'fr': "Attaque la Plus Efficace"},
    'form': {'pt': "Forma Recente", 'en': "Recent Form", 'it': "Forma Recente", 'es': "Forma Reciente", 'fr': "Forme Récente"},
    'venue_title': {'pt': "Estatísticas por Sede", 'en': "Venue Statistics", 'it': "Statistiche per Sede", 'es': "Estadísticas por Sede", 'fr': "Statistiques par Lieu"},
    'venue_matches': {'pt': "Jogos", 'en': "Matches", 'it': "Partite", 'es': "Partidos", 'fr': "Matchs"},
    'avg_goals_venue': {'pt': "Média de Gols", 'en': "Avg Goals", 'it': "Media Gol", 'es': "Prom. Goles", 'fr': "Moy. Buts"},
}

def t(key, default=None):
    if default is None:
        default = key
    if key in LOCAL_STRINGS:
        return LOCAL_STRINGS[key].get(lang, default)
    if key in translations:
        val = translations[key].get(lang)
        if val:
            return val
    return default

# ---------------------------------------------------------
# FLAGS
# ---------------------------------------------------------
FLAGS = {
    'Brazil': '🇧🇷', 'Argentina': '🇦🇷', 'France': '🇫🇷', 'Germany': '🇩🇪',
    'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Spain': '🇪🇸', 'Portugal': '🇵🇹', 'Netherlands': '🇳🇱',
    'Italy': '🇮🇹', 'Belgium': '🇧🇪', 'USA': '🇺🇸', 'Mexico': '🇲🇽',
    'Canada': '🇨🇦', 'Japan': '🇯🇵', 'South Korea': '🇰🇷', 'Australia': '🇦🇺',
    'Morocco': '🇲🇦', 'Senegal': '🇸🇳', 'Uruguay': '🇺🇾', 'Colombia': '🇨🇴',
    'Ecuador': '🇪🇨', 'Switzerland': '🇨🇭', 'Croatia': '🇭🇷', 'Denmark': '🇩🇰',
    'Sweden': '🇸🇪', 'Norway': '🇳🇴', 'Austria': '🇦🇹', 'Poland': '🇵🇱',
    'Turkey': '🇹🇷', 'Iran': '🇮🇷', 'Saudi Arabia': '🇸🇦', 'South Africa': '🇿🇦',
    'Ghana': '🇬🇭', 'Tunisia': '🇹🇳', 'Egypt': '🇪🇬', 'Algeria': '🇩🇿',
    'DR Congo': '🇨🇩', 'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Paraguay': '🇵🇾', 'Qatar': '🇶🇦',
    'Haiti': '🇭🇹', 'Panama': '🇵🇦', 'Bosnia and Herzegovina': '🇧🇦',
    'Czech Republic': '🇨🇿', 'Cape Verde': '🇨🇻', 'Jordan': '🇯🇴', 'Iraq': '🇮🇶',
    'Uzbekistan': '🇺🇿', 'New Zealand': '🇳🇿', 'Curaçao': '🇨🇼', 'Ivory Coast': '🇨🇮',
}

def flag(team):
    return FLAGS.get(team, '🏳️')

# ---------------------------------------------------------
# JOGADORES POR PAÍS
# ---------------------------------------------------------
PLAYERS = {
    'Brazil': ['Vini Jr.', 'Rodrygo', 'Endrick', 'Raphinha', 'Bruno Guimarães', 'Gabriel Martinelli'],
    'Argentina': ['Lionel Messi', 'Lautaro Martínez', 'Julián Álvarez', 'Di María', 'Enzo Fernández'],
    'France': ['Kylian Mbappé', 'Ousmane Dembélé', 'Antoine Griezmann', 'Marcus Thuram', 'Tchouaméni'],
    'Germany': ['Florian Wirtz', 'Kai Havertz', 'Leroy Sané', 'Jamal Musiala', 'Thomas Müller'],
    'England': ['Jude Bellingham', 'Harry Kane', 'Phil Foden', 'Bukayo Saka', 'Marcus Rashford'],
    'Spain': ['Lamine Yamal', 'Nico Williams', 'Pedri', 'Álvaro Morata', 'Dani Olmo'],
    'Portugal': ['Cristiano Ronaldo', 'Bruno Fernandes', 'Bernardo Silva', 'Rafael Leão', 'João Félix'],
    'Netherlands': ['Virgil van Dijk', 'Memphis Depay', 'Cody Gakpo', 'Xavi Simons', 'Tijjani Reijnders'],
    'USA': ['Christian Pulisic', 'Tyler Adams', 'Weston McKennie', 'Josh Sargent', 'Gio Reyna'],
    'Mexico': ['Hirving Lozano', 'Raúl Jiménez', 'Edson Álvarez', 'Henry Martín', 'Guillermo Ochoa'],
    'Morocco': ['Achraf Hakimi', 'Youssef En-Nesyri', 'Hakim Ziyech', 'Romain Saïss', 'Sofiane Boufal'],
    'Japan': ['Takehiro Tomiyasu', 'Ritsu Doan', 'Kaoru Mitoma', 'Daichi Kamada', 'Wataru Endō'],
    'South Korea': ['Son Heung-min', 'Kim Min-jae', 'Lee Kang-in', 'Hwang Hee-chan', 'Cho Gue-sung'],
    'Australia': ['Mathew Ryan', 'Mat Leckie', 'Mitch Duke', 'Aaron Mooy', 'Martin Boyle'],
    'Belgium': ['Kevin De Bruyne', 'Romelu Lukaku', 'Youri Tielemans', 'Axel Witsel', 'Toby Alderweireld'],
    'Uruguay': ['Luis Suárez', 'Darwin Núñez', 'Federico Valverde', 'Ronald Araújo', 'Rodrigo Bentancur'],
    'Colombia': ['Luis Díaz', 'Falcao', 'James Rodríguez', 'Juan Cuadrado', 'Yerry Mina'],
    'Canada': ['Alphonso Davies', 'Jonathan David', 'Cyle Larin', 'Stephen Eustáquio', 'Milan Borjan'],
    'Switzerland': ['Granit Xhaka', 'Xherdan Shaqiri', 'Yann Sommer', 'Breel Embolo', 'Manuel Akanji'],
    'Norway': ['Erling Haaland', 'Martin Ødegaard', 'Alexander Sørloth', 'Sander Berge'],
    'Sweden': ['Viktor Gyökeres', 'Dejan Kulusevski', 'Emil Forsberg', 'Alexander Isak'],
    'Turkey': ['Hakan Çalhanoğlu', 'Arda Güler', 'Kerem Aktürkoğlu', 'Cenk Tosun'],
    'Saudi Arabia': ['Salem Al-Dawsari', 'Firas Al-Buraikan', 'Saud Abdulhamid'],
    'Scotland': ['Andy Robertson', 'Scott McTominay', 'Kieran Tierney', 'John McGinn'],
    'Ecuador': ['Enner Valencia', 'Moisés Caicedo', 'Jeremy Sarmiento', 'Piero Hincapié'],
    'Croatia': ['Luka Modrić', 'Ivan Perišić', 'Mateo Kovačić', 'Andrej Kramarić', 'Joško Gvardiol'],
    'Tunisia': ['Wahbi Khazri', 'Youssef Msakni', 'Ali Maaloul', 'Ellyes Skhiri'],
    'Cape Verde': ['Garry Rodrigues', 'Ryan Mendes', 'Stopira'],
    'Senegal': ['Sadio Mané', 'Kalidou Koulibaly', 'Ismaïla Sarr', 'Idrissa Gueye'],
    'Iran': ['Mehdi Taremi', 'Sardar Azmoun', 'Alireza Jahanbakhsh'],
}

def get_random_scorer(team):
    roster = PLAYERS.get(team, ['Nº 9', 'Nº 10', 'Nº 11'])
    random.seed(len(team) + 42 + len(roster))
    return random.choice(roster)

def get_match_scorers(match):
    home_team = match['home_team']
    away_team = match['away_team']
    scores = [int(s) for s in match['score'].split('-')]
    home_score, away_score = scores[0], scores[1]
    home_scorers, away_scorers = [], []
    roster_home = PLAYERS.get(home_team, ['Nº 9', 'Nº 10'])
    roster_away = PLAYERS.get(away_team, ['Nº 9', 'Nº 10'])
    random.seed(match['id'] * 7 + home_score * 3)
    for _ in range(home_score):
        p = random.choice(roster_home)
        minute = random.randint(5, 90)
        home_scorers.append((p, minute))
    random.seed(match['id'] * 11 + away_score * 5)
    for _ in range(away_score):
        p = random.choice(roster_away)
        minute = random.randint(5, 90)
        away_scorers.append((p, minute))
    return sorted(home_scorers, key=lambda x: x[1]), sorted(away_scorers, key=lambda x: x[1])

def simulate_match_stats(match):
    random.seed(match['id'] * 13)
    shots_home = random.randint(5, 22)
    shots_away = random.randint(3, 18)
    sot_home = max(1, int(shots_home * random.uniform(0.3, 0.65)))
    sot_away = max(1, int(shots_away * random.uniform(0.3, 0.65)))
    fouls_home = random.randint(8, 20)
    fouls_away = random.randint(8, 20)
    poss_home = random.randint(38, 65)
    poss_away = 100 - poss_home
    corners_home = random.randint(2, 12)
    corners_away = random.randint(1, 9)
    yellow_home = random.randint(0, 4)
    yellow_away = random.randint(0, 4)
    red_home = 1 if random.random() > 0.9 else 0
    red_away = 1 if random.random() > 0.9 else 0
    offsides_home = random.randint(0, 5)
    offsides_away = random.randint(0, 5)
    pass_acc_home = random.randint(72, 93)
    pass_acc_away = random.randint(68, 91)
    saves_home = max(0, sot_away - int(match['score'].split('-')[1]))
    saves_away = max(0, sot_home - int(match['score'].split('-')[0]))
    # xG: baseado em chutes no alvo e posição simulada
    xg_home = round(sot_home * random.uniform(0.08, 0.22), 2)
    xg_away = round(sot_away * random.uniform(0.08, 0.22), 2)
    return {
        'shots': (shots_home, shots_away),
        'shots_on_target': (sot_home, sot_away),
        'fouls': (fouls_home, fouls_away),
        'possession': (poss_home, poss_away),
        'corners': (corners_home, corners_away),
        'yellow': (yellow_home, yellow_away),
        'red': (red_home, red_away),
        'offsides': (offsides_home, offsides_away),
        'pass_accuracy': (pass_acc_home, pass_acc_away),
        'saves': (saves_home, saves_away),
        'xg': (xg_home, xg_away),
    }

# ---------------------------------------------------------
# CARREGAR DADOS
# ---------------------------------------------------------
def get_data():
    api_url = "https://ai-worldcup26.jd0rwz.easypanel.host/matches"
    headers = {"X-Token": "COPA26!"}
    try:
        response = requests.get(api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Falha ao buscar da API, usando fallback:", e)
    try:
        with open("src/fallback-matches.js", "r", encoding="utf-8") as f:
            content = f.read()
            json_str = re.sub(r"^export\s+const\s+FALLBACK_MATCHES\s*=\s*", "", content)
            json_str = re.sub(r";\s*$", "", json_str)
            return json.loads(json_str)
    except Exception as e:
        print("Erro crítico ao carregar fallback:", e)
        return []

# ---------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------
st.set_page_config(
    page_title=t('dashboard_title'),
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

PLOTLY_DARK = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Outfit, sans-serif', color='#a1a1aa'),
    margin=dict(l=0, r=0, t=30, b=0),
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
.main { background-color: #09090b; }
section[data-testid="stSidebar"] { background-color: #0f0f11; }

.wc-header {
    background: linear-gradient(135deg, #0a3d1a 0%, #09090b 55%, #1a0a00 100%);
    border: 1px solid #1f3a28; border-radius: 20px;
    padding: 28px 32px; margin-bottom: 20px; position: relative; overflow: hidden;
}
.wc-header::before {
    content: ''; position: absolute; top: -40%; left: -5%; width: 50%; height: 180%;
    background: radial-gradient(ellipse, rgba(0,255,135,0.06) 0%, transparent 70%);
}
.wc-title { font-size: 2rem; font-weight: 900; color: #fff; margin: 0; letter-spacing: -0.5px; }
.wc-subtitle { font-size: 0.93rem; color: #71717a; margin: 4px 0 0; }
.wc-badge {
    display: inline-block; background: linear-gradient(135deg, #00ff87, #00cc6a);
    color: #09090b; font-size: 0.68rem; font-weight: 700; padding: 3px 10px;
    border-radius: 20px; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;
}
.kpi-card {
    background: #141416; border: 1px solid #27272a; border-radius: 16px;
    padding: 18px 20px; height: 100%;
}
.kpi-label { color: #71717a; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.kpi-value { color: #00ff87; font-size: 1.9rem; font-weight: 900; line-height: 1; }
.kpi-sub { color: #52525b; font-size: 0.78rem; margin-top: 4px; }
.kpi-highlight { color: #fff; font-size: 0.88rem; font-weight: 600; margin-top: 2px; }

div[data-testid="stMetricValue"] { color: #00ff87 !important; font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; }
div[data-testid="stMetricLabel"] { color: #a1a1aa !important; font-family: 'Outfit', sans-serif !important; }
div[data-testid="stTabs"] button { font-family: 'Outfit', sans-serif; font-weight: 600; color: #71717a; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #00ff87 !important; border-bottom-color: #00ff87 !important; }

.match-card { background: #141416; border: 1px solid #27272a; border-radius: 16px; padding: 16px 20px; margin-bottom: 10px; }
.match-card.finished { border-left: 3px solid #00ff87; }
.match-card.scheduled { border-left: 3px solid #3f3f46; }
.match-card.live { border-left: 3px solid #ef4444; }
.match-teams { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.match-team { font-size: 1.05rem; font-weight: 700; color: #fff; flex: 1; }
.match-team.away { text-align: right; }
.match-score { font-size: 1.5rem; font-weight: 900; color: #00ff87; min-width: 80px; text-align: center; background: #0d1f14; border-radius: 10px; padding: 4px 12px; }
.match-score.scheduled { color: #52525b; background: #18181b; font-size: 1rem; padding: 8px 12px; }
.match-meta { display: flex; gap: 14px; margin-top: 8px; font-size: 0.78rem; color: #71717a; align-items: center; flex-wrap: wrap; }
.status-badge { padding: 2px 8px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px; }
.status-finished { background: #0d1f14; color: #00ff87; }
.status-scheduled { background: #18181b; color: #71717a; }
.status-live { background: #3f0000; color: #ef4444; }

.detail-card { background: #141416; border: 1px solid #27272a; border-radius: 20px; padding: 24px; margin-top: 4px; }
.detail-score-board { background: linear-gradient(135deg, #0a1f12 0%, #09090b 100%); border: 1px solid #1f3a28; border-radius: 16px; padding: 22px; text-align: center; margin-bottom: 18px; }
.detail-teams-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.detail-team-name { font-size: 1.3rem; font-weight: 800; color: #fff; flex: 1; text-align: center; }
.detail-score-big { font-size: 2.8rem; font-weight: 900; color: #00ff87; min-width: 110px; text-align: center; }
.stat-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin: 8px 0; font-size: 0.88rem; color: #d4d4d8; }
.stat-label-center { color: #71717a; font-size: 0.78rem; text-align: center; min-width: 120px; }
.progress-container { background: #27272a; border-radius: 100px; height: 7px; overflow: hidden; flex: 1; }
.progress-fill { height: 100%; border-radius: 100px; transition: width 0.4s ease; }
.scorer-item { background: #1c1c1f; border-radius: 8px; padding: 5px 11px; margin: 3px 0; font-size: 0.82rem; color: #d4d4d8; }

.rank-row { display: flex; align-items: center; background: #141416; border: 1px solid #27272a; border-radius: 12px; padding: 10px 16px; margin-bottom: 7px; gap: 12px; }
.rank-pos { font-size: 1.05rem; font-weight: 800; color: #71717a; min-width: 28px; }
.rank-pos.gold { color: #f59e0b; } .rank-pos.silver { color: #94a3b8; } .rank-pos.bronze { color: #b45309; }
.rank-player { font-weight: 600; color: #fff; flex: 1; font-size: 0.92rem; }
.rank-team { color: #71717a; font-size: 0.8rem; }
.rank-goals { font-size: 1.05rem; font-weight: 800; color: #00ff87; min-width: 44px; text-align: right; }

.progress-bar-full { background: #27272a; border-radius: 100px; height: 8px; overflow: hidden; }
.progress-bar-fill { height: 100%; border-radius: 100px; background: linear-gradient(90deg, #00ff87, #00cc6a); }

.section-title { color: #fff; font-size: 1.05rem; font-weight: 700; margin: 18px 0 12px; display: flex; align-items: center; gap: 8px; }
.highlight-box { background: #141416; border: 1px solid #27272a; border-radius: 14px; padding: 16px 18px; }
.highlight-box.green { border-left: 3px solid #00ff87; }
.highlight-box.blue { border-left: 3px solid #3b82f6; }
.highlight-box.yellow { border-left: 3px solid #f59e0b; }
.highlight-box.red { border-left: 3px solid #ef4444; }
.hl-label { color: #71717a; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.hl-value { color: #fff; font-size: 0.98rem; font-weight: 700; }
.hl-sub { color: #52525b; font-size: 0.78rem; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CARREGA DADOS
# ---------------------------------------------------------
all_matches = get_data()
finished_matches = [m for m in all_matches if m.get('status') == 'finished' and m.get('score')]
scheduled_matches = [m for m in all_matches if m.get('status') == 'scheduled']
all_dates = sorted(list(set(m['date'] for m in all_matches)))
total_matches = len(all_matches)

# Pré-computa estatísticas acumuladas por seleção
team_agg = {}
for m in finished_matches:
    hs = int(m['score'].split('-')[0])
    aws = int(m['score'].split('-')[1])
    stats = simulate_match_stats(m)
    for team, scored, conceded, side in [
        (m['home_team'], hs, aws, 0),
        (m['away_team'], aws, hs, 1)
    ]:
        if team not in team_agg:
            team_agg[team] = {
                'played': 0, 'wins': 0, 'draws': 0, 'losses': 0,
                'gf': 0, 'ga': 0, 'pts': 0,
                'shots': 0, 'shots_on_target': 0,
                'possession': 0, 'fouls': 0,
                'yellow': 0, 'red': 0,
                'corners': 0, 'xg': 0.0,
                'offsides': 0, 'pass_acc': [], 'saves': 0,
                'clean_sheets': 0,
            }
        team_agg[team]['played'] += 1
        team_agg[team]['gf'] += scored
        team_agg[team]['ga'] += conceded
        team_agg[team]['shots'] += stats['shots'][side]
        team_agg[team]['shots_on_target'] += stats['shots_on_target'][side]
        team_agg[team]['possession'] += stats['possession'][side]
        team_agg[team]['fouls'] += stats['fouls'][side]
        team_agg[team]['yellow'] += stats['yellow'][side]
        team_agg[team]['red'] += stats['red'][side]
        team_agg[team]['corners'] += stats['corners'][side]
        team_agg[team]['xg'] += stats['xg'][side]
        team_agg[team]['offsides'] += stats['offsides'][side]
        team_agg[team]['pass_acc'].append(stats['pass_accuracy'][side])
        team_agg[team]['saves'] += stats['saves'][side]
        if conceded == 0:
            team_agg[team]['clean_sheets'] += 1
        if scored > conceded:
            team_agg[team]['wins'] += 1
            team_agg[team]['pts'] += 3
        elif scored == conceded:
            team_agg[team]['draws'] += 1
            team_agg[team]['pts'] += 1
        else:
            team_agg[team]['losses'] += 1

# Totais gerais
total_goals = sum(t_d['gf'] for t_d in team_agg.values()) // 2 if team_agg else 0
avg_goals = total_goals / len(finished_matches) if finished_matches else 0
total_yellows = sum(simulate_match_stats(m)['yellow'][0] + simulate_match_stats(m)['yellow'][1] for m in finished_matches)
total_reds = sum(simulate_match_stats(m)['red'][0] + simulate_match_stats(m)['red'][1] for m in finished_matches)
total_fouls_all = sum(simulate_match_stats(m)['fouls'][0] + simulate_match_stats(m)['fouls'][1] for m in finished_matches)
progress_pct = int((len(finished_matches) / total_matches) * 100) if total_matches > 0 else 0

# Destaques automáticos
biggest_win_match = None
biggest_win_diff = 0
highest_goals_match = None
highest_goals_total = 0
for m in finished_matches:
    s = m['score'].split('-')
    diff = abs(int(s[0]) - int(s[1]))
    total = int(s[0]) + int(s[1])
    if diff > biggest_win_diff:
        biggest_win_diff = diff
        biggest_win_match = m
    if total > highest_goals_total:
        highest_goals_total = total
        highest_goals_match = m

most_efficient_team = max(team_agg.items(),
    key=lambda x: x[1]['gf'] / max(x[1]['shots_on_target'], 1), default=(None, {}))[0] if team_agg else None

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown(f"""
<div class="wc-header">
    <div class="wc-badge">🏆 FIFA World Cup 2026 — USA · Canada · Mexico</div>
    <div class="wc-title">{t('dashboard_title')}</div>
    <div class="wc-subtitle">{t('dashboard_subtitle')}</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# KPI BAR
# ---------------------------------------------------------
c1, c2, c3, c4, c5, c6 = st.columns(6)
kpis = [
    ("⚽", t('total_goals'), str(total_goals), f"{avg_goals:.1f} {t('per_game')}"),
    ("📅", t('finished_matches'), str(len(finished_matches)), f"{progress_pct}% do torneio"),
    ("👟", t('fouls'), f"{total_fouls_all / max(len(finished_matches),1):.1f}", f"Total: {total_fouls_all}"),
    ("🟨", t('yellow_cards'), str(total_yellows), f"{total_yellows/max(len(finished_matches),1):.1f} {t('per_game')}"),
    ("🟥", t('red_cards'), str(total_reds), f"1 a cada {max(len(finished_matches)//max(total_reds,1),1)} jogos"),
    ("🏟️", "Clean Sheets", str(sum(1 for m in finished_matches if '0' in m['score'].split('-'))), "Jogos s/ gol sofrido"),
]
for col, (icon, label, val, sub) in zip([c1, c2, c3, c4, c5, c6], kpis):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{icon} {label}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab_calendar, tab_overview, tab_scorers, tab_standings, tab_xg, tab_timeline, tab_discipline, tab_compare = st.tabs([
    f"📅 {t('tab_calendar')}",
    f"📊 {t('tab_overview')}",
    f"👟 {t('tab_scorers')}",
    f"🏆 {t('tab_teams')}",
    f"🎯 {t('tab_xg')}",
    f"⏱️ {t('tab_timeline')}",
    f"🔴 {t('tab_discipline')}",
    f"⚖️ {t('tab_compare')}",
])

# ==========================================================
# TAB: CALENDÁRIO
# ==========================================================
with tab_calendar:
    if not all_dates:
        st.info(t('no_finished_matches'))
    else:
        def fmt_date(d):
            try:
                dt = datetime.strptime(d, "%Y-%m-%d")
                months = {
                    'pt': ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'],
                    'en': ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                    'es': ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
                    'fr': ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'],
                    'it': ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic'],
                }
                m_list = months.get(lang, months['en'])
                days_en = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
                days_pt = ['Seg','Ter','Qua','Qui','Sex','Sáb','Dom']
                days_map = {'pt': days_pt, 'en': days_en}
                day_names = days_map.get(lang, days_en)
                return f"{day_names[dt.weekday()]}, {dt.day} {m_list[dt.month-1]}"
            except:
                return d

        date_labels = [fmt_date(d) for d in all_dates]
        day_options = [t('all_days')] + date_labels
        selected_label = st.selectbox(f"📅 {t('select_day')}", options=day_options, index=0, key="day_sel")

        if selected_label == t('all_days'):
            filtered_dates = all_dates
        else:
            idx = date_labels.index(selected_label) if selected_label in date_labels else 0
            filtered_dates = [all_dates[idx]]

        matches_in_view = [m for m in all_matches if m['date'] in filtered_dates]
        by_date = defaultdict(list)
        for m in matches_in_view:
            by_date[m['date']].append(m)

        if 'selected_match_id' not in st.session_state:
            st.session_state.selected_match_id = None

        for d in sorted(by_date.keys()):
            day_matches = by_date[d]
            fin_count = sum(1 for m in day_matches if m.get('status') == 'finished')
            sch_count = sum(1 for m in day_matches if m.get('status') == 'scheduled')
            goals_day = sum(
                int(m['score'].split('-')[0]) + int(m['score'].split('-')[1])
                for m in day_matches if m.get('status') == 'finished' and m.get('score')
            )

            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; margin: 20px 0 10px;">
                <div style="color:#fff; font-size:1rem; font-weight:700;">📅 {fmt_date(d)}</div>
                <div style="color:#00ff87; font-size:0.73rem; font-weight:700; background:#0d1f14; padding:2px 9px; border-radius:20px;">⚽ {goals_day} gols</div>
                {"<div style='color:#52525b; font-size:0.73rem; font-weight:600; background:#18181b; padding:2px 9px; border-radius:20px;'>📋 " + str(sch_count) + "</div>" if sch_count > 0 else ""}
            </div>
            """, unsafe_allow_html=True)

            for m in day_matches:
                status = m.get('status', 'scheduled')
                status_label = t(f'status_{status}') if status in ['finished', 'scheduled', 'live'] else status
                status_class = status if status in ['finished', 'scheduled', 'live'] else 'scheduled'
                home, away = m['home_team'], m['away_team']
                hf, af = flag(home), flag(away)
                group_label = f"{t('group')} {m['group']}" if len(m.get('group','')) == 1 else m.get('group','')
                is_selected = st.session_state.selected_match_id == m['id']

                if status == 'finished' and m.get('score'):
                    score_html = f"<div class='match-score'>{m['score']}</div>"
                else:
                    score_html = f"<div class='match-score scheduled'>{m['time']}</div>"

                st.markdown(f"""
                <div class="match-card {status_class}" style="{'border-color:#00ff87;' if is_selected else ''}">
                    <div class="match-teams">
                        <div class="match-team">{hf} {home}</div>
                        {score_html}
                        <div class="match-team away">{away} {af}</div>
                    </div>
                    <div class="match-meta">
                        <span class="status-badge status-{status_class}">{status_label}</span>
                        <span>🏟️ {m.get('stadium','')}</span>
                        <span>📍 {m.get('city','')}</span>
                        <span>🏷️ {group_label}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if status == 'finished':
                    btn_label = "▼ Detalhes" if not is_selected else "▲ Fechar"
                    if st.button(btn_label, key=f"mb_{m['id']}"):
                        st.session_state.selected_match_id = None if is_selected else m['id']
                        st.rerun()

                    if is_selected:
                        stats = simulate_match_stats(m)
                        home_sc, away_sc = get_match_scorers(m)
                        hs_score = int(m['score'].split('-')[0])
                        as_score = int(m['score'].split('-')[1])
                        winner_html = (
                            f"🏆 {t('winner')}: {hf} {home}" if hs_score > as_score else
                            f"🏆 {t('winner')}: {af} {away}" if as_score > hs_score else
                            f"🤝 {t('draw_result')}"
                        )
                        ph, pa = stats['possession']
                        sh, sa = stats['shots']
                        soh, soa = stats['shots_on_target']
                        fh, fa = stats['fouls']
                        ch, ca = stats['corners']
                        yh, ya = stats['yellow']
                        rh, ra = stats['red']
                        oh, oa = stats['offsides']
                        pph, ppa = stats['pass_accuracy']
                        svh, sva = stats['saves']
                        xgh, xga = stats['xg']

                        # Pre-compute scorer HTML to avoid backslash-in-f-string (Python 3.10)
                        no_goals_html = '<div style="color:#52525b; font-size:0.8rem;">' + t('no_goals_text') + '</div>'
                        home_scorers_html = ''.join(
                            '<div class="scorer-item">⚽ ' + p + ' <span style="color:#52525b;">' + str(mi) + "'</span></div>"
                            for p, mi in home_sc
                        ) if home_sc else no_goals_html
                        away_scorers_html = ''.join(
                            '<div class="scorer-item">⚽ ' + p + ' <span style="color:#52525b;">' + str(mi) + "'</span></div>"
                            for p, mi in away_sc
                        ) if away_sc else no_goals_html

                        def stat_row_html(val_h, val_a, label, color="#00ff87", is_pct=False, invert=False):
                            max_v = max(val_h, val_a, 1)
                            w_h = int((val_h / max_v) * 100) if not invert else int((1 - val_h / max(val_h + val_a, 1)) * 100)
                            w_a = int((val_a / max_v) * 100) if not invert else int((1 - val_a / max(val_h + val_a, 1)) * 100)
                            display_h = f"{val_h}{'%' if is_pct else ''}"
                            display_a = f"{val_a}{'%' if is_pct else ''}"
                            return f"""
                            <div class="stat-row">
                                <div style="font-weight:700; color:#fff; min-width:44px;">{display_h}</div>
                                <div class="progress-container"><div class="progress-fill" style="width:{w_h}%; background:linear-gradient(90deg,{color},{color}99);"></div></div>
                                <div class="stat-label-center">{label}</div>
                                <div class="progress-container" style="transform:scaleX(-1);"><div class="progress-fill" style="width:{w_a}%; background:linear-gradient(90deg,{color},{color}99);"></div></div>
                                <div style="font-weight:700; color:#fff; min-width:44px; text-align:right;">{display_a}</div>
                            </div>"""

                        scorers_label_home = t('scorers_match') + ' — ' + hf + ' ' + home
                        scorers_label_away = t('scorers_match') + ' — ' + af + ' ' + away

                        st.markdown(f"""
                        <div class="detail-card">
                            <div class="detail-score-board">
                                <div style="color:#52525b; font-size:0.75rem; margin-bottom:10px;">🏟️ {m.get('stadium','')} · 📍 {m.get('city','')} · {m.get('date','')} {m.get('time','')}</div>
                                <div class="detail-teams-row">
                                    <div class="detail-team-name">{hf}<br>{home}</div>
                                    <div class="detail-score-big">{m['score']}</div>
                                    <div class="detail-team-name">{af}<br>{away}</div>
                                </div>
                                <div style="margin-top:12px; color:#00ff87; font-weight:600; font-size:0.88rem;">{winner_html}</div>
                                <div style="margin-top:8px; font-size:0.78rem; color:#52525b;">
                                    xG: <span style="color:#a1a1aa;">{hf} {xgh:.2f}</span> — <span style="color:#a1a1aa;">{af} {xga:.2f}</span>
                                </div>
                            </div>

                            <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:18px;">
                                <div>
                                    <div style="color:#71717a; font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.5px; margin-bottom:8px;">⚽ {scorers_label_home}</div>
                                    {home_scorers_html}
                                </div>
                                <div>
                                    <div style="color:#71717a; font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.5px; margin-bottom:8px;">⚽ {scorers_label_away}</div>
                                    {away_scorers_html}
                                </div>
                            </div>

                            <div style="color:#71717a; font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.5px; margin-bottom:10px; border-top:1px solid #27272a; padding-top:14px;">
                                📊 {t('match_detail')}
                            </div>
                            <div style="display:flex; justify-content:space-between; margin-bottom:10px; padding: 0 44px;">
                                <span style="color:#71717a; font-size:0.78rem; font-weight:600;">{hf} {home}</span>
                                <span style="color:#71717a; font-size:0.78rem; font-weight:600;">{af} {away}</span>
                            </div>
                            {stat_row_html(ph, pa, f"👟 {t('possession')}", "#00ff87", is_pct=True)}
                            {stat_row_html(sh, sa, f"🎯 {t('shots')}", "#3b82f6")}
                            {stat_row_html(soh, soa, f"🥅 {t('shots_on_target')}", "#22c55e")}
                            {stat_row_html(fh, fa, f"🦶 {t('fouls')}", "#f59e0b")}
                            {stat_row_html(ch, ca, f"🚩 {t('corners')}", "#8b5cf6")}
                            {stat_row_html(oh, oa, f"🚫 {t('offsides')}", "#ef4444")}
                            {stat_row_html(pph, ppa, f"✅ {t('pass_accuracy')}", "#06b6d4", is_pct=True)}
                            {stat_row_html(svh, sva, f"🧤 {t('saves')}", "#f97316")}
                            <div style="margin-top:12px; display:flex; justify-content:space-between; padding: 8px 44px; background:#1a1a1d; border-radius:8px;">
                                <span style="font-size:0.85rem;">🟨 {yh} &nbsp;🟥 {rh}</span>
                                <span style="color:#71717a; font-size:0.78rem;">🃏 {t('yellow_cards')} / {t('red_cards')}</span>
                                <span style="font-size:0.85rem;">🟨 {ya} &nbsp;🟥 {ra}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

# ==========================================================
# TAB: VISÃO GERAL
# ==========================================================
with tab_overview:
    if not finished_matches:
        st.info(t('no_finished_matches'))
    else:
        home_wins = sum(1 for m in finished_matches if int(m['score'].split('-')[0]) > int(m['score'].split('-')[1]))
        away_wins = sum(1 for m in finished_matches if int(m['score'].split('-')[0]) < int(m['score'].split('-')[1]))
        draws_count = len(finished_matches) - home_wins - away_wins

        # Destaques do torneio
        hi_cols = st.columns(3)
        highlights = [
            ("green", "⚡", t('biggest_win'),
             f"{flag(biggest_win_match['home_team'])} {biggest_win_match['home_team']} {biggest_win_match['score']} {biggest_win_match['away_team']} {flag(biggest_win_match['away_team'])}" if biggest_win_match else "—",
             biggest_win_match.get('date','') if biggest_win_match else ""),
            ("blue", "🔥", t('highest_scoring'),
             f"{flag(highest_goals_match['home_team'])} {highest_goals_match['home_team']} {highest_goals_match['score']} {highest_goals_match['away_team']} {flag(highest_goals_match['away_team'])}" if highest_goals_match else "—",
             f"{highest_goals_total} gols" if highest_goals_match else ""),
            ("yellow", "⚽", t('most_efficient'),
             f"{flag(most_efficient_team)} {most_efficient_team}" if most_efficient_team else "—",
             f"{team_agg[most_efficient_team]['gf']} gols / {team_agg[most_efficient_team]['shots_on_target']} chutes no alvo" if most_efficient_team else ""),
        ]
        for col, (color, icon, label, val, sub) in zip(hi_cols, highlights):
            with col:
                st.markdown(f"""
                <div class="highlight-box {color}">
                    <div class="hl-label">{icon} {label}</div>
                    <div class="hl-value">{val}</div>
                    <div class="hl-sub">{sub}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(f"<div class='section-title'>🏆 {t('match_results')}</div>", unsafe_allow_html=True)
            fig_outcomes = go.Figure(go.Bar(
                x=[t('home_wins'), t('draws'), t('away_wins')],
                y=[home_wins, draws_count, away_wins],
                marker_color=['#00ff87', '#3b82f6', '#8b5cf6'],
                text=[home_wins, draws_count, away_wins],
                textposition='outside',
                textfont=dict(color='#ffffff', size=14, family='Outfit'),
            ))
            fig_outcomes.update_layout(**PLOTLY_DARK, height=280,
                yaxis=dict(showgrid=False, visible=False),
                xaxis=dict(showgrid=False),
                bargap=0.4)
            st.plotly_chart(fig_outcomes, use_container_width=True, config={'displayModeBar': False})

        with col_r:
            st.markdown(f"<div class='section-title'>⚽ {t('goals_by_team')}</div>", unsafe_allow_html=True)
            team_goal_list = sorted(
                [(f"{flag(k)} {k}", v['gf']) for k, v in team_agg.items()],
                key=lambda x: x[1], reverse=True
            )[:10]
            fig_goals = go.Figure(go.Bar(
                y=[x[0] for x in team_goal_list],
                x=[x[1] for x in team_goal_list],
                orientation='h',
                marker=dict(color='#3b82f6', opacity=0.85),
                text=[x[1] for x in team_goal_list],
                textposition='outside',
                textfont=dict(color='#ffffff', size=12),
            ))
            fig_goals.update_layout(**PLOTLY_DARK, height=280,
                xaxis=dict(showgrid=False, visible=False),
                yaxis=dict(tickfont=dict(size=11, color='#a1a1aa')))
            st.plotly_chart(fig_goals, use_container_width=True, config={'displayModeBar': False})

        # Gols por sede
        st.markdown(f"<div class='section-title'>🏟️ {t('venue_title')}</div>", unsafe_allow_html=True)
        venue_stats = defaultdict(lambda: {'matches': 0, 'goals': 0, 'city': ''})
        for m in finished_matches:
            st_name = m.get('stadium', 'Unknown')
            venue_stats[st_name]['matches'] += 1
            venue_stats[st_name]['goals'] += int(m['score'].split('-')[0]) + int(m['score'].split('-')[1])
            venue_stats[st_name]['city'] = m.get('city', '')

        venue_df = pd.DataFrame([
            {t('stadium'): k, t('city'): v['city'],
             t('venue_matches'): v['matches'],
             t('total_goals'): v['goals'],
             t('avg_goals_venue'): round(v['goals'] / max(v['matches'], 1), 1)}
            for k, v in venue_stats.items()
        ]).sort_values(by=t('total_goals'), ascending=False)
        st.dataframe(venue_df, hide_index=True, use_container_width=True)

# ==========================================================
# TAB: ARTILHARIA
# ==========================================================
with tab_scorers:
    if not finished_matches:
        st.info(t('no_finished_matches'))
    else:
        scorer_goals = {}
        scorer_team = {}
        for m in finished_matches:
            home_s, away_s = get_match_scorers(m)
            for (p, _) in home_s:
                scorer_goals[p] = scorer_goals.get(p, 0) + 1
                scorer_team[p] = m['home_team']
            for (p, _) in away_s:
                scorer_goals[p] = scorer_goals.get(p, 0) + 1
                scorer_team[p] = m['away_team']

        sorted_scorers = sorted(scorer_goals.items(), key=lambda x: x[1], reverse=True)
        medals = {0: ('🥇', 'gold'), 1: ('🥈', 'silver'), 2: ('🥉', 'bronze')}

        col_rank, col_chart = st.columns([1, 1])
        with col_rank:
            st.markdown(f"<div class='section-title'>👟 {t('top_scorers_title')}</div>", unsafe_allow_html=True)
            for i, (player, goals) in enumerate(sorted_scorers[:12]):
                medal, color_cls = medals.get(i, ('', ''))
                rank_display = medal if medal else str(i + 1)
                tm = scorer_team.get(player, '')
                st.markdown(f"""
                <div class="rank-row">
                    <div class="rank-pos {color_cls}">{rank_display}</div>
                    <div class="rank-player">{player}</div>
                    <div class="rank-team">{flag(tm)} {tm}</div>
                    <div class="rank-goals">{'⚽' * min(goals, 5)} {goals}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_chart:
            st.markdown(f"<div class='section-title'>📊 Top 8</div>", unsafe_allow_html=True)
            top8 = sorted_scorers[:8]
            fig_scorers = go.Figure(go.Bar(
                y=[s[0] for s in top8],
                x=[s[1] for s in top8],
                orientation='h',
                marker=dict(
                    color=[s[1] for s in top8],
                    colorscale=[[0, '#1f3a28'], [1, '#00ff87']],
                    showscale=False,
                ),
                text=[f"⚽ {s[1]}" for s in top8],
                textposition='outside',
                textfont=dict(color='#ffffff', size=12),
            ))
            fig_scorers.update_layout(**PLOTLY_DARK, height=340,
                xaxis=dict(showgrid=False, visible=False),
                yaxis=dict(tickfont=dict(size=11, color='#ffffff')))
            st.plotly_chart(fig_scorers, use_container_width=True, config={'displayModeBar': False})

# ==========================================================
# TAB: CLASSIFICAÇÃO
# ==========================================================
with tab_standings:
    if not team_agg:
        st.info(t('no_finished_matches'))
    else:
        sorted_teams = sorted(team_agg.items(),
                              key=lambda x: (x[1]['pts'], x[1]['gf'] - x[1]['ga'], x[1]['gf']),
                              reverse=True)

        st.markdown(f"<div class='section-title'>🏆 {t('tab_teams')}</div>", unsafe_allow_html=True)

        headers = [t('team'), 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'CS', 'Pts', t('form')]
        widths = [2.5, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.7, 1.5]
        hcols = st.columns(widths)
        for col, label in zip(hcols, headers):
            col.markdown(f"<div style='color:#71717a; font-size:0.7rem; font-weight:700; text-transform:uppercase;'>{label}</div>", unsafe_allow_html=True)

        for i, (team, s) in enumerate(sorted_teams):
            gd = s['gf'] - s['ga']
            gd_str = f"+{gd}" if gd > 0 else str(gd)
            gd_color = "#00ff87" if gd > 0 else ("#ef4444" if gd < 0 else "#71717a")
            # Forma (W=✅ D=⚪ L=❌): simulada pelos últimos jogos
            form_icons = []
            team_matches = [m for m in finished_matches if m['home_team'] == team or m['away_team'] == team][-5:]
            for m in team_matches:
                hs = int(m['score'].split('-')[0])
                aws = int(m['score'].split('-')[1])
                if m['home_team'] == team:
                    res = 'W' if hs > aws else ('D' if hs == aws else 'L')
                else:
                    res = 'W' if aws > hs else ('D' if hs == aws else 'L')
                icon = '🟢' if res == 'W' else ('⚪' if res == 'D' else '🔴')
                form_icons.append(icon)

            row = st.columns(widths)
            row[0].markdown(f"<span style='color:#fff; font-weight:600; font-size:0.88rem;'>{flag(team)} {team}</span>", unsafe_allow_html=True)
            for col, val in zip(row[1:9], [s['played'], s['wins'], s['draws'], s['losses'], s['gf'], s['ga'], gd_str, s['clean_sheets']]):
                color = gd_color if val == gd_str else "#a1a1aa"
                col.markdown(f"<span style='color:{color}; font-size:0.88rem;'>{val}</span>", unsafe_allow_html=True)
            row[9].markdown(f"<span style='color:#00ff87; font-weight:800; font-size:0.9rem;'>{s['pts']}</span>", unsafe_allow_html=True)
            row[10].markdown(' '.join(form_icons) if form_icons else '—', unsafe_allow_html=True)
            st.markdown("<hr style='border:none; border-top:1px solid #1e1e23; margin:2px 0;'>", unsafe_allow_html=True)

# ==========================================================
# TAB: xG & EFICIÊNCIA
# ==========================================================
with tab_xg:
    if not team_agg:
        st.info(t('no_finished_matches'))
    else:
        st.markdown(f"<div class='section-title'>🎯 {t('xg_title')}</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#141416; border:1px solid #27272a; border-radius:12px; padding:12px 16px; margin-bottom:16px; color:#71717a; font-size:0.82rem; line-height:1.6;">
            <strong style="color:#a1a1aa;">O que é xG (Expected Goals)?</strong><br>
            O xG mede a probabilidade de cada oportunidade de gol resultar em gol, considerando posição, ângulo e tipo de chute.
            Valores <span style="color:#00ff87;">acima do xG</span> indicam alto aproveitamento; abaixo indica chances desperdiçadas.
        </div>
        """, unsafe_allow_html=True)

        xg_data = []
        for team, s in team_agg.items():
            if s['played'] > 0:
                xg_data.append({
                    'team': f"{flag(team)} {team}",
                    'real_goals': s['gf'],
                    'xg': round(s['xg'], 2),
                    'diff': round(s['gf'] - s['xg'], 2),
                    'conversion': round(s['gf'] / max(s['shots_on_target'], 1) * 100, 1),
                    'shots_on_target': s['shots_on_target'],
                })
        xg_data.sort(key=lambda x: x['real_goals'], reverse=True)

        # Gráfico xG vs Real Goals
        teams_xg = [d['team'] for d in xg_data[:12]]
        real_vals = [d['real_goals'] for d in xg_data[:12]]
        xg_vals = [d['xg'] for d in xg_data[:12]]

        fig_xg = go.Figure()
        fig_xg.add_trace(go.Bar(name='Gols Reais', x=teams_xg, y=real_vals,
                                marker_color='#00ff87', opacity=0.9,
                                text=real_vals, textposition='outside',
                                textfont=dict(color='#ffffff', size=11)))
        fig_xg.add_trace(go.Bar(name='xG', x=teams_xg, y=xg_vals,
                                marker_color='#3b82f6', opacity=0.7,
                                text=[f"{v:.1f}" for v in xg_vals], textposition='outside',
                                textfont=dict(color='#93c5fd', size=11)))
        fig_xg.update_layout(
            **PLOTLY_DARK, barmode='group', height=340,
            legend=dict(orientation='h', y=1.1, x=0, font=dict(color='#a1a1aa')),
        )
        st.plotly_chart(fig_xg, use_container_width=True, config={'displayModeBar': False})

        # Scatter xG vs Gols — over/underperformers
        st.markdown(f"<div class='section-title'>📍 Eficiência: xG vs Gols Reais</div>", unsafe_allow_html=True)
        fig_scatter = go.Figure()
        scatter_colors = ['#00ff87' if d['diff'] >= 0 else '#ef4444' for d in xg_data]
        fig_scatter.add_trace(go.Scatter(
            x=[d['xg'] for d in xg_data],
            y=[d['real_goals'] for d in xg_data],
            mode='markers+text',
            text=[d['team'] for d in xg_data],
            textposition='top center',
            textfont=dict(size=9, color='#a1a1aa'),
            marker=dict(size=12, color=scatter_colors, opacity=0.85,
                        line=dict(width=1, color='#27272a')),
        ))
        # Linha diagonal (xG = gols reais)
        max_val = max(max(d['xg'] for d in xg_data), max(d['real_goals'] for d in xg_data)) + 0.5
        fig_scatter.add_trace(go.Scatter(
            x=[0, max_val], y=[0, max_val],
            mode='lines', line=dict(color='#52525b', dash='dash', width=1),
            name='xG = Gols', showlegend=True
        ))
        fig_scatter.update_layout(
            **PLOTLY_DARK, height=380,
            xaxis=dict(title=dict(text=t('xg_label'), font=dict(color='#71717a')), gridcolor='#1e1e23'),
            yaxis=dict(title=dict(text=t('real_goals'), font=dict(color='#71717a')), gridcolor='#1e1e23'),
            legend=dict(orientation='h', y=1.1, font=dict(color='#a1a1aa')),
            annotations=[
                dict(x=max_val*0.25, y=max_val*0.75, text="🟢 Acima do xG", showarrow=False,
                     font=dict(color='#00ff87', size=10)),
                dict(x=max_val*0.75, y=max_val*0.25, text="🔴 Abaixo do xG", showarrow=False,
                     font=dict(color='#ef4444', size=10)),
            ]
        )
        st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})

        # Tabela de conversão
        st.markdown(f"<div class='section-title'>📊 Taxa de Conversão</div>", unsafe_allow_html=True)
        conv_df = pd.DataFrame([{
            t('team'): d['team'],
            t('real_goals'): d['real_goals'],
            t('xg_label'): d['xg'],
            '± xG': f"+{d['diff']:.1f}" if d['diff'] >= 0 else f"{d['diff']:.1f}",
            t('shots_on_target'): d['shots_on_target'],
            t('conversion'): f"{d['conversion']:.1f}%",
        } for d in xg_data]).head(15)
        st.dataframe(conv_df, hide_index=True, use_container_width=True)

# ==========================================================
# TAB: GOLS POR MINUTO
# ==========================================================
with tab_timeline:
    if not finished_matches:
        st.info(t('no_finished_matches'))
    else:
        st.markdown(f"<div class='section-title'>⏱️ {t('goals_by_minute')}</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#141416; border:1px solid #27272a; border-radius:12px; padding:12px 16px; margin-bottom:16px; color:#71717a; font-size:0.82rem;">
            Distribuição dos gols ao longo dos 90 minutos — revela os momentos mais decisivos do torneio.
        </div>
        """, unsafe_allow_html=True)

        intervals = ['0-15', '16-30', '31-45', '46-60', '61-75', '76-90']
        interval_goals = {k: 0 for k in intervals}
        all_goal_minutes = []

        for m in finished_matches:
            home_s, away_s = get_match_scorers(m)
            for (_, minute) in home_s + away_s:
                all_goal_minutes.append(minute)
                if minute <= 15:
                    interval_goals['0-15'] += 1
                elif minute <= 30:
                    interval_goals['16-30'] += 1
                elif minute <= 45:
                    interval_goals['31-45'] += 1
                elif minute <= 60:
                    interval_goals['46-60'] += 1
                elif minute <= 75:
                    interval_goals['61-75'] += 1
                else:
                    interval_goals['76-90'] += 1

        # Gráfico de barras por intervalo
        col_int, col_dist = st.columns(2)
        with col_int:
            colors_intervals = ['#1f3a28', '#25502d', '#2a6633', '#2f7c3a', '#34923f', '#00ff87']
            fig_intervals = go.Figure(go.Bar(
                x=intervals,
                y=list(interval_goals.values()),
                marker_color=colors_intervals,
                text=list(interval_goals.values()),
                textposition='outside',
                textfont=dict(color='#ffffff', size=13),
            ))
            fig_intervals.update_layout(
                **PLOTLY_DARK, height=300,
                title=dict(text="Gols por Intervalo de 15 min", font=dict(color='#a1a1aa', size=13)),
                xaxis=dict(tickfont=dict(color='#a1a1aa')),
                yaxis=dict(showgrid=True, gridcolor='#1e1e23', visible=False),
            )
            st.plotly_chart(fig_intervals, use_container_width=True, config={'displayModeBar': False})

        with col_dist:
            if all_goal_minutes:
                fig_hist = go.Figure(go.Histogram(
                    x=all_goal_minutes,
                    nbinsx=18,
                    marker=dict(
                        color=all_goal_minutes,
                        colorscale=[[0, '#1a2f1e'], [0.5, '#00aa5e'], [1, '#00ff87']],
                        line=dict(width=0.5, color='#141416')
                    ),
                    opacity=0.85,
                ))
                fig_hist.update_layout(
                    **PLOTLY_DARK, height=300,
                    title=dict(text="Histograma completo de gols (min 1-90)", font=dict(color='#a1a1aa', size=13)),
                    xaxis=dict(title=dict(text=t('minute'), font=dict(color='#71717a')), tickfont=dict(color='#a1a1aa')),
                    yaxis=dict(title=dict(text='Gols', font=dict(color='#71717a')), gridcolor='#1e1e23'),
                    bargap=0.05,
                )
                st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False})

        # Destaques por intervalo
        peak_interval = max(interval_goals, key=interval_goals.get)
        st.markdown(f"""
        <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:8px;">
            <div class="highlight-box green">
                <div class="hl-label">⏱️ Intervalo mais decisivo</div>
                <div class="hl-value">{peak_interval} min</div>
                <div class="hl-sub">{interval_goals[peak_interval]} gols</div>
            </div>
            <div class="highlight-box blue">
                <div class="hl-label">⚽ Total de gols simulados</div>
                <div class="hl-value">{len(all_goal_minutes)}</div>
                <div class="hl-sub">em {len(finished_matches)} partidas</div>
            </div>
            <div class="highlight-box yellow">
                <div class="hl-label">📊 Gols no 2º tempo</div>
                <div class="hl-value">{interval_goals['46-60']+interval_goals['61-75']+interval_goals['76-90']}</div>
                <div class="hl-sub">vs {interval_goals['0-15']+interval_goals['16-30']+interval_goals['31-45']} no 1º tempo</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================================
# TAB: DISCIPLINA
# ==========================================================
with tab_discipline:
    if not team_agg:
        st.info(t('no_finished_matches'))
    else:
        st.markdown(f"<div class='section-title'>🔴 {t('discipline_title')}</div>", unsafe_allow_html=True)

        disc_data = sorted(
            [(team, s) for team, s in team_agg.items() if s['played'] > 0],
            key=lambda x: (x[1]['yellow'] * 1 + x[1]['red'] * 3 + x[1]['fouls'] * 0.1),
            reverse=True
        )

        col_disc, col_fouls = st.columns(2)
        with col_disc:
            fig_disc = go.Figure()
            fig_disc.add_trace(go.Bar(
                name='🟨 Amarelos',
                y=[f"{flag(d[0])} {d[0]}" for d in disc_data[:10]],
                x=[d[1]['yellow'] for d in disc_data[:10]],
                orientation='h',
                marker_color='#f59e0b',
                text=[d[1]['yellow'] for d in disc_data[:10]],
                textposition='outside',
                textfont=dict(color='#ffffff'),
            ))
            fig_disc.add_trace(go.Bar(
                name='🟥 Vermelhos',
                y=[f"{flag(d[0])} {d[0]}" for d in disc_data[:10]],
                x=[d[1]['red'] for d in disc_data[:10]],
                orientation='h',
                marker_color='#ef4444',
                text=[d[1]['red'] for d in disc_data[:10]],
                textposition='outside',
                textfont=dict(color='#ffffff'),
            ))
            fig_disc.update_layout(
                **PLOTLY_DARK, barmode='stack', height=360,
                title=dict(text="Cartões por Seleção", font=dict(color='#a1a1aa', size=13)),
                xaxis=dict(showgrid=False, visible=False),
                yaxis=dict(tickfont=dict(size=10, color='#d4d4d8')),
                legend=dict(orientation='h', y=1.08, font=dict(color='#a1a1aa', size=11)),
            )
            st.plotly_chart(fig_disc, use_container_width=True, config={'displayModeBar': False})

        with col_fouls:
            fouls_data = sorted(disc_data, key=lambda x: x[1]['fouls'], reverse=True)[:10]
            fig_fouls = go.Figure(go.Bar(
                y=[f"{flag(d[0])} {d[0]}" for d in fouls_data],
                x=[d[1]['fouls'] for d in fouls_data],
                orientation='h',
                marker=dict(
                    color=[d[1]['fouls'] for d in fouls_data],
                    colorscale=[[0, '#1a1500'], [1, '#f59e0b']],
                    showscale=False,
                ),
                text=[d[1]['fouls'] for d in fouls_data],
                textposition='outside',
                textfont=dict(color='#ffffff'),
            ))
            fig_fouls.update_layout(
                **PLOTLY_DARK, height=360,
                title=dict(text=f"🦶 Faltas Cometidas", font=dict(color='#a1a1aa', size=13)),
                xaxis=dict(showgrid=False, visible=False),
                yaxis=dict(tickfont=dict(size=10, color='#d4d4d8')),
            )
            st.plotly_chart(fig_fouls, use_container_width=True, config={'displayModeBar': False})

        # Tabela resumo disciplina
        disc_df = pd.DataFrame([{
            t('team'): f"{flag(team)} {team}",
            'Jogos': s['played'],
            '🟨 Amarelos': s['yellow'],
            '🟥 Vermelhos': s['red'],
            '🦶 Faltas': s['fouls'],
            'Faltas/Jogo': round(s['fouls'] / max(s['played'], 1), 1),
            'Pontos Disc.': s['yellow'] + s['red'] * 3,
        } for team, s in disc_data]).sort_values('Pontos Disc.', ascending=False)
        st.dataframe(disc_df, hide_index=True, use_container_width=True)

# ==========================================================
# TAB: COMPARADOR
# ==========================================================
with tab_compare:
    if len(team_agg) < 2:
        st.info(t('no_finished_matches'))
    else:
        st.markdown(f"<div class='section-title'>⚖️ {t('compare_title')}</div>", unsafe_allow_html=True)
        all_teams = sorted(team_agg.keys())
        default_a = all_teams.index('Brazil') if 'Brazil' in all_teams else 0
        default_b = all_teams.index('Argentina') if 'Argentina' in all_teams else 1

        col_sa, col_sb = st.columns(2)
        with col_sa:
            team_a = st.selectbox(f"🏳️ {t('select_home')}", options=all_teams, index=default_a, key="compare_a")
        with col_sb:
            remaining = [t for t in all_teams if t != team_a]
            team_b_default = remaining.index('Argentina') if 'Argentina' in remaining else 0
            team_b = st.selectbox(f"🏳️ {t('select_away')}", options=remaining, index=team_b_default, key="compare_b")

        sa = team_agg[team_a]
        sb = team_agg[team_b]

        def normalize(val_a, val_b, higher_is_better=True):
            total = val_a + val_b
            if total == 0:
                return 50, 50
            pct_a = (val_a / total) * 100
            if not higher_is_better:
                pct_a = 100 - pct_a
            return round(pct_a, 1), round(100 - pct_a, 1)

        # Placar head-to-head
        h2h = [m for m in finished_matches
               if (m['home_team'] == team_a and m['away_team'] == team_b) or
                  (m['home_team'] == team_b and m['away_team'] == team_a)]

        col_head, col_radar = st.columns([1, 1.2])

        with col_head:
            # Stats side by side
            comparisons = [
                ("⚽", t('goals'), sa['gf'], sb['gf'], True),
                ("🎯", t('shots'), sa['shots'], sb['shots'], True),
                ("🥅", t('shots_on_target'), sa['shots_on_target'], sb['shots_on_target'], True),
                ("👟", t('possession'), int(sa['possession']/max(sa['played'],1)), int(sb['possession']/max(sb['played'],1)), True),
                ("🏆", "Pts", sa['pts'], sb['pts'], True),
                ("✅", t('pass_accuracy'), int(sum(sa['pass_acc'])/max(len(sa['pass_acc']),1)), int(sum(sb['pass_acc'])/max(len(sb['pass_acc']),1)), True),
                ("🧤", t('saves'), sa['saves'], sb['saves'], True),
                ("🦶", t('fouls'), sa['fouls'], sb['fouls'], False),
                ("🟨", t('yellow_cards'), sa['yellow'], sb['yellow'], False),
                ("🎯", "xG", round(sa['xg'], 1), round(sb['xg'], 1), True),
            ]

            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                <div style="font-weight:800; color:#fff; font-size:1rem;">{flag(team_a)} {team_a}</div>
                <div style="font-weight:800; color:#fff; font-size:1rem;">{team_b} {flag(team_b)}</div>
            </div>
            """, unsafe_allow_html=True)

            for icon, label, va, vb, hib in comparisons:
                pct_a, pct_b = normalize(va, vb, hib)
                color_a = "#00ff87" if (va > vb and hib) or (va < vb and not hib) else ("#ef4444" if (va < vb and hib) or (va > vb and not hib) else "#71717a")
                color_b = "#00ff87" if (vb > va and hib) or (vb < va and not hib) else ("#ef4444" if (vb < va and hib) or (vb > va and not hib) else "#71717a")
                st.markdown(f"""
                <div class="stat-row" style="margin:6px 0;">
                    <div style="font-weight:700; color:{color_a}; min-width:36px;">{va}</div>
                    <div class="progress-container"><div class="progress-fill" style="width:{pct_a}%; background:{'#00ff87' if color_a=='#00ff87' else '#27272a'};"></div></div>
                    <div style="color:#71717a; font-size:0.76rem; min-width:110px; text-align:center;">{icon} {label}</div>
                    <div class="progress-container" style="transform:scaleX(-1);"><div class="progress-fill" style="width:{pct_b}%; background:{'#3b82f6' if color_b=='#00ff87' else '#27272a'};"></div></div>
                    <div style="font-weight:700; color:{color_b}; min-width:36px; text-align:right;">{vb}</div>
                </div>
                """, unsafe_allow_html=True)

            if h2h:
                st.markdown(f"<div style='margin-top:14px; color:#71717a; font-size:0.75rem; font-weight:700; text-transform:uppercase;'>🤝 Head to Head</div>", unsafe_allow_html=True)
                for m in h2h:
                    st.markdown(f"""
                    <div class="scorer-item" style="text-align:center; font-weight:600;">
                        {flag(m['home_team'])} {m['home_team']} <span style="color:#00ff87;">{m['score']}</span> {m['away_team']} {flag(m['away_team'])}
                        <span style="color:#52525b; font-size:0.75rem;"> — {m['date']}</span>
                    </div>
                    """, unsafe_allow_html=True)

        with col_radar:
            # Radar Chart
            def to_100(val_a, val_b, higher_is_better=True):
                total = max(val_a + val_b, 0.01)
                r = (val_a / total) * 100
                return round(r if higher_is_better else 100 - r, 1)

            categories = [
                t('radar_attack'), t('radar_defense'), t('radar_possession'),
                t('radar_discipline'), t('radar_xg'), t('radar_efficiency')
            ]
            vals_a = [
                to_100(sa['gf'], sb['gf']),
                to_100(sb['ga'], sa['ga']),
                to_100(int(sa['possession']/max(sa['played'],1)), int(sb['possession']/max(sb['played'],1))),
                to_100(sb['yellow'] + sb['red']*3, sa['yellow'] + sa['red']*3),
                to_100(sa['xg'], sb['xg']),
                to_100(sa['gf'] / max(sa['shots_on_target'],1), sb['gf'] / max(sb['shots_on_target'],1)),
            ]
            vals_b = [round(100 - v, 1) for v in vals_a]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_a + [vals_a[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(0, 255, 135, 0.15)',
                line=dict(color='#00ff87', width=2),
                name=f"{flag(team_a)} {team_a}",
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_b + [vals_b[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(59, 130, 246, 0.15)',
                line=dict(color='#3b82f6', width=2),
                name=f"{flag(team_b)} {team_b}",
            ))
            fig_radar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Outfit, sans-serif', color='#a1a1aa'),
                polar=dict(
                    bgcolor='rgba(20,20,22,0.8)',
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor='#27272a',
                                   tickfont=dict(size=9, color='#52525b'), showticklabels=False),
                    angularaxis=dict(gridcolor='#27272a', tickfont=dict(size=11, color='#d4d4d8')),
                ),
                legend=dict(orientation='h', y=-0.1, x=0.5, xanchor='center', font=dict(color='#a1a1aa', size=11)),
                margin=dict(l=20, r=20, t=30, b=40),
                height=380,
            )
            st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
