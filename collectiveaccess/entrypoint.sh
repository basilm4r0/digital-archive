#!/bin/bash
set -e

#DATABASE INIT/CONFIG
echo "Initializing configuration database..."
mysql --host=$DB_HOST --user=root --password=$DB_ROOT_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"
mysql --host=$DB_HOST --user=root --password=$DB_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER' IDENTIFIED BY '$DB_PASSWORD';"

# Create necessary directories and own them to www-data
echo "Creating necessary directories and owning them to www-data..."
cd $CA_PROVIDENCE_DIR/media && mkdir -p collectiveaccess
cd $CA_PROVIDENCE_DIR/media/collectiveaccess && mkdir -p tilepics images
cd $CA_PAWTUCKET_DIR && chown www-data:www-data . -R && chmod -R u+rX .
cd $CA_PROVIDENCE_DIR && chown www-data:www-data . -R && chmod -R u+rX .

if [[ ! "$(ls -A /$CA_PROVIDENCE_DIR/app/conf/)" ]]; then
	cp -r /var/ca/providence/conf/* /$CA_PROVIDENCE_DIR/app/conf/
fi

sweep() {
	local ca="$ca"
	sed -i -e "/__CA_DB_HOST__/s/'.*'/'$DB_HOST'/" setup.php
	sed -i -e "/__CA_DB_USER__/s/'.*'/'$DB_USER'/" setup.php
	sed -i -e "/__CA_DB_PASSWORD__/s/'.*'/'$DB_PASSWORD'/" setup.php
	sed -i -e "/__CA_DB_DATABASE__/s/'.*'/'$DB_NAME'/" setup.php

	if [[ "$DISPLAY_NAME" != "" ]];then
		sed -i -e "/__CA_APP_DISPLAY_NAME__/s/\"M.*m\"/\"$DISPLAY_NAME\"/" setup.php
	fi
	if [[ "$ADMIN_EMAIL" != "" ]];then
		sed -i -e "/__CA_ADMIN_EMAIL__/s/'.*'/'$ADMIN_EMAIL'/" setup.php
	fi
	if [[ "$SMTP_SERVER" != "" ]];then
		sed -i -e "/__CA_SMTP_SERVER__/s/'.*'/'$SMTP_SERVER'/g" setup.php
	fi
}
cd $CA_PROVIDENCE_DIR
ca='pro'
sweep $ca
cd $CA_PAWTUCKET_DIR
ca='paw'
sweep $ca

echo "Running image..."
exec "$@"
