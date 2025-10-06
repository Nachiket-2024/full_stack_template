# ---------------------------- External Imports ----------------------------
# Use official Node.js 20 image with build tools for optional dependencies
FROM node:20-bullseye

# ---------------------------- Setup ----------------------------
WORKDIR /app

# ---------------------------- Install Build Tools ----------------------------
# Required to compile native optional dependencies for Rollup / esbuild
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------- Copy Dependencies ----------------------------
# Copy only dependency manifests to leverage Docker cache
COPY frontend/package*.json ./

# ---------------------------- Install Node.js Dependencies ----------------------------
# Install dependencies inside the container so the correct rollup binary is picked
RUN npm install --legacy-peer-deps

# ---------------------------- Copy App Source ----------------------------
COPY frontend/ .

# ---------------------------- Expose Ports ----------------------------
EXPOSE 5173

# ---------------------------- CMD ----------------------------
CMD ["npm", "run", "dev", "--", "--host"]
