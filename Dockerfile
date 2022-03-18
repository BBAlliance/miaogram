FROM python:alpine
LABEL maintainer=BBAliance

WORKDIR /miaogram
COPY . /miaogram

# disabling cgo when built, so no need to install libc6-compat
RUN apk add --no-cache bash libjpeg libwebp libpng \
    && apk add --no-cache --virtual build-deps gcc g++ zlib-dev jpeg-dev libxslt-dev libxml2-dev libwebp-dev libpng-dev \
    && pip install -r requirements.txt \
    && apk del build-deps \
    && mkdir -p /miaogram/data

VOLUME /miaogram/data

ENTRYPOINT ["/usr/local/bin/python3", "-u", "main.py"]
