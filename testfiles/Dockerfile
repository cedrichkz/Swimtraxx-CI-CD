FROM python:3

#install debug tool
RUN apt-get update 

#copy packages & script
WORKDIR /usr/src/app
COPY testfiles ./

#install packages
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]
