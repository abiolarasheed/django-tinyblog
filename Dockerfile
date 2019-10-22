FROM python:3.7
EXPOSE 8000

ARG PROJECT_USER=blogger
ARG PROJECT_DIR=/home/blogger/django-tinyblog

# Update to latest pip, create app user and install pipenv
RUN pip install --no-cache-dir --upgrade pip \
    && adduser --disabled-password --gecos "" $PROJECT_USER \
    && mkdir $PROJECT_DIR && chown -R $PROJECT_USER:$PROJECT_USER $PROJECT_DIR \
    && pip install pipenv

USER $PROJECT_USER
WORKDIR $PROJECT_DIR

RUN pip install --user pipenv
ENV PATH="/home/$PROJECT_USER/.local/bin:${PATH}"

# Copy our pipfile into the temp dir and convert to requirements.txt then install with pip
# Then cleanup after our self
COPY --chown=$PROJECT_USER:$PROJECT_USER Pipfile* /tmp/
RUN cd /tmp && pipenv lock --clear --requirements > requirements.txt \
    && pip install --user --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /tmp/requirements.txt && rm -rf /tmp/Pipfile*

# Copy code over to user home directory
COPY --chown=$PROJECT_USER:$PROJECT_USER . .
