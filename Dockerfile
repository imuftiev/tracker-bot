FROM python:
LABEL authors="iwast"

ENTRYPOINT ["top", "-b"]