FROM python:alpine
LABEL maintainer="Narate Ketram <rate@dome.cloud>"
WORKDIR /app
ADD ./requirements.txt .
RUN pip install -r requirements.txt
ADD ./app.py .
EXPOSE 5000
CMD ["python", "-u", "app.py"]
