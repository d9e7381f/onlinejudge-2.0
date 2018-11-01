FROM python:3.6-alpine3.6

ENV OJ_ENV production

COPY deploy/pip.conf /etc/

RUN apk add --update build-base nginx openssl curl unzip supervisor jpeg-dev zlib-dev postgresql-dev freetype-dev python-dev git

ADD . /app
WORKDIR /app

RUN git clean -fdx && \
    git reset --hard @

HEALTHCHECK --interval=5s --retries=3 CMD python2 /app/deploy/health_check.py

RUN git clone --depth 1 -b dgut-login https://github.com/d9e7381f/OnlineJudgeFE.git frontend_tmp && \
    mv frontend_tmp/dist . && \
    rm -rf frontend_tmp

RUN pip install -U pip && \
    pip install --no-cache-dir pipenv

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN pipenv --bare install --dev

ENTRYPOINT /app/deploy/entrypoint.sh
