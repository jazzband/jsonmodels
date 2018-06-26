# Install pytest python library as well as add all files in current directory
FROM python:3 AS base
WORKDIR /usr/src/app
RUN apt-get update \
    && apt-get install -y enchant \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install coveralls
ADD . .
RUN pip install --no-cache-dir -r requirements.txt
RUN python ./setup.py test
CMD ["python", "./setup.py", "test"]
