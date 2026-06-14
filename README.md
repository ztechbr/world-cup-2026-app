# Smartwatch Copa do Mundo 2026 - Simulador & Estatísticas

Esta é uma aplicação web de alta fidelidade que simula um aplicativo de relógio inteligente circular para consulta e simulação de partidas da Copa do Mundo de 2026, integrada a um **Dashboard de Estatísticas** dinâmico desenvolvido em Python Streamlit.

A interface exibe um relógio interativo (com suporte a swipe lateral para navegação e botão coroa funcional), um painel de controle lateral translúcido (glassmorphism) para simulação de jogos ao vivo, e um botão **Statistics** para abrir o dashboard analítico em um iframe/modal responsivo.

---

## 🚀 Como Executar o Projeto

Você pode rodar o ecossistema completo do projeto localmente de duas maneiras: utilizando Docker Compose (Recomendado) ou executando os serviços manualmente.

### Opção 1: Via Docker Compose (Rápido & Isolado)

Certifique-se de ter o Docker e o Docker Compose instalados em sua máquina.

1. **Inicie o ambiente:**
   No diretório raiz do projeto, execute o comando:
   ```bash
   docker-compose up --build
   ```
   Isso construirá e iniciará ambos os contêineres:
   * **Simulador Smartwatch (Frontend Vite):** Disponível em [http://localhost:3000](http://localhost:3000).
   * **Dashboard de Estatísticas (Python Streamlit):** Disponível em [http://localhost:90](http://localhost:90).

---

### Opção 2: Execução Manual

#### Serviço 1: Simulador Smartwatch (Vite + Javascript)
1. Certifique-se de ter o **Node.js** instalado.
2. Navegue até a pasta do projeto e instale as dependências:
   ```bash
   npm install
   ```
3. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```
4. Acesse no navegador em [http://localhost:3000](http://localhost:3000).

#### Serviço 2: Dashboard de Estatísticas (Python Streamlit)
1. Certifique-se de ter o **Python 3.9+** instalado.
2. Instale as dependências necessárias listadas em `Dockerfile.stats`:
   ```bash
   pip install streamlit pandas requests
   ```
3. Inicie o servidor Streamlit:
   ```bash
   streamlit run stats_app.py
   ```
4. Acesse no navegador em [http://localhost:90](http://localhost:90).

---

## 📊 Dashboard de Estatísticas (Streamlit)

O painel secundário calcula e exibe em tempo real o desempenho do torneio para todas as partidas com status `finished` (finalizadas):
* **Métricas Principais:** Contagem de partidas concluídas, total e média de gols por partida, cartões amarelos e vermelhos simulados, e faltas cometidas.
* **Artilharia (Top Scorers):** Ranking gráfico dinâmico dos jogadores que marcaram gols no torneio.
* **Desempenho de Confrontos:** Gráfico comparativo de vitórias de mandantes, empates e vitórias de visitantes.
* **Ataques Eficientes:** Tabela interativa com os times que mais marcaram gols.
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
  src="http://localhost:90/?language=pt" 
  width="100%" 
  height="750px" 
  style="border: none; border-radius: 16px; background: #09090b; box-shadow: 0 10px 30px rgba(0,0,0,0.5);"
  allow="fullscreen">
</iframe>
```

> 💡 **Dica de Produção:** Em ambientes de produção hospedados em HTTPS (como o Easypanel), configure um subdomínio seguro (ex: `https://stats.seudominio.com`) para apontar para o contêiner Streamlit na porta `90`. Isso evita problemas de bloqueio de **Mixed Content** (conteúdo misto HTTP dentro de HTTPS) nos navegadores dos usuários.

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
│   └── config.toml         # Configuração de portas, tema escuro e bypass de CORS/XSRF no Streamlit
├── public
│   └── translate.xml       # Dicionário XML central de traduções (PT, EN, IT, ES, FR)
└── src
    ├── styles.css          # Estilos premium, glassmorphism, frame do smartwatch e animações
    ├── app.js              # Controlador principal (eventos, carregamento dinâmico de iframe e reatividade)
    ├── api.js              # Cliente da API com estratégias híbridas de caching e fallback
    ├── simulator.js        # Motor de simulação de jogo ao vivo e gerador de eventos retroativos
    ├── utils.js            # Utilitários (traduções de times, emojis de bandeira e standings)
    └── fallback-matches.js # Base estática local com os 104 jogos para modo offline
```
