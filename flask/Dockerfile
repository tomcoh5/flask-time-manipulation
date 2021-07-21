FROM python:3
VOLUME /mydata
WORKDIR /usr/src/appi
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "./web.py" ]
