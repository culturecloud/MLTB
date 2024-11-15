FROM anasty17/mltb:latest

WORKDIR /usr/src/app
SHELL ["/bin/bash", "-c"]

COPY requirements.txt .

RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && source $HOME/.local/bin/env \
    && uv venv --seed --no-cache --link-mode=copy mltbenv \
    && source mltbenv/bin/activate \
    && uv pip install --no-cache --link-mode=copy -Ur requirements.txt \
    && rm -rf /root/.cache/* \
    && rm -rf /var/cache/*

COPY . .

RUN chmod -R 755 /usr/src/app

CMD ["start.sh"]
