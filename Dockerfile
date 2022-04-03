FROM python:3.8
COPY ./ /usr/questions_bank
WORKDIR /usr/questions_bank
RUN pip install -r requirements.txt