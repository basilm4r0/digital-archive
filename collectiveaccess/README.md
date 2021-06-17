# CollectiveAccess

## About

- This image does not contain MySQL, it needs to be linked
- Contains both Providence and Pawtucket2
- Pawtucket is accessed by `https://domain_or_ipaddress:port/`
- Providence is accessed by `https://domain_or_ipaddress:port/providence`

## Note

You should not use the `latest` tag, it is unstable and can break.

Please use from tag 1.0.0 onwards.

The `DISPLAY_NAME` is the name of your archive that will show in the tab title and on Pawtucket.

## Pull Requests

If you fork the repo and make some changes that other's can use as well, please contribute them back as a PR!

Thanks to @martjanz for contributing.

## Usage with Docker Compose

`docker-compose -p collectiveaccess up -d`

The first time this command is run MySQL database will be created from scratch.

If any error occur you can check containers status with `docker ps -a` and if something happened on backend container probably is due to a lagged start of MySQL server. Running `docker-compose -p film up -d` will trigger a backend restart and will fix it.

Providence (admin UI) will be running on http://server-ip:8080/providence
Pawtucket (client UI) will be running on http://server-ip:8080/

## Usage with Docker

    # Run mysql container
    docker run
        --name ca_mysql
        -e MYSQL_USER=user
        -e MYSQL_PASSWORD=pass
        -e MYSQL_DATABASE=collective
        -e MYSQL_ROOT_PASSWORD=rootpass
        -v /var/ca/mysql:/var/lib/mysql
        -d
        mysql:5.7

    # Run the collective access container
    docker run
        -–link ca_mysql:mysql
        -p 8080:80
        -e DB_HOST=ca_mysql
        -e DB_USER=user
        -e DB_PASSWORD=pass
        -e DB_NAME=collective
        -e DISPLAY_NAME="My Archive"        # optional
        -e ADMIN_EMAIL=admin@my-archive.tld # optional
        -e SMTP_SERVER=mail.my-archive.tld  # optional
        -v /var/ca/conf:/var/www/providence/app/conf
        -v /var/ca/media:/var/www/providence/media/
        pkuehne/collectiveaccess:1.1.0

    # Go to https://domain_or_ip:8080/providence to setup the database structure

## Image build

`docker build --tag collective:latest .`
