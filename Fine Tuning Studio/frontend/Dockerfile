FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine
RUN npm install -g serve

WORKDIR /app

COPY --from=0 /app/build ./build
COPY package*.json ./

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
