sudo chown www-data.adm /home/pi/repos/home_hub/flask_app
sudo chown www-data.adm /home/pi/repos/home_hub/flask_app/app_contents
uwsgi --ini /home/pi/repos/home_hub/flask_app/nginx_config/uwsgi.ini
sudo rm /etc/nginx/sites-enabled/default
sudo cp /home/pi/repos/home_hub/flask_app/nginx_config/brandonruggles_proxy /etc/nginx/sites-available/brandonruggles_proxy
sudo ln -s /etc/nginx/sites-available/brandonruggles_proxy /etc/nginx/sites-enabled
sudo systemctl restart nginx
sudo cp /home/pi/repos/home_hub/flask_app/nginx_config/uwsgi.service /etc/systemd/system/uwsgi.service
cd /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start uwsgi.service

