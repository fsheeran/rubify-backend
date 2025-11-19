
FROM python:3.13-trixie

RUN apt-get update && apt-get install -y \
    libssl-dev \
    libffi-dev

WORKDIR /app


COPY ./requirements.txt /app/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


COPY ./src /app/src

COPY ./update_dictionaries.py /app/update_dictionaries.py
RUN python /app/update_dictionaries.py

CMD ["fastapi", "run", "/app/src/main.py", "--port", "80"]