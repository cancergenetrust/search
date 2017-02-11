FROM python:2-onbuild
ENTRYPOINT ["uwsgi", "--ini uwsgi.ini"]
