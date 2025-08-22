FROM oven/bun:latest

WORKDIR /app

COPY bun.lock package.json ./
RUN bun install --no-cache --frozen-lockfile

COPY . .

EXPOSE 3000
CMD ["bun", "run", "--bun", "dev", "--port", "3000", "--host", "0.0.0.0"]
