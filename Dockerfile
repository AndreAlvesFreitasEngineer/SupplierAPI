FROM python:3.10-slim

WORKDIR /app

# 1. Instala dependências do sistema e limpa cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 2. Garante que o pip está atualizado
RUN pip install --no-cache-dir --upgrade pip

# 3. Copia requirements primeiro (para cache eficiente)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Instala o Uvicorn explicitamente como pacote global
RUN pip install --no-cache-dir uvicorn

# 5. Copia o restante da aplicação
COPY . .

# 6. Define o comando usando o caminho absoluto
CMD ["/usr/local/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]