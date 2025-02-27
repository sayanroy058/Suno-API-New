# syntax=docker/dockerfile:1 
                                                                                                                                                                                                    
FROM node:lts-bookworm AS builder                                                                                       
WORKDIR /src                                                                                                            
COPY package*.json ./                                                                                                   
RUN npm install                                                                                                         
COPY . .                                                                                                               
RUN npm run build                                                                                                       
                                                                                                                    
FROM node:lts-bookworm                                                                                                  
WORKDIR /app                                                                                                            
COPY package*.json ./                                                                                                   
                                                                                                                    
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y libnss3 \                                       
    libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \                       
    libgbm1 libxkbcommon0 libasound2 libcups2 xvfb                                                                      
                                                                                                                    
ARG SUNO_COOKIE             
RUN if [ -z "$SUNO_COOKIE" ]; then echo "Warning: SUNO_COOKIE is not set. You will have to set the cookies in the Cookie header of your requests."; fi                                           
ENV SUNO_COOKIE=${SUNO_COOKIE}
# Disable GPU acceleration, as with it suno-api won't work in a Docker environment
ENV BROWSER_DISABLE_GPU=true

RUN npm install --only=production                                                                                       
                                                                                                                    
# Install all supported browsers, else switching browsers requires an image rebuild                                     
# Install Playwright browsers with dependencies and set proper permissions
RUN npx playwright install --with-deps chromium && \
    mkdir -p /home/sbx_user1051/.cache && \
    chmod -R 777 /home/sbx_user1051/.cache

# Set environment variables for Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/home/sbx_user1051/.cache/ms-playwright
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

COPY --from=builder /src/.next ./.next
EXPOSE 3000
CMD ["npm", "run", "start"]
