BRamble
=======

BRamble is a web-based administration system for 6LoWPAN
border-routers. It provides setup and diagnostic tools to easily
deploy 6LoWPAN networks.

Features
========

* RPL network visualization
  * queries routing information from nodes implmenting [rplinfo](https://github.com/malvira/rplinfo) CoAP resources

* Automatic IPv6 network configuration
  * bridge configuration via tunslip6 and [erbr](https://github.com/malvira/erbr)
  * global tunnel configuration via [TSP](http://tools.ietf.org/html/rfc5572)
    * [Lowpan.com](https://www.lowpan.com/)
    * [Freenet6 (Gogo6)](http://www.gogo6.com/freenet6)

* Radio managment
  * automatic firmware loading

Screenshots
------------

* [Settings](https://raw.github.com/wiki/malvira/bramble/images/settings.png)
* [Radio](https://raw.github.com/wiki/malvira/bramble/images/radio.png)
* [Mesh 1](https://raw.github.com/wiki/malvira/bramble/images/mesh1.png)
* [Mesh 2](https://raw.github.com/wiki/malvira/bramble/images/mesh2.png)
* [Mesh 3](https://raw.github.com/wiki/malvira/bramble/images/mesh3.png)
* [Mesh 4](https://raw.github.com/wiki/malvira/bramble/images/mesh4.png)


Getting Help and Contibuting
============================

Please see the [wiki](https://github.com/malvira/bramble/wiki) for
detailed development details. If you need help, please ask questions
in the [issue tracker](https://github.com/malvira/bramble/issues). 

Installation
============

Get BRamble
-----------

```
git clone https://github.com/malvira/bramble.git
```

### Install dependencies

On a debian/ubuntu machine, the following should get you pretty close:

```
apt-get update 
apt-get install cython libjs-jquery python-flask python-pip python-dev ipv6calc
pip install Flask-OpenID Flask-Login Flask-Principal Flask-Bcrypt Flask-Mako IPy
```

See also the advanced scripts in:

  [bramble/files/debian/install-debian.sh](https://github.com/malvira/bramble/blob/master/files/arch/install-arch.sh)
  [bramble/files/arch/install-arch.sh](https://github.com/malvira/bramble/blob/master/files/debian/install-debian.sh)

These scripts will setup nginx and automatically start BRamble
etc... **READ THROUGH THEM BEFORE RUNNING ON YOUR SYSTEM** 

#### Install gevent from source

```
git clone https://github.com/SiteSupport/gevent.git
cd gevent
python setup.py build
python setup.py install
```

#### Install libcoap and coap-client

BRabmle currently uses coap-client from [libcoap](http://libcoap.sourceforge.net/).

Currently mainline contiki implements coap-08 in erbium (used by
`erbr` and `rplinfo`). To get the latest version of libcoap that works
with with this version of erbium:

```
git clone git://libcoap.git.sourceforge.net/gitroot/libcoap/libcoap
cd libcoap
git checkout a662f73
autoconf
./configure
make
cp examples/coap-client /usr/local/bin
```

#### Econotag tools

If you are using econotags or mc13224vs with bramble you will need
mc1322x-load (the C version and not the perl script):

```
/contiki/cpu/mc1322x/tools$ gcc mc1322x-load.c -o mc1322x-load
sudo cp mc1322x-load /usr/local/bin
```

and probably `bbmc` (esp. if you are using PC w/econotag):

```
sudo apt-get install libftdi-dev
/contiki/cpu/mc1322x/tools/ftditools$ make
sudo cp bbmc /usr/local/bin
```

#### Contiki stuff

You should just need tunslip6 in a executable place. 

#### Distribution files

See the files directory for details on how to configure your
particular distribution.

In particular,

##### Gogoc template

_only necessary if you are using a TSP tunnel_

A suitable gogoc template must be present in the BRamble search path
(default: `['/etc/gogoc', '/var/cache/bradmin',
'/etc/lowpan', '/usr/local/etc/lowpan', '.']`

##### getbripv6.sh

This script needs to be in your path somewhere. E.g.:

```
cp ./files/debian/bin/getbripv6.sh /usr/local/bin
```

Running Bramble
===============

```
cd bramble/web
python runserver.py
```

This will print initalization information to the screen while the
border-router is loaded with firmware, tunslip is connected, and
`gogoc` aquires a tunnel. It will also start the BRamble webserver.

If all goes well, point your browser to localhost the default password
is default.

License
=======

BRamble is released under [GPLv3](http://www.gnu.org/licenses/gpl-3.0.txt).
