# Smartwatch Copa do Mundo 2026 - Simulador & Estatísticas

Esta é uma aplicação web de alta fidelidade que simula um aplicativo de relógio inteligente circular para consulta e simulação de partidas da Copa do Mundo de 2026, integrada a um **Dashboard de Estatísticas** dinâmico desenvolvido em Python Streamlit.

A interface exibe um relógio interativo (com suporte a swipe lateral para navegação e botão coroa funcional), um painel de controle lateral translúcido (glassmorphism) para simulação de jogos ao vivo, e um botão **Statistics** para abrir o dashboard analítico em um iframe/modal responsivo.

---

## 🔌 Arquitetura de Proxy Reverso (Como tudo se conecta)

Para evitar conflitos de portas, simplificar o suporte a HTTPS/SSL e contornar erros de **Mixed Content** (conteúdo misto HTTP/HTTPS) nos navegadores, o projeto utiliza uma arquitetura de proxy reverso unificada sob o domínio principal:

```text
                  [ Usuário / Navegador ]
                             │
                             ▼ (HTTPS / Porta 443)
                 [ Easypanel Router (Traefik) ]
                             │
                             ▼ (HTTP / Porta 80)
            ┌───────────────────────────────────┐
            │   worldcup-simulator (Nginx)      │
            │                                   │
            ├───────────────┬───────────────────┤
            │ Caminho: /    │ Caminho: /stats/  │
            └───────┬───────┴─────────┬─────────┘
                    │                 │
                    ▼ (Estático)      ▼ (Proxy Reverso Interno)
              [ Smartwatch ]    [ worldcup-stats (Porta 90) ]
```

* **Nginx (Porta 80) como Porta de Entrada:** O Nginx gerencia todo o tráfego público.
  * Chamadas à raiz (`/`) ou arquivos de código (HTML/JS/CSS) são entregues diretamente como conteúdo estático.
  * Chamadas para o subcaminho `/stats/` são interceptadas e repassadas internamente pelo Docker para o contêiner do Python Streamlit na porta `90`.
* **Fim do Conflito de Portas:** O Easypanel só precisa expor a porta `80` do simulador. Toda a comunicação com o Streamlit ocorre na rede interna do Docker.

---

## 🚀 Como Executar o Projeto Localmente

Você pode rodar o ecossistema completo do projeto localmente de duas maneiras: utilizando Docker Compose (Recomendado) ou executando os serviços manualmente.

### Opção 1: Via Docker Compose (Rápido & Isolado)

Certifique-se de ter o Docker e o Docker Compose instalados em sua máquina.

1. **Inicie o ambiente:**
   No diretório raiz do projeto, execute o comando:
   ```bash
   docker-compose up --build
   ```
   Isso construirá e iniciará ambos os contêineres:
   * **Simulador Smartwatch (Frontend Vite/Nginx):** Disponível em [http://localhost:3000](http://localhost:3000). O subcaminho das estatísticas estará ativo em [http://localhost:3000/stats/](http://localhost:3000/stats/).
   * **Dashboard de Estatísticas (Python Streamlit):** Disponível internamente em [http://localhost:90](http://localhost:90).

---

### Opção 2: Execução Manual

#### Serviço 1: Simulador Smartwatch (Vite + Javascript)
1. Instale as dependências:
   ```bash
   npm install
   ```
2. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```
3. Acesse no navegador em [http://localhost:3000](http://localhost:3000).

#### Serviço 2: Dashboard de Estatísticas (Python Streamlit)
1. Instale as dependências necessárias do Python:
   ```bash
   pip install streamlit pandas requests
   ```
2. Inicie o servidor Streamlit:
   ```bash
   streamlit run stats_app.py
   ```
3. Acesse no navegador em [http://localhost:90](http://localhost:90).

---

## 🚀 Implantação no Easypanel

Por se tratar de um projeto composto por dois contêineres independentes (Nginx e Streamlit), você deve configurá-los no Easypanel de uma das seguintes maneiras:

### Método A: Criando Dois Serviços Dedicados (Recomendado)

1. **Crie o Serviço do Simulador (Smartwatch):**
   * Crie um novo **App** no Easypanel (ex: `worldcup2026demo`).
   * Aponte para o seu repositório Git.
   * Nas configurações de domínio, aponte o seu domínio público para a porta **80** (Destino: HTTP / Porta: 80).
   * **Importante:** Não configure nenhuma regra de domínio apontando para a porta 90 neste App para evitar conflito.

2. **Crie o Serviço de Estatísticas (Streamlit):**
   * No mesmo projeto, clique em `+ Serviço` e selecione um novo **App** (ex: `worldcup-stats`).
   * Aponte para o **mesmo** repositório Git.
   * Nas configurações de build do App, mude o **Dockerfile Path** para `Dockerfile.stats`.
   * Você não precisa associar nenhum domínio público a este App, pois ele será acessado apenas internamente.

3. **Como eles se comunicam:**
   * A configuração do Nginx no simulador tentará encontrar o Streamlit pelo hostname padrão do contêiner (`worldcup-stats:90`).
   * Se o seu projeto no Easypanel se chama `ai` e o App do Streamlit se chama `worldcup-stats`, o Nginx tentará se conectar via `http://worldcup-stats:90` e automaticamente usará a regra de fallback para `http://ai_worldcup-stats:90` caso a primeira falhe.

---

### Método B: Utilizando a pilha do Docker Compose do Easypanel

1. No Easypanel, em vez de criar um "App" padrão, adicione um serviço do tipo **Docker Compose**.
2. Aponte para o repositório Git. O Easypanel detectará o arquivo `docker-compose.yml` e subirá os dois serviços (`worldcup-simulator` e `worldcup-stats`) na mesma rede interna.
3. Nas configurações do serviço de compose do Easypanel, aponte o domínio público do projeto para o contêiner `worldcup-simulator` na porta `80`.

---

## 📊 Dashboard de Estatísticas (Streamlit)

O painel calcula e exibe em tempo real o desempenho do torneio para todas as partidas com status `finished` (finalizadas):
* **Métricas Principais:** Contagem de partidas concluídas, total e média de gols por partida, cartões amarelos e vermelhos simulados, e faltas cometidas.
* **Artilharia (Top Scorers):** Ranking gráfico dinâmico dos jogadores que marcaram gols no torneio.
* **Desempenho de Confrontos:** Gráfico comparativo de vitórias de mandantes, empates e vitórias de visitantes.
* **Ataques Eficientes:** Tabela interativa com os times que mais marcaram gols (mapeados e traduzidos).
* **Últimas Partidas:** Relatório com os placares das últimas partidas finalizadas.

---

## 🌐 Internacionalização e Suporte Multilíngue

Todo o ecossistema (relógio inteligente, painel de controle e dashboard Streamlit) compartilha as traduções mapeadas no dicionário XML centralizado em `public/translate.xml`.

O idioma ativo é determinado via parâmetro de busca na URL (`?language=` ou `?lang=`).

### Idiomas Suportados:
- **Português:** `pt`
- **Inglês (padrão):** `en`
- **Italiano:** `it`
- **Espanhol:** `es`
- **Francês:** `fr`

---

## 📦 Como Incorporar via Iframe Externo

O painel de estatísticas foi configurado no arquivo `.streamlit/config.toml` desativando as proteções de CORS e XSRF para que possa ser incorporado livremente em sites e portais esportivos parceiros.

### Exemplo de Código HTML:

```html
<!-- Incorpora o painel de estatísticas com idioma em português -->
<iframe 
  src="https://ai-worldcup2026demo.jd0rwz.easypanel.host/stats/?language=pt" 
  width="100%" 
  height="750px" 
  style="border: none; border-radius: 16px; background: #09090b; box-shadow: 0 10px 30px rgba(0,0,0,0.5);"
  allow="fullscreen">
</iframe>
```

---

## 🛠️ Arquitetura e Estrutura de Arquivos

```text
├── index.html              # Estrutura principal (Relógio, Painel e Modal do Iframe)
├── docker-compose.yml      # Configuração de containers multi-serviços (Vite e Streamlit)
├── Dockerfile              # Definição do container para o Simulador Smartwatch (Vite + Nginx)
├── Dockerfile.stats        # Definição do container para o Dashboard de Estatísticas (Streamlit)
├── vite.config.js          # Configuração do proxy local (CORS Bypass)
├── package.json            # Scripts e dependências de desenvolvimento (Vite)
├── stats_app.py            # Dashboard de estatísticas em Python Streamlit
├── .streamlit
│   └── config.toml         # Configuração de portas, subpath (/stats/), tema escuro e bypass de CORS no Streamlit
├── public
│   └── translate.xml       # Dicionário XML central de traduções (PT, EN, IT, ES, FR)
└── src
    ├── styles.css          # Estilos premium, glassmorphism, frame do smartwatch e painel
    ├── app.js              # Controlador principal (eventos, iframe relativo e reatividade)
    ├── api.js              # Cliente da API com estratégias híbridas de caching e fallback
    ├── simulator.js        # Motor de simulação de jogo ao vivo e gerador de eventos retroativos
    ├── utils.js            # Utilitários (traduções de times, emojis de bandeira e standings)
    └── fallback-matches.js # Base estática local com os 104 jogos para modo offline
```
