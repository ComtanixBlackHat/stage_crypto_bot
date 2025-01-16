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
