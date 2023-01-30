FROM culturecloud/mltb:anasty17

ENV TZ Asia/Dhaka
ENV DEPLOY_REPO culturecloud/mltb
ENV DEPLOY_BRANCH freepaas
ENV REQ_FILE_NAME libraries.txt
ENV REQ_FILE_URL https://github.com/${DEPLOY_REPO}/raw/${DEPLOY_BRANCH}/${REQ_FILE_NAME}

WORKDIR /culturecloud/mltb/

RUN apt-get update \
    && apt-get -y --no-install-recommends upgrade \
    && apt-get clean \
    && apt-get -y autoremove \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv --upgrade-deps $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV PYTHONWARNINGS ignore
RUN curl -sOL $REQ_FILE_URL \
    && pip3 install --no-cache-dir -U wheel \
    && pip3 install --no-cache-dir -Ur $REQ_FILE_NAME \
    && cd /culturecloud/megasdk/bindings/python/ \
    && python3 setup.py bdist_wheel \
    && cd dist \
    && pip3 install --no-cache-dir megasdk-*.whl

RUN rm -rf /culturecloud/mltb/* \
    && git clone -b $DEPLOY_BRANCH \
    https://github.com/$DEPLOY_REPO /culturecloud/mltb/
    
COPY . .

ENTRYPOINT ["/tini", "--"]
CMD ["bash", "start.sh"]
