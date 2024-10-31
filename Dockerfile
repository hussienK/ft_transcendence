#using python
FROM python:3.9-slim

#set the working directory in the container
WORKDIR /app

#copy the requirements file into the container
COPY requirements.txt ./

#install all the needed packages
RUN pip install --no-cache-dir -r requirements.txt

#copy the rest of the app code
COPY . .

#expose the used port
EXPOSE 8000

#set the env vars
ENV PYTHONNUNBUFFERED=1

#Run the application
CMD ['python', 'manage.py', 'runserver', '0.0.0.0:8000']