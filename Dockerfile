FROM python:3-onbuild
ENTRYPOINT ["uwsgi", "--ini", "uwsgi.ini"]
