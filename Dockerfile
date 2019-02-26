# Install pytest python library as well as add all files in current directory
FROM python:3.7 AS base
WORKDIR /usr/src/app
RUN apt-get update \
    && apt-get install -y enchant \
    && rm -rf /var/lib/apt/lists/*

RUN pip install coveralls
ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e .

RUN python ./setup.py test
CMD ["python", "./setup.py", "test"]
