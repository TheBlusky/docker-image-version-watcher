FROM python:3
RUN useradd python_user
RUN mkdir /app
WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD docker-image-version-watcher.py .
USER python_user
CMD ["python", "docker-image-version-watcher.py"]