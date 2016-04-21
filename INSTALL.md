Installation
============


Requirements
------------

- Sierra 2.1 or later
- A publicaly accessibly web server, with:
  - Python 3.4 or later
  - PostgreSQL 9.1 or later (but see below)

AutoHolds runs on a server, outside of the Sierra servers. You can choose to install it on the server that runs your
web site, or on a separate server by itself.

AutoHolds doesn't specifically require PostgresSQL. We haven't tested it, but it might also work with other
database systems that Django supports, like MySQL. These instructions will assume you are using PostgreSQL.


Create the autoholds user
-------------------------

1. Create an autoholds user on your server.

This user will run the AutoHolds app. You can use another username, but it must match the name of the PostgreSQL role
you configure AutoHolds to use.


Create the autoholds database
-----------------------------

These instructions assume you have a working PostgreSQL installation and PostgreSQL is running on the same
server as the AutoHolds app.

AutoHolds does not need an IP connection to PostgreSQL. AutoHolds will connect to PostgreSQL using the Unix-domain socket.
This also means the autoholds user can connect to PostgreSQL as the autoholds role without a password.

1. Connect to PostgreSQL as a superuser.
2. Create a role called autoholds.
3. Create a database called autoholds. The database must be owned by the autoholds role and use UTF-8 encoding.
4. Optimise PostgreSQL's configuration as per the [Django documentation](https://docs.djangoproject.com/en/1.9/ref/databases/#postgresql-notes).  

The following script is equivalent to the steps above.
 
```sql
CREATE ROLE autoholds WITH LOGIN;
CREATE DATABASE autoholds WITH OWNER autoholds TEMPLATE template0 ENCODING 'utf8';
ALTER ROLE autoholds IN DATABASE autoholds SET client_encoding = 'utf8';
ALTER ROLE autoholds IN DATABASE autoholds SET default_transaction_isolation = 'read committed';
ALTER ROLE autoholds IN DATABASE autoholds SET timezone = 'UTC';
```


Create a Sierra SQL user
------------------------

1. In the Sierra Admin App, create a user.
2. Enter the name: autoholds.
3. Enter the full name: AutoHolds App.
4. If you see SDA Context Only, ensure it is un-ticked.
5. Enter a dummy password for now. You'll set the proper password in a moment.
6. Set the language to English.
7. Don't worry about anything else. Nothing else is used for SQL users.
8. Save the user.
9. Under applications, assign Sierra SQL Access and accept the access license.
10. Save the user.
11. Change the password to the proper password for this user. You'll need this same password again when you configure the AutoHolds app. 


Create an Sierra API key
------------------------

1. At the top of the Sierra Admin App, go into Sierra API Keys.
2. Create a new API key.
3. Enter the client: autoholds
4. Enter your email address.
5. Under patron permission, tick Global Patron Access.
6. Generate an API key.
7. In the email Sierra sends you, follow the Continue Registration link.
8. Register a client secret (password) for the API key. 
9. Note the API key and the secret. You'll need these when you configure the AutoHolds app.


Install the AutoHolds app
-------------------------

1. Create a directory on your server to hold the AutoHolds app. These instruction will refer to this directory as the install directory.
2. Make the install directory owned by the autoholds user. Any directories leading up to the install directory must also be accessible by the autoholds user, but not necessarily writable.
3. Become the autoholds user and change into the install directory.
4. Clone the release branch of the AutoHolds app from GitHub into the install directory.

Instead of cloning from GitHub, you can download a ZIP file from GitHub and extract the ZIP file into the install directory.

The advantage of cloning is that when you want to upgrade to the latest release, you just need `git pull` and you'll have the
latest released code merged into any local modifications you've made.

If you're not familiar with GitHub or Git see <https://help.github.com/> and <https://git-scm.com/>.


Install the necessary Python packages
-------------------------------------

AutoHolds requires the following additional Python packages.

- django 1.9.x
- requests 2.9 or later
- psycopg2 2.5 or later

The requirements.txt file in the install directory can be used together with the pip tool to install these.

`pip install --requirement requirements.txt`


Configure the AutoHolds app
---------------------------

1. In the install directory copy the file `autoholds/sierrasettings-sample.py` to `autoholds/sierrasettings.py`.
2. Edit `autoholds/sierrasettings.py`.
3. After the `SIERRA_API` line:
4. In the `base_url` line, change `sierra-app-server.mylibrary.url` to the hostname of your Sierra application server.
5. In the `client_key` line, change `key` to the API key.
6. In the `client_secret` line, change `secret` to the API secret (password).
7. After the `SIERRA_SQL` line:
8. In the `host` line, change `sierra-db-server.mylibrary.url` to the hostname of your Sierra database server (not your Sierra application server).
9. In the `password` line, change `pass` to the password of the autoholds Sierra user.

Where replacing values in `sierrasettings.py` be sure to keep the triple quotes (`'''`) around each setting value.


Generate a secret key for Django
--------------------------------

1. Edit `autoholds/settings.py`.
2. In the `SECRET_KEY` line, change `CHANGE ME` to a long random string.  See the [Django documentation](https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/#secret-key) for details.

A command like the following one with generate an appropriate random string.

```
tr -dc '[[:graph:]]' < /dev/urandom | head -c 100
```


Migrate the database
--------------------

1. From within the install directory, run the command: `python manage.py migrate`.

This will create the necessary tables in the PostgreSQL database.

This will also test that the AutoHolds app can connect to the autoholds database.


Refresh the AutoHolds app
-------------------------

1. From within the install directory, run the command: `python manage.py refresh_proto`.

This will copy the formats, languages and pickup locations from your Sierra into the AutoHolds app.

This will also test that the AutoHolds app can connect to Sierra's database.


Test the AutoHolds app
----------------------

This is safe because there are no registrations in the AutoHolds app yet. No holds will be placed.

1. From within the install directory, run the command: `python manage.py autoholds`.

This will establish a starting date and time for the AutoHolds app. Only bibs created from now will be considered for AutoHolds.

This will also test that the AutoHolds app can use the API key and secret to connect to Sierra.


Create a Django superuser
-------------------------

1. From within the install directory, run the command: `python manage.py createsuperuser`.
2. Enter a username for yourself.
3. Enter your email address.
4. Enter a password for your AutoHolds Django user.

This will create an initial user in Django so you can log into the Django Admin App.


Test the AutoHolds app with the development server
--------------------------------------------------

Note that this is only temporary. While the AutoHolds app may be running during these steps, it is running insecurely.
You must properly deploy the AutoHolds app before allowing access to it beyond yourself.

### Start the development server

1. Open tcp port 12345 in your server's firewall to allow access from your computer.
2. From within the install directory, start the development server by running the command: `python manage.py runserver --insecure 12345`.

Note that port 12345 is arbitrary. If that port is not available on the server, choose another.

### Test the patron web pages

1. In a browser go to `http://autoholds.server.url:12345/`, but substitute the hostname of the server running the AutoHolds app.
2. You should be redirected to `http://autoholds.server.url:12345/patron/login`.
3. Log in with your patron barcode.
4. You should be redirected to `http://localhost:12345/patron/` and you should see your name in the blue bar.
5. Click on the Pickup Location drop-down and you should see your library's pickup locations.
6. Click on the Preferred Format drop-down and you should see your library's formats.
7. Click on the Preferred Lanaguage drop-down and you should see your library's languages.
8. Click Logout.

### Test the admin web pages

1. In a browser go to `http://autoholds.server.url:12345/admin`, but substitute the hostname of the server running the AutoHolds app.
2. Log in with your Django superuser username and password.
3. Click on Users and you should see your superuser.
4. Click on Home and then click on Formats, you should see your library's formats.
5. Click on Home and then click on Languages, you should see your library's languages.
6. Click on Home and then click on Pickup Locations, you should see your library's pickup locations.
7. Click Log Out.

### Stop the development server

1. Stop the development server by hitting Ctrl+C. 
2. Close tcp port 12345 in your server's firewall.


Deploy the AutoHolds app into production
----------------------------------------

1. Edit `autoholds/settings.py`.
2. In the `DEBUG` line, change `True` to `False`. There should be no quotes around `False`.

Follow through the [Django documentation](https://docs.djangoproject.com/en/1.9/howto/deployment/) to deploy the app into production.

Particularly take a look at the [deployment checklist](https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/).

Strongly consider getting a certificate for your server and only using HTTPS for the AutoHolds app.