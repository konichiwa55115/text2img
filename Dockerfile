FROM alpine:3.16.2

RUN apk add git=2.36.3-r0 --no-cache

RUN apk add bash=5.1.16-r2 --no-cache

RUN apk add python3=3.10.5-r0 --no-cache

RUN apk add py3-pip=22.1.1-r0 --no-cache

RUN apk add py3-virtualenv=20.14.1-r0 --no-cache

RUN apk add gcompat=1.0.0-r4 --no-cache

RUN mkdir /storage

RUN mkdir /storage/text2img

COPY . /storage/text2img

RUN /bin/bash /storage/text2img/scripts/install.sh

EXPOSE 80

CMD ["./storage/text2img/scripts/run.sh"]
