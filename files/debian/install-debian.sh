#!/bin/sh

DIR=`pwd`
BASE=$DIR/../..

apt-get update 
apt-get install -y git libssl0.9.8 nginx uwsgi uwsgi-plugins-all cython libjs-jquery python-flask python-pip python-dev ipv6calc apt-src
pip install Flask-OpenID Flask-Login Flask-Principal Flask-Bcrypt nameparser Flask-Mako uwsgitop

# get the uwsgi source, build the gevent plugin and install
cd /tmp
apt-src install uwsgi
cd uwsgi-1.2.5+dfsg
python uwsgiconfig.py --plugin plugins/gevent
cp gevent_plugin.so /usr/lib/uwsgi/plugins

# get gevent from source, build and install it
cd /tmp
git clone https://github.com/SiteSupport/gevent.git
cd gevent
python setup.py build
python setup.py install

cd $DIR
# setup nginx
STATIC=$BASE/web/bradmin
cp etc/nginx/bradmin /etc/nginx/sites-available
ln -sf /etc/nginx/sites-available/bradmin /etc/nginx/sites-enabled/bradmin
sudo sed -i "s,root PATH-TO-BRADMIN-STATIC,root $STATIC,g" /etc/nginx/sites-available/bradmin
service nginx restart

#setup uwsgi app
cp ../arch/etc/uwsgi/apps/bradmin.ini /etc/uwsgi/apps-available
ln -sf /etc/uwsgi/apps-available/bradmin.ini /etc/uwsgi/apps-enabled/bradmin.ini
service uwsgi restart