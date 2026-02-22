FROM python:3.11

WORKDIR /app

# Potrzebne narzędzia do kompilacji niektórych pakietów
RUN apt-get update && apt-get install -y build-essential python3-dev && rm -rf /var/lib/apt/lists/*


RUN python -m pip install --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .


EXPOSE 5000

CMD ["python", "app.py"]
