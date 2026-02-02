FROM oven/bun:latest

# Create app directory
WORKDIR /app

# Copy only lockfile & package.json first for caching
COPY bun.lock package.json ./

# Install deps
RUN bun install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Run dev server
CMD ["bun", "run", "dev", "--port", "3000", "--host", "0.0.0.0"]
