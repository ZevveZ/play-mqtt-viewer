#! /bin/bash
docker-compose up -d mysql
docker-compose up -d mosquitto
docker-compose up -d django
