# stage_crypto_bot
# stage_crypto_bot
wget https://dev.mysql.com/get/mysql-apt-config_0.8.33-1_all.deb
sudo dpkg -i mysql-apt-config_0.8.33-1_all.deb
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
mysql -u root -p
CREATE DATABASE karakin_db;
CREATE USER 'karakin'@'localhost' IDENTIFIED BY 'botdatabase991122';
GRANT ALL PRIVILEGES ON karakin_db.* TO 'karakin'@'localhost';
FLUSH PRIVILEGES;
sudo apt update
sudo apt install -y libmysqlclient-dev
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev python3-pip libmysqlclient-dev pkg-config
sudo apt install redis-server
sudo systemctl enable redis
sudo systemctl start redis
g++ -std=c++17 main.cpp -o websocket_client -lboost_system -lpthread
sudo apt update
sudo apt-get install libboost-all-dev

sudo apt-get install libhiredis-dev
git clone https://github.com/redis/hiredis.git

cd hiredis

make

make install


sudo apt install libboost-system-dev libboost-thread-dev libasio-dev nlohmann-json3-dev
cd ~/stage_crypto_bot/cpp/BOTMAIN
git clone https://github.com/zaphoyd/websocketpp.git
cd websocketpp/
sudo apt install cmake
mkdir build
cd build
cmake ..
make
make install
