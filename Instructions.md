# To Run The app follow the steps

- Make sure docker is installed and running
- remove any previously active prosses `docker rm -f $(docker ps -a -q)`
- shut down all previous containers `docker-compose down -v`
- to build on production (no live updates) `docker-compose --profile production up --build`
- to build on development (enable live udpates) `docker-compose --profile development up --build`