# ==========================================
# Etapa 1: Build da Aplicação Vite
# ==========================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copia arquivos de dependência e instala
COPY package*.json ./
RUN npm ci

# Copia os fontes e executa o build de produção
COPY . .
RUN npm run build

# ==========================================
# Etapa 2: Servidor Web de Produção (Nginx)
# ==========================================
FROM nginx:stable-alpine

# Copia os arquivos de build gerados pelo Vite
COPY --from=builder /app/dist /usr/share/nginx/html

# Copia a configuração customizada do Nginx com Proxy Reverso
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
