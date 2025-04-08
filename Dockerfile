FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y \
	make postgresql-client

ADD src/ .

EXPOSE 8000

CMD ["make", "up"]