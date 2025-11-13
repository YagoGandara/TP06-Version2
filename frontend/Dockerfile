FROM node:20-alpine
WORKDIR /app
ENV CI=true
RUN npm i -g @angular/cli@18.2.4
COPY package.json package-lock.json* ./
RUN npm ci || npm i
COPY . .
EXPOSE 4200
ENV API_BASE_URL=http://localhost:8080
CMD ["sh", "-c", "ng serve --host 0.0.0.0 --port 4200"]
