# Smartwatch Copa do Mundo 2026 - Simulador de Partidas

Esta é uma aplicação web de alta fidelidade que simula um aplicativo de relógio inteligente circular para consulta e simulação de partidas da Copa do Mundo de 2026, com base no layout fornecido e na API oficial do torneio.

A interface exibe um relógio interativo (com suporte a swipe lateral para navegação e botão coroa funcional) e um painel de controle lateral translúcido (glassmorphism) para controlar a simulação das partidas em tempo real.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Node.js instalado (versão 18 ou superior recomendada).

### Passo a Passo

1. **Defina o Workspace:**
   No seu editor de código, abra a pasta deste projeto:
   `/Users/rodrigozaroni/.gemini/antigravity/scratch/world-cup-2026-app`

2. **Instale as dependências:**
   No terminal, execute:
   ```bash
   npm install
   ```

3. **Inicie o servidor de desenvolvimento:**
   Execute o comando abaixo:
   ```bash
   npm run dev
   ```
   
4. **Acesse no navegador:**
   Abra o endereço exibido no terminal (geralmente [http://localhost:3000](http://localhost:3000)).

---

## 🛠️ Arquitetura e Estrutura de Arquivos

O projeto é estruturado de forma modular utilizando HTML, CSS Vanilla e Javascript nativo estruturado em módulos ES6:

```text
├── index.html              # Estrutura principal (Relógio e Painel de Controle)
├── vite.config.js          # Configuração do proxy local (CORS Bypass)
├── package.json            # Scripts e dependências de desenvolvimento (Vite)
├── README.md               # Este arquivo de instruções
└── src
    ├── styles.css          # Estilos premium, glassmorphism, frame do smartwatch e animações
    ├── app.js              # Controlador principal da aplicação (eventos, navegação e reatividade)
    ├── api.js              # Cliente da API com estratégias híbridas de caching e fallback
    ├── simulator.js        # Motor de simulação de jogo ao vivo e gerador de eventos retroativos
    ├── utils.js            # Utilitários (traduções de times, emojis de bandeira e cálculo de tabelas)
    └── fallback-matches.js # Base estática local com os 104 jogos para modo offline
```

---

## 🌟 Recursos Principais

### 1. Simulador de Smartwatch Físico Interativo
- **Tela Circular Perfeita:** Conteúdo centralizado e dimensionado para evitar cortes nas bordas redondas.
- **Carrossel de Telas (Páginas 1 a 3):**
  - **Tela 1 (Países):** Busca reativa de seleções, filtros por confederação continental (América do Sul, Europa, África, etc.) e marcação de favoritos (estrela).
  - **Tela 2 (Grupos):** Classificação dinâmica recalculada em tempo real para os grupos A até L. Exibe pontos de status verdes na zona de classificação direta (top 2).
  - **Tela 3 (Jogos do Dia):** Lista organizada da rodada contendo seções de jogos "Ao vivo" e "Mais tarde".
- **Gesto de Swipe:** Arraste a tela do relógio para os lados com o mouse ou toque para alternar entre as telas.
- **Botão Físico (Coroa):** Toque na coroa lateral do relógio para retroceder da tela de detalhes ou ciclar entre as abas.
- **Tela 4 (Detalhes do Jogo):** Exibe o placar ampliado, estádio, cidade e uma linha do tempo vertical de eventos do jogo (gols e cartões).

### 2. Motor de Simulação em Tempo Real (Live Matchday)
- A base da API possui 4 jogos agendados para a data de **14 de Junho de 2026** (hoje na linha do tempo simulada):
  1. *Alemanha × Curaçao* (Grupo E)
  2. *Holanda × Japão* (Grupo F)
  3. *Costa do Marfim × Equador* (Grupo E)
  4. *Suécia × Tunísia* (Grupo F)
- Ao clicar em **"Iniciar Simulação"** no painel direito:
  - Os jogos passam de "Agendados" para "Ao vivo" simultaneamente.
  - O minuto do jogo avança de 1' até 90'.
  - Gols e cartões amarelos/vermelhos são disparados aleatoriamente com base em probabilidades realistas.
  - Os nomes dos goleadores são sorteados dinamicamente com base em elencos reais pré-cadastrados para cada país.
  - A tabela de classificação dos grupos e a pontuação dos países na Tela 1 são atualizadas **em tempo real** conforme os gols acontecem!
- **Controle de Velocidade:** Acelere os ticks da partida (100ms por minuto de jogo) para ver a tabela se transformar em segundos ou use velocidades mais calmas.

### 3. Bypass de CORS & Resiliência
- **Proxy Vite:** O arquivo `vite.config.js` está configurado para atuar como proxy, interceptando chamadas para `/api/*` e repassando para a URL da API oficial injetando o cabeçalho `X-Token: COPA26!`. Isso resolve problemas de CORS nos navegadores.
- **Estratégia Híbrida de Fallback:** O cliente `src/api.js` tentará usar o proxy local. Se falhar, tentará a requisição direta. Se ambos falharem (sem internet ou rodando sem servidor de desenvolvimento), ele carregará automaticamente a base offline local de 104 jogos, garantindo que o app funcione em qualquer situação.
- **Persistência Local:** Favoritos e o estado ativo da simulação são guardados no `localStorage`, permitindo que o progresso não seja perdido ao recarregar a página.
