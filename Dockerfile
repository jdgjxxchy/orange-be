FROM python:3.8-alpine3.15
COPY . .
RUN apk add -U g++ gcc
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 9999
CMD ["python", "./main.py"]