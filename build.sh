# install docker
sudo yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2
sudo yum-config-manager \
  --add-repo \
  https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce

# install docker-compose
sudo pip3 install docker-compose

# get mosquitto-auth-plug
git clone https://github.com/ZevveZ/mosquitto-auth-plug.git

# build containers
docker-compose build
