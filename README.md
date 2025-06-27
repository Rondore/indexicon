# About

Indexicon is a tool to building an index of files in open directories (ODs). ODs are also known as *index of* webpages since they often have a page title like *Index of "/"*. ODs can contain all sorts of files

# Installing

Indexicon does not have any built-in security. Unless you are binding it to a loopback network device (127.0.0.1) and are on a single-user computer, you will need to proxy through another server such as nginx and setup authentication there. If you are running this on a home network, using an nginx proxy to password-protect the admin page is advised.

## Docker

Docker is the easiest way to run indexicon. First, install Docker and Docker-Compose if you do not already have it on your system. The only other thing you will need is a folder to store the persistent data and optionally a folder for any addon functionality.

First, let's create our folders. They can be stored anywhere, but for our exampel we will be using a folder in our user's `.config` folder. We can make them by running these commands:

```bash
mkdir -p ~/.config/indexicon/data
mkdir -p ~/.config/indexicon/addon
```

Next, lets set up our docker service file. Start by downloading the default one and saving it into our indexicon folder:

```bash
curl 'https://raw.githubusercontent.com/Rondore/indexicon/refs/heads/master/docker-compose.yaml' > ~/.config/indexicon/docker-compose.yaml
```

Now you can configure the options in the `docker-compose.yaml` file with a text editor. The options are set in the `enviroment:` section. Each option is detailed in the Configuration section below. Each value name in the configuration file aligns with the following setting:

```
INDEXICON_DB_TYPE      db_type
INDEXICON_DB_DB        db_db
INDEXICON_DB_USER      db_user
INDEXICON_DB_PASSWORD  db_password
INDEXICON_DB_HOST      db_host
INDEXICON_DB_POOL      db_pool

INDEXICON_NAME         name
INDEXICON_INTERNAL_URL internal_base_url
INDEXICON_PUBLIC_URL   public_base_url
INDEXICON_LOG          scrape_log
INDEXICON_MIN_AGE      min_age
INDEXICON_USER_AGENT   user_agent

INDEXICON_EXTENSIONS   extensions
```

All configuration values are set as the Configuration describes except for `INDEXICON_EXTENSIONS` which uses a pipe-seperated list like this: `"doc|docx"`

If you want to run the service on the standard http port 80, change `127.0.0.1:8080:80` to `127.0.0.1:80:80`. If you want to be able to reach the service from other devices on your network, change `127.0.0.1` to `0.0.0.0`.

Any settings you set in the docker compose file will override any settings you set in `data/settings.py`.

Once your configuration is saved, you can `cd` into the directory containing the compose file and launch it with one of the following commands depending on which version of docker you are running:

```bash
docker-compose up -d
```

```bash
docker compose up -d
```

You should now be able to access the service in your browser at `localhost:8080`. If you changed the port from 8080 to 80, you can use `localhost`.

## Running From Source

```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
git clone 'https://github.com/Rondore/indexicon.git'
cd indexicon
python3 -m venv venv
./venv/bin/pip3 install -r requirements.txt
```

Now you can configure the options in Configuration section by creating a file called `settings.py` inside your data folder and adding the following content:

```python
#!/usr/bin/env python3

import settings

settings.db_type = 'maria'
```

Each setting can be set with a new line imitating the db_type.

Once your configuration is saved, you can launch indexicon with the following command:

```bash
./.venv/bin/flask run -h 127.0.0.1 -p 80
```

If you want to be able to reach the service from other devices on your network, change `127.0.0.1` to `0.0.0.0`.

# Configuration

Here is an example of a settings file you can save as `data/settings.py`

```
#!/usr/bin/env python3

import settings

settings.db_type = 'mariadb'
settings.db_db = 'indexicon'
settings.db_user = 'indexicon'
settings.db_password = 'bad_password'
settings.db_host = '192.168.0.1'
settings.db_pool = 5

settings.name = 'Indexicon'
settings.local_base_url = "/"
settings.public_base_url = local_base_url
settings.scrape_log = 'scrape.log'
settings.min_age = 604800
settings.user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0'

settings.extensions = ['doc','docx']
```

## Database

When using sqlite (the default) database type, the user, password and host values are not used.

### `db_type`

Indexicon can use either SQLite or MariaDB/MySQL to store persistent data.

### `db_db`

Setting this value to 'maria' or 'mariadb' will switch Indexicon to use MariaDB. Using 'mysql' will switch Indexicon to use MySQL. Any other value set for `db_db` will cause Indexicon to use SQLite.

### `db_user`

When using MariaDB/MySQL, this value is the username to use to log into the database.

### `db_password`

When using MariaDB/MySQL, this value is the password to use to log into the database.

### `db_host`

When using MariaDB/MySQL, this value is the server hostname to use to access the database.

### `db_pool`

The number of connections in the MariaDB/MySQL connection pool. Increase this value if you run into "pool exhausted" errors.

## Other Options

### `extensions`

This value is used to determine which files from each open directory should be saved into the database.

The value of `extenstions` is a list of file extensions that are saved. In `settings.py`, this value is a python list such as `["jpg", "jpeg", "png"]`. When using docker environment variables, the vale is specified in a pipe-seperated list like so: `"jpg|jpeg|png"`. When this option is left blank (the default), all files are indexed.

### `name`

The name of the site.

This value is used in the html head and some page titles. The default value is `Indexicon`.

### `internal_base_url`

The base url after the domain and port number to use for incoming requests.

If you are hosting inexicon on it's own domain or IP address, use '/' (the default).

If you are hosting Indexicon from a folder on a server that runs multiple apps, and you serve Indexicon from `http://example.com/indexicon/admin` by way of a proxy, you can forward the request as either `/indexicon/admin` or `/admin`. When using ther former, this value would be `/indexicon/`, and for the later, `/`.

### `public_base_url`

The base url after the domain and port number to use for links.

If you are hosting inexicon on it's own domain or IP address, use '/' (the default).

If you are hosting Indexicon from a folder on a server that runs multiple apps, and you serve Indexicon from `http://example.com/indexicon/admin` by way of a proxy, this value would be `/indexicon/`.

The only time this value should be different from `internal_base_url` is when a proxy is stripping part of the URL off the path when forwarding the request.

### `scrape_log`

The file to log the most recent scrape to.

The log is reset for each scrape. The default is `data/scrape.log`.

### `min_age`

When running a full scrape, any sources that have been scraped less than this many seconds ago are skipped. This allows you to run full scrapes on a schedule or after adding a new sources and not bog down servers. 86400 seconds = 1 day; 604800 seconds = 1 week.

### `user_agent`

The browser user-agent to use for all scraping web requests. This value should be updated fairly regularly to avoid being blocked by some servers.

## Addon

You can customize some functinality by adding content to the addon folder. Details can be found in [ADDON.md](ADDON.md)

# Operating

## Admin

To make indexicon operational, we first need to add sources to scrape. On the admin page, enter URLs of open directories to scrape and hit enter. When adding sources, be sure to include the trailing slash in the URL.

We can set folders to skip during a scrape. This can be important if the server has a hard or soft links in it's filesystem that lead to infinite recursion. To set a folder to be passed over during a scrape, paste the full URL of the folder to skip into the passover field and hit enter.

## Search

The search field is a basic search. It locates files that contain every word in the search. The search is case insensitive. The only advanced search feature included is the minus word feature. To exclude files that contain a word, enter a minus with the word imediately afterwords like this: `cat gif -thumbnail`

## Running Recursive Downloads

If you want to download all the files in an open directy (or just a folder of it) you can supply the url to a built in script. This can only be done from the terminal.

### Download (installed from source)

First navigate to the folder you want save the files in. Then activate the python environment. This step does not need to be repeated between downloads as long as the shell stays running. You will need to use the path where you installed indexicon.

```bash
source /home/user/indexicon/venv/bin/activate
```

Now navigate to the download directory. Then enter the path of the download script and the url to download from:

```bash
/home/user/indexicon/full_download.py 'http://example.com/cat-memes/'
```

### Download (docker)

When using a docker instance of indexicon, you will need to mount an extra download folder to run recursive downloads. Once the download mount is set up run something like `docker exec -it indexicon bash` to start a shell. Then navigate to your download directory.

Now just enter the path of the download script and the url to download from:

```bash
/usr/src/app/full_download.py 'http://example.com/cat-memes/'
```