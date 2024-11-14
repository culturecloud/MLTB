FROM anasty17/mltb:latest

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir uv --break-system-packages \
    && uv pip install --no-cache --system -Ur requirements.txt --break-system-packages

COPY . .

RUN chmod -R 777 /usr/src/app

CMD ["bash", "start.sh"]
