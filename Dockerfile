FROM python:3.8
COPY ./ /usr/questions_bank
WORKDIR /usr/questions_bank
RUN apt-get update && apt-get install -y wkhtmltopdf
RUN apt-get install -y pandoc
RUN pip install -r requirements.txt