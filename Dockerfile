FROM python:alpine
COPY src/. /app
WORKDIR /app
#Psutil
RUN apk add --update gcc libc-dev linux-headers && rm -rf /var/cache/apk/*
RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["python", "app.py"]
