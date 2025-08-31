FROM node:18-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

# Exponer el puerto que usa el servidor de desarrollo de React
EXPOSE 3000

# Comando para iniciar el servidor de desarrollo
CMD ["npm", "start"]