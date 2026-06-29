version: "3.9"

services:
  ws-server:
    build: ./ws-server
    container_name: {{PROJECT_SLUG}}_ws
    env_file: ./ws-server/.env
    ports:
      - "{{WS_PORT}}:{{WS_PORT}}"
    restart: unless-stopped

  backend:
    build: ./backend
    container_name: {{PROJECT_SLUG}}_backend
    environment:
      - PORT={{BACKEND_PORT}}
    ports:
      - "{{BACKEND_PORT}}:{{BACKEND_PORT}}"
    depends_on:
      - ws-server
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: {{PROJECT_SLUG}}_frontend
    environment:
      - PORT={{FRONTEND_PORT}}
      - REACT_APP_BACKEND_URL=http://localhost:{{BACKEND_PORT}}
      - REACT_APP_WS_URL=ws://localhost:{{WS_PORT}}
    ports:
      - "{{FRONTEND_PORT}}:{{FRONTEND_PORT}}"
    depends_on:
      - backend
    restart: unless-stopped
