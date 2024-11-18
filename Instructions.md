# To Run The app follow the steps

- Make sure docker is installed and running
- remove any previously active prosses `docker rm -f $(docker ps -a -q)`
- shut down all previous containers `docker-compose down -v`
- to build on production (no live updates) `docker-compose --profile production up --build`
- to build on development (enable live udpates) `docker-compose --profile development up --build`


## Testing and debugging tips:

- for sending an email to test, after running container in a seperate terminal, `docker exec -it ft_transcendance_app_dev bash`, `from django.core.mail import send_mail`, `send_mail ('test mail', 'helloooooo', 'transcendence.42beirut@gmail.com', ['hussienkenaan93@gmail.com'])`

