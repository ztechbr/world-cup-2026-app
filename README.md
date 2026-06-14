# 🏆 World Cup 2026 — Smartwatch Simulator & Analytics Dashboard

> **Demonstração interativa de alto nível** que combina um simulador de smartwatch circular com um dashboard analítico profissional de estatísticas da Copa do Mundo FIFA 2026.

![License](https://img.shields.io/badge/license-MIT-green) ![Node](https://img.shields.io/badge/node-20-blue) ![Python](https://img.shields.io/badge/python-3.10-blue) ![Streamlit](https://img.shields.io/badge/streamlit-1.30%2B-red) ![Vite](https://img.shields.io/badge/vite-5-purple) ![Docker](https://img.shields.io/badge/docker-compose-blue)

---

## 📋 Visão Geral

O projeto é composto por **dois serviços independentes** que se comunicam internamente via proxy reverso Nginx:

| Serviço | Tecnologia | Porta | Função |
|---|---|---|---|
| **Simulador Smartwatch** | Vite + Vanilla JS + Nginx | 80 | Interface circular de smartwatch com simulação ao vivo |
| **Dashboard Analytics** | Python + Streamlit + Plotly | 90 | 8 tabs de estatísticas profissionais do torneio |

---

## ✨ Funcionalidades

### ⌚ Smartwatch Simulator
- **Interface circular** fiel a um smartwatch real, com ponteiros analógicos animados
- **Swipe lateral** para navegar entre grupos da Copa (A → L)
- **Botão coroa** para abrir/fechar o painel de controle
- **Painel lateral glassmorphism** com simulação de partidas ao vivo
- **Forçar sincronização** com a API externa de partidas
- **Modo offline** automático com fallback nos 104 jogos pré-carregados
- **Botão Statistics** que abre o dashboard em um modal com iframe responsivo
- **5 idiomas** sincronizados: PT, EN, IT, ES, FR

### 📊 Analytics Dashboard (8 Tabs)

| Tab | Conteúdo |
|---|---|
| 📅 **Calendário** | Navegação por dia, cards de partida com 10 estatísticas inline ao expandir |
| 📊 **Visão Geral** | Destaques automáticos, gols por seleção, estatísticas por estádio/sede |
| 👟 **Artilharia** | Top 15 com medalhas e gráfico de barras graduado |
| 🏆 **Classificação** | Tabela completa com P/V/E/D/GF/GA/SD/CS/Pts + forma recente (🟢⚪🔴) |
| 🎯 **xG & Eficiência** | Expected Goals vs Gols Reais, scatter de over/underperformers, taxa de conversão |
| ⏱️ **Gols por Minuto** | Histograma 0-90min + distribuição por intervalos de 15min |
| 🔴 **Disciplina** | Ranking de cartões e faltas por seleção com Plotly interativo |
| ⚖️ **Comparador** | Radar Chart interativo com seleção de 2 times + 10 métricas lado a lado |

---

## 🏗️ Arquitetura do Sistema

### Diagrama de Containers

```
                        ┌─────────────────────────────────────┐
                        │     Usuário / Navegador             │
                        └─────────────────────────────────────┘
                                        │
                                        │ HTTPS (443)
                                        ▼
                        ┌─────────────────────────────────────┐
                        │    Easypanel / Traefik Router        │
                        │    (SSL Termination + Load Bal.)    │
                        └─────────────────────────────────────┘
                                        │
                                        │ HTTP (80)
                                        ▼
                   ┌────────────────────────────────────────────────┐
                   │         worldcup-simulator                      │
                   │         Nginx (Alpine) — porta 80               │
                   │                                                  │
                   │  location /        → /usr/share/nginx/html      │
                   │  location /api/    → proxy externo (API Copa)   │
                   │  location /stats   → proxy interno :90          │
                   └────────────────┬───────────────────────────────┘
                                    │  rede Docker interna
                                    │  http://worldcup-stats:90
                                    ▼
                   ┌────────────────────────────────────────────────┐
                   │         worldcup-stats                          │
                   │         Python 3.10 + Streamlit — porta 90      │
                   │         baseUrlPath = "stats"                   │
                   └────────────────────────────────────────────────┘
```

### Fluxo de Dados

```
  ┌─────────────┐       GET /api/matches       ┌─────────────────────────────┐
  │  app.js     │ ─────────────────────────────► Nginx /api/ proxy           │
  │  (Frontend) │                               │ → api.worldcup26.host/...  │
  └─────────────┘ ◄──────────────────────────── API externa + X-Token        │
        │                                       └─────────────────────────────┘
        │   Fallback (offline)
        ▼
  ┌─────────────────────┐         GET /stats/?language=pt
  │ fallback-matches.js │    ─────────────────────────────────────►
  │ (104 jogos estáticos│         Nginx → Streamlit (porta 90)
  └─────────────────────┘    ◄─────────────────────────────────────
                                    Dashboard HTML + WebSocket
```

---

## 📁 Estrutura de Arquivos

```
world-cup-2026-app/
│
├── 📄 index.html                   # Estrutura HTML principal — smartwatch + modal + painel
│
├── 🐳 Dockerfile                   # Build multi-stage: Vite → Nginx (Alpine)
├── 🐳 Dockerfile.stats             # Imagem Python 3.10-slim + Streamlit + Plotly
├── 🐳 docker-compose.yml           # Orquestração produção (sem ports/container_name)
├── 🐳 docker-compose.local.yml     # Override local com mapeamento de portas
│
├── 🌐 nginx.conf                   # Proxy reverso: / estático + /api/ externo + /stats/ Streamlit
├── ⚙️  vite.config.js               # Dev server Vite com proxy local para /api/
├── 📦 package.json                 # Dependências: vite@5
│
├── 🐍 stats_app.py                 # Dashboard Streamlit completo (8 tabs, +1200 linhas)
│
├── .streamlit/
│   └── ⚙️  config.toml             # Porta 90, baseUrlPath=stats, tema neon dark
│
├── public/
│   └── 🌐 translate.xml            # Dicionário central de traduções (PT/EN/IT/ES/FR)
│
└── src/
    ├── 🎨 styles.css               # Design system: glassmorphism, neon green, smartwatch frame
    ├── 🧠 app.js                   # Controlador principal: eventos, swipe, iframe, i18n
    ├── 🔌 api.js                   # Cliente API: fetch + cache + fallback automático
    ├── ⚽ simulator.js              # Motor de simulação: eventos ao vivo, placar em tempo real
    ├── 🛠️  utils.js                 # Utilitários: traduções, emojis de bandeira, standings
    └── 📊 fallback-matches.js      # Base estática: 104 jogos da Copa 2026 (modo offline)
```

---

## 🛠️ Stack Tecnológico

### Frontend (Smartwatch Simulator)
| Tecnologia | Versão | Uso |
|---|---|---|
| **HTML5** | — | Estrutura da interface circular |
| **Vanilla CSS** | — | Glassmorphism, animações, design system |
| **Vanilla JS (ESM)** | — | Lógica de simulação, swipe, eventos |
| **Vite** | 5.x | Build e dev server com HMR |
| **Nginx** | Alpine | Servidor de produção + proxy reverso |

### Backend (Analytics Dashboard)
| Tecnologia | Versão | Uso |
|---|---|---|
| **Python** | 3.10 | Runtime |
| **Streamlit** | 1.30+ | Framework de dashboard |
| **Plotly** | latest | Gráficos interativos (radar, scatter, histograma) |
| **Pandas** | latest | Processamento e tabelas de dados |
| **Requests** | latest | Fetch da API externa de partidas |

### Infraestrutura
| Tecnologia | Uso |
|---|---|
| **Docker** | Containers isolados por serviço |
| **Nginx Alpine** | Servidor web + proxy reverso interno |
| **Easypanel** | PaaS para deploy via Git ou Docker Compose |
| **Traefik** | SSL/TLS automático e roteamento no Easypanel |

---

## 🔌 Comunicação Inter-Serviços

O Nginx atua como **único ponto de entrada público** e roteia requisições internamente:

```nginx
# Conteúdo estático (smartwatch frontend)
location / {
    root /usr/share/nginx/html;
    try_files $uri $uri/ /index.html;
}

# Proxy da API externa (evita CORS no browser)
location /api/ {
    proxy_pass https://api-copa26.easypanel.host/;
    proxy_set_header X-Token "COPA26!";
}

# Proxy interno para o Streamlit (mesma rede Docker)
location /stats {
    set $stats_upstream worldcup-stats;
    proxy_pass http://$stats_upstream:90;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";   # WebSocket (necessário para Streamlit)
    proxy_buffering off;                      # Streaming em tempo real
}
```

> **Por que proxy reverso?** Evita Mixed Content (HTTP/HTTPS), centraliza SSL, elimina exposição de portas internas e permite que o iframe do dashboard seja carregado sem bloqueio do navegador.

---

## 🌍 Internacionalização (i18n)

Todo o ecossistema compartilha um **dicionário XML centralizado** em `public/translate.xml`:

```xml
<translations>
  <key name="countries_title">
    <pt>Países</pt>
    <en>Countries</en>
    <it>Paesi</it>
    <es>Países</es>
    <fr>Pays</fr>
  </key>
  <!-- ... 60+ chaves traduzidas -->
</translations>
```

O idioma ativo é passado via **query parameter** na URL:

```
https://seu-dominio.com/?language=pt
https://seu-dominio.com/stats/?language=es
```

O `app.js` detecta o idioma e injeta `?language=<lang>` no src do iframe do Streamlit automaticamente. O `stats_app.py` lê o parâmetro via `st.query_params` e renderiza todo o dashboard no idioma correspondente.

**Idiomas suportados:** 🇧🇷 PT · 🇺🇸 EN · 🇮🇹 IT · 🇪🇸 ES · 🇫🇷 FR

---

## 📊 Estatísticas Disponíveis no Dashboard

### Por Partida (ao expandir no Calendário)
| Estatística | Descrição |
|---|---|
| ⚽ Artilheiros | Jogadores com minuto do gol simulado |
| 👟 Posse de Bola | % por equipe com barra visual proporcional |
| 🎯 Chutes Totais | Total de tentativas |
| 🥅 Chutes no Alvo | Finalizações dentro do gol |
| 🦶 Faltas | Infrações cometidas |
| 🚩 Escanteios | Cobranças de canto |
| 🚫 Impedimentos | Posições de offside detectadas |
| ✅ Precisão de Passe | % de passes completados |
| 🧤 Defesas do Goleiro | Saves realizados |
| 🎯 xG inline | Expected Goals de cada equipe |

### Pelo Torneio (tabs globais)
| Métrica | Tab |
|---|---|
| xG vs Gols Reais (over/underperformers) | 🎯 xG & Eficiência |
| Scatter plot de eficiência com diagonal de referência | 🎯 xG & Eficiência |
| Taxa de conversão (gols / chutes no alvo) | 🎯 xG & Eficiência |
| Histograma de gols por minuto (0–90) | ⏱️ Gols por Minuto |
| Distribuição por intervalo de 15 min | ⏱️ Gols por Minuto |
| Ranking de cartões por seleção (empilhado) | 🔴 Disciplina |
| Ranking de faltas por seleção | 🔴 Disciplina |
| Pontos disciplinares (🟨×1 + 🟥×3) | 🔴 Disciplina |
| Radar Chart comparativo (6 dimensões) | ⚖️ Comparador |
| Head-to-head histórico | ⚖️ Comparador |
| Saldo de gols, forma recente, clean sheets | 🏆 Classificação |
| Estatísticas por estádio/sede | 📊 Visão Geral |
| Maior goleada e jogo com mais gols | 📊 Visão Geral |

---

## 🚀 Executar Localmente

### Pré-requisitos
- [Docker](https://www.docker.com/) + Docker Compose
- [Node.js 20+](https://nodejs.org/) (para desenvolvimento frontend)
- [Python 3.10+](https://python.org/) (para desenvolvimento do dashboard)

### Opção 1: Docker Compose (Recomendado)

```bash
# Clona o repositório
git clone https://github.com/ztechbr/world-cup-2026-app.git
cd world-cup-2026-app

# Sobe os dois containers com mapeamento local de portas
docker compose -f docker-compose.yml -f docker-compose.local.yml up --build
```

| Serviço | URL |
|---|---|
| Smartwatch + Estatísticas | http://localhost:3000 |
| Dashboard direto | http://localhost:3000/stats/ |
| Streamlit standalone | http://localhost:90/stats/ |

### Opção 2: Serviços Separados (Desenvolvimento)

**Terminal 1 — Frontend:**
```bash
npm install
npm run dev
# Acessar: http://localhost:3000
```

**Terminal 2 — Dashboard:**
```bash
pip install streamlit pandas requests plotly
streamlit run stats_app.py \
  --server.port=90 \
  --server.baseUrlPath=stats \
  --server.enableCORS=false
# Acessar: http://localhost:90/stats/
```

---

## ☁️ Deploy no Easypanel

### Método A: Dois Apps Separados (Recomendado)

> Garante isolamento, rebuild independente e menos conflitos de configuração.

**App 1 — Simulador (worldcup2026demo)**

| Campo | Valor |
|---|---|
| Source | Git → branch `main` |
| Dockerfile Path | `Dockerfile` |
| Domínio Público | Porta **80** |

**App 2 — Estatísticas (worldcup-stats)**

| Campo | Valor |
|---|---|
| Source | Mesmo repositório Git → branch `main` |
| Dockerfile Path | `Dockerfile.stats` |
| Domínio Público | ❌ **Nenhum** — acessado apenas internamente |

> ⚠️ **Importante:** O App do Streamlit **deve ser nomeado exatamente `worldcup-stats`** no Easypanel. Este nome é usado como hostname DNS interno pelo Nginx para resolver `http://worldcup-stats:90`.

> ✅ Ambos os Apps devem estar no **mesmo projeto Easypanel** para compartilharem a rede Docker interna.

### Método B: Docker Compose via Easypanel

1. Criar serviço do tipo **Docker Compose** no Easypanel
2. Apontar para o repositório Git (branch `main`)
3. Arquivo compose: `docker-compose.yml`
4. Configurar domínio público → serviço `worldcup-simulator` → porta `80`

> ℹ️ Os avisos `container_name` e `ports` exibidos no log do Easypanel são normais — vêm do `docker-compose.override.yml` gerado automaticamente pelo Easypanel e **não afetam o funcionamento**.

---

## 🔗 Embed via Iframe

O dashboard pode ser incorporado em qualquer portal ou site externo:

```html
<!-- Dashboard completo com idioma em português -->
<iframe
  src="https://seu-dominio.easypanel.host/stats/?language=pt"
  width="100%"
  height="800px"
  style="border: none; border-radius: 16px; background: #09090b;"
  allow="fullscreen">
</iframe>
```

**Parâmetros de URL suportados:**

| Parâmetro | Valores | Exemplo |
|---|---|---|
| `language` | `pt`, `en`, `it`, `es`, `fr` | `?language=pt` |

---

## 🔒 Variáveis de Ambiente e Configurações

| Variável | Localização | Descrição |
|---|---|---|
| `X-Token` | `nginx.conf` + `stats_app.py` | Token de autenticação da API externa |
| API URL | `stats_app.py` linha 312 | Endpoint de partidas ao vivo |
| `baseUrlPath` | `Dockerfile.stats` CMD | Prefixo `/stats` do Streamlit |
| Porta Streamlit | `Dockerfile.stats` CMD | `90` |
| Porta Nginx | `Dockerfile` EXPOSE | `80` |

---

## 🗺️ Modo Offline & Fallback

O sistema possui estratégia de fallback em duas camadas:

```
1. Tenta buscar partidas da API externa (timeout: 5s)
   └── Se falhar →
       2. Lê src/fallback-matches.js (104 jogos pré-definidos)
          └── Se falhar → retorna lista vazia com aviso
```

O arquivo `fallback-matches.js` contém todos os jogos da fase de grupos da Copa 2026 (11 Jun – 2 Jul 2026) com estadios, cidades, países anfitriões (USA, Canada, Mexico), horários e grupos A–L.

---

## 📱 Compatibilidade

| Plataforma | Suporte |
|---|---|
| Chrome / Edge (desktop) | ✅ Completo |
| Firefox (desktop) | ✅ Completo |
| Safari (desktop) | ✅ Completo |
| Chrome / Safari (mobile) | ✅ Swipe + touch |
| Modo escuro | ✅ Nativo (design dark-first) |
| iframe em site externo | ✅ CORS desativado |

---

## 📝 Licença

MIT © 2026 — Projeto de demonstração técnica de alto nível para Copa do Mundo FIFA 2026.
