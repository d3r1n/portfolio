FROM oven/bun:latest AS builder

WORKDIR /app

COPY package.json ./
COPY bun.lock ./

RUN bun install

COPY . ./

CMD ["bun", "run", "build"]