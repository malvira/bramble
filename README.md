Installation
============

Stuff...

Install libcoap and coap-client
-------------------------------

Get the latest version of libcoap that works with erbium:

```
git clone git://libcoap.git.sourceforge.net/gitroot/libcoap/libcoap
cd libcoap
git checkout a662f73
autoconf
./configure
make
cp examples/coap-client /usr/local/bin
```

compatibility after this version is broken

Running on BR12
===============

- how does hostname work? Currently they come up as alarm

- root password is root (how is this going to work?)

- serial console is disabled by default. TODO: make the prog12 set
  that mux 

Everthing under this is old
===========================

code to run on border-routers

How to use:
-----------

Use new-device to get a new eui for a BR12. 

In the web.git, run python passwords to generate a device password.

 python passwords.py 
{"password": "IP7w6o5CfU7qGIf6NAKKmbli", "bcrypt": "$2a$12$NzXEXmiHgvfI1Xy0bpXdSu9q0dt/WL8PLiEJsANTMzhj8O/qFO/GW"}

Put the bcrypt into the database and put the password into lowpan.json

$2a$12$NzXEXmiHgvfI1Xy0bpXdSu9q0dt/WL8PLiEJsANTMzhj8O/qFO/GW

database:
 "passwords": {"login": "$2a$12$NzXEXmiHgvfI1Xy0bpXdSu9q0dt/WL8PLiEJsANTMzhj8O/qFO/GW"}

lowpan.json:
{
    "url" : "http://couch-0-ord.devl.org:5000", 
    "eui" : "ec473cbb12000003",
    "password" : "IP7w6o5CfU7qGIf6NAKKmbli",
    "realm" : "lowpan",
    "gogo-conf": "/etc/gogoc"
}

run lowpan-tunnel, this will get a tsps password and allocate a
tunnel. It will write a /etc/gogoc.conf with this info.

Getting a tunnel:
-----------------

NOTE securing the passwords/credentials: not sure how to do
this. Can I store the private key on the server and then issue
certificates or something? Short answer is no, a determined person
will get the keys/passwords. But I think that's ok. If you own the
password you own the license. That's my policy. I just have to make it
hard for people to steal passwords from other people.

eui and password are used to get the tunnel endpoint from the web api
gogoc is configured to use that tunnel endpoint (using mac and tunnel password)
tsp send pass with digst-md5. This will be sent a lot so we'll use a
different password.

tsps looks up the allocated subnet for the border-router and passes it along.

lowpan-tunnel needs to generate a password and the passhash and send
the passhash to the server.

Directory Structure:
--------------------

web/
   flask border-router webpage
files/
   files for various systems, mirrors their directory structure
   arch/
      files for arch/arm
   debian/
      files for debian/ubuntu desktops acting as border-routers
      (useful for development)
