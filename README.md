# Omeka S

Info on some docker images https://forum.omeka.org/t/omeka-s-docker-image-for-version-3-0/13247/3, the current image is taken from https://git.biblibre.com/docker/omeka-s.

## Base commands

Assuming docker-compose is properly installed, just run `docker-compose -p omeka up -d` in this folder to start the deployment. `docker-compose -p omeka down` to stop it.

The Omeka S instance is then accessible at `http://localhost:8080`.

An initial user is created as:
```
email: admin@dummymail.com
password: admin_default_password
```

It should be be changed at the first login to avoid security issues.

## Modules

The `docker-compose.yml` specifies the local `omeka-modules` folder as a volume. So adding modules can easily be done by just running the following commands

```
mkdir omeka-modules
cd omeka-modules
wget https://github.com/omeka-s-modules/Collecting/releases/download/v1.6.1/Collecting-1.6.1.zip
unzip Collecting-1.6.1.zip

wget https://github.com/omeka-s-modules/ValueSuggest/releases/download/v1.8.0/ValueSuggest-1.8.0.zip
unzip ValueSuggest-1.8.0.zip

wget https://github.com/zerocrates/PdfEmbedS/releases/download/v1.2.0/PdfEmbed-1.2.0.zip
unzip PdfEmbed-1.2.0.zip
```

## Things to address for deployment

### HTTPS

Can probably be done by having a local proxy server in front (like `nginx`) and using certbot for https configuration of the proxy server.

### Automatic Thumbnail of PDFs

Needs to change imagemagick policy so that it process PDFs
https://forum.omeka.org/t/thumbnail-image-icon-for-pdfs/6680/9

### Omeka Media as a volume directory

Currently the media files (such as PDFs) directory is not a volume and is probably erased between docker restarts, that needs to be addressed.

### Backups

Probably the easiest way to do it is by saving the docker volumes. For instance, we could change them to be local directories (just like the modules), and save them to `.tar` files and upload them to a S3 or equivalent long term storage. It is important that the deployment would be shut down before saving the directories to avoid conccurent read/writes.

The backup procedure should be tried before deploying.


# Notes (for Benoit)

## Full-text-search

https://forum.omeka.org/t/what-are-the-best-practices-for-full-text-search-with-omeka-s/5891

https://www.biblibre.com/fr/blog/rechercher-avec-solr-dans-omeka-s-1-installation-et-configuration-minimale/

## API

Credentials generated from the admin dashboard
- key_identity: 5UxoiInyatZiEIpUOmB9YOPXkrENK3IE
- key_credential: dhz4REYtv7E8qabZ1CMxz4KmiAZFCHCi

## PDF thumbnails

Needs to change imagemagick policy so that it process PDFs
https://forum.omeka.org/t/thumbnail-image-icon-for-pdfs/6680/9

# OCR

OCR solutions:
    Opensource -> Kraken
    https://github.com/mittagessen/kraken
    Arabic model https://github.com/mittagessen/kraken/issues/121
    Commercial -> Google OCR

OCR arabic
https://github.com/OpenITI/OCR_GS_Data


Directly convert to OCRized PDF https://github.com/jbarlow83/OCRmyPDF
Possible to add plugins to add OCREngine https://github.com/jbarlow83/OCRmyPDF/blob/master/src/ocrmypdf/pluginspec.py#L321


# CollectiveAccess

Single docker file 1.7.11 https://github.com/GovernoRegionalAcores/collectiveaccess
Docker compose 1.7.8 https://github.com/pkuehne/collectiveaccess

In collectiveaccess repo (which is the compose repo with the version updated to 1.7.11), just build the image `docker build . -t collective` then run `docker-compose -p collectiveaccess up -d`.

Needs to install by going to `127.0.0.1:8080/providence/install`

Collectiveaccess 
- admin, h3r1tag3