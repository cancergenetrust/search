FROM alpine:latest

RUN apk add --update python py-pip
RUN pip install --upgrade pip

WORKDIR /app
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD . /app

# ENTRYPOINT ["python", "crawl.py"]
# ENTRYPOINT ["cron", "-f"]
CMD crond -l 2 -f

