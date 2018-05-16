FROM node:8.11.1
RUN apt-get update && apt-get install -y nginx
WORKDIR /app
ADD . /app/
RUN npm install && npm run build &&cp -r dist/* /var/www/html/
CMD ["nginx","-g","daemon off;"]
