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

#### Flask
Bramble uses the [Flask](http://flask.pocoo.org/) micro-framework for
[Python](http://www.python.org/).

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

#### Contiki stuff

You should just need tunslip6 in a executable place. 

#### Distribution files

See the files directory for details on how to configure your
particular distribution.

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
