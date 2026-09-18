FROM node:20-alpine
WORKDIR /app

RUN npm install -g pnpm
COPY app/package.json app/pnpm-lock.yaml* ./
RUN pnpm install --ignore-scripts
COPY . .

EXPOSE 3000
CMD ["sleep", "infinity"]

# -- production 
# CMD ["pnpm", "dev"]
