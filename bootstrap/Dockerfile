FROM node:lts-slim

WORKDIR /bootstrap

COPY bootstrap/src ./
COPY bootstrap/package.json ./
COPY bootstrap/package-lock.json ./
COPY bootstrap/webpack.config.js ./

RUN /usr/local/bin/npm install

ENTRYPOINT ["/usr/local/bin/npm", "run", "start"]
#ENTRYPOINT ["/bin/sleep", "100"]