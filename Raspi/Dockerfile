FROM node:13

RUN apt-get update \
    && apt-get install -y build-essential libudev-dev

WORKDIR /das
COPY package.json /das/package.json
RUN npm install
COPY . /das

ENTRYPOINT [ "/usr/local/bin/node", "." ]
