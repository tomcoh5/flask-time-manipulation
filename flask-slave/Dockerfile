FROM python:3
VOLUME /mydata
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY web.py .
EXPOSE 5001
CMD [ "python" , "web.py" ]
