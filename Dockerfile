FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y \
	make sqlite3 libsqlite3-dev postgresql-client

ADD src/ .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["make", "re"]