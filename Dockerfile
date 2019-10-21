FROM python:3.7
EXPOSE 8000

# Update to latest pip, create app user and install pipenv
RUN pip install --no-cache-dir --upgrade pip \
    && adduser --disabled-password --gecos "" blogger \
    && pip install pipenv

USER blogger
WORKDIR /home/blogger

RUN pip install --user pipenv
ENV PATH="/home/blogger/.local/bin:${PATH}"

# Copy our pipfile into the temp dir and convert to requirements.txt then install with pip
# Then cleanup after our self
COPY --chown=blogger:blogger Pipfile* /tmp/
RUN cd /tmp && pipenv lock --clear --requirements > requirements.txt \
    && pip install --user --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /tmp/requirements.txt && rm -rf /tmp/Pipfile*


# Copy code over to user home directory
COPY --chown=blogger:blogger . .
