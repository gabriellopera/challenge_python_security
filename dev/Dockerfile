FROM python:3.10-slim-buster
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y python3 python3-dev libmariadbclient-dev pkg-config gcc default-libmysqlclient-dev && pip3 install mysqlclient
#RUN apt-get update && apt-get install -y python3 python3-dev gcc default-libmysqlclient-dev && pip3 install mysqlclient coreapi
RUN pip install --upgrade pip

WORKDIR /api/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8025
CMD ["gunicorn", "--bind", ":8025", "--workers", "4", "--timeout", "120", "reto_seguridad.wsgi"]
