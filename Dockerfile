FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    apertium \
    apertium-en-es \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY process_pdfs.py .

CMD ["python", "process_pdfs.py"]
