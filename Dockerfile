FROM python:3.7
EXPOSE 8000
RUN pip install pipenv && mkdir /app
WORKDIR /app/
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN pip install  --no-cache-dir -r /tmp/requirements.txt
COPY . /app/
