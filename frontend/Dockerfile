FROM node:22-alpine

WORKDIR /app

COPY package*.json ./

RUN if [ -f package.json ]; then npm install; else echo "No package.json found, skipping install"; fi

COPY . .

CMD ["npm", "run", "dev", "--", "--host"]
