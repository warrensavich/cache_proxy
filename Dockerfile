FROM python:3.7-alpine
RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev
ADD ./requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip install -r requirements.txt
ADD . /code
CMD ["python", "run.py"]