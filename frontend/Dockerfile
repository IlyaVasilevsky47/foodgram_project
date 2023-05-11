# build env 
FROM node:13.12.0-alpine as build 
WORKDIR /app 
EXPOSE 3000
COPY package*.json ./ 
RUN npm install 
COPY . ./ 
RUN npm run build 
CMD ["npm", "start"]