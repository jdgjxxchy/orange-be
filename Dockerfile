FROM python:3.8-alpine3.15
COPY . .
RUN apk add -U g++ gcc
RUN pip3 install --upgrade pip3
RUN pip3 install -r requirements.txt
EXPOSE 9999
CMD ["python", "./main.py"]