# Frontend - Build (Vite) + Servir com Nginx
# Estágio 1: build
FROM node:20-alpine AS builder

WORKDIR /app

# Dependências (package.json e lock)
COPY package.json package-lock.json* ./
RUN npm ci

# Variáveis de ambiente em tempo de build (Vite usa VITE_*)
ARG VITE_API_KEY
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ENV VITE_API_KEY=$VITE_API_KEY
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY

COPY . .
RUN npm run build

# Estágio 2: servir com Nginx
FROM nginx:alpine

# Copiar artefatos do build
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuração Nginx (proxy /api para o backend)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
