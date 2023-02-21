FROM culturecloud/mltb:alpine

ARG DEPLOY_BRANCH="freepaas"

RUN git clone -b \
    $DEPLOY_BRANCH \
    https://github.com/culturecloud/mltb-rclone \
    /culturecloud/mltb
    
WORKDIR /culturecloud/mltb

COPY . .

CMD ["bash", "start.sh"]