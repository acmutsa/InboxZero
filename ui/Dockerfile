FROM node:20-alpine
WORKDIR /app

RUN npm install -g pnpm
COPY app/package.json app/pnpm-lock.yaml* ./
RUN pnpm install --ignore-scripts
COPY app/ .

RUN pnpm build

EXPOSE 3000
CMD ["sh", "-c", "pnpm next start -p ${PORT:-3000}"]
