FROM python:3-onbuild
EXPOSE 5000
ENTRYPOINT ["uwsgi", "--ini", "uwsgi.ini"]
