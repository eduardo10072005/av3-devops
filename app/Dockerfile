FROM python:3.10-slim

WORKDIR /app

# Copia os requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copia o resto dos arquivos da aplicação
COPY . .

# O Render exige que escutemos na porta 10000 por padrão
EXPOSE 10000

# Inicia o app usando o Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "2", "app:app"]
