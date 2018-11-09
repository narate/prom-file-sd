FROM python:alpine
LABEL maintainer="Narate Ketram <rate@dome.cloud>"
WORKDIR /app
ADD ./requirements.txt .
RUN pip install -r requirements.txt
ADD ./app.py .
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
