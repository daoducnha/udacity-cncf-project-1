FROM python:3.8

COPY . /app

WORKDIR /app

# Install dependencies
RUN pip install -r requirements.txt

# Initialize the database 
RUN python init_db.py

CMD [ "python", "app.py" ]