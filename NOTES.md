

# CollectiveAccess

Single docker file 1.7.11 https://github.com/GovernoRegionalAcores/collectiveaccess
Docker compose 1.7.8 https://github.com/pkuehne/collectiveaccess

In collectiveaccess repo (which is the compose repo with the version updated to 1.7.11), just build the image `docker build . -t collective` then run `docker-compose -p collectiveaccess up -d`.

Needs to install by going to `127.0.0.1:8080/providence/install`

Collectiveaccess 
- admin, h3r1tag3

# Omeka S

Info on some docker images https://forum.omeka.org/t/omeka-s-docker-image-for-version-3-0/13247/3

`docker-compose -p omeka up -d` in this folder, does mount the `omeka-modules` folder as a volume.

`docker exec omeka_solr_1 bin/solr create_core -c omeka-s` to initialize solr core

Set `solr:8983/solr/omeka-s` for the url of the solr core.

http://34.65.82.241/admin
seg.benoit@gmail.com
r365Yl1fN&M

```
mkdir omeka-modules
cd omeka-modules
wget https://github.com/omeka-s-modules/Collecting/releases/download/v1.6.1/Collecting-1.6.1.zip
unzip Collecting-1.6.1.zip

wget https://github.com/omeka-s-modules/ValueSuggest/releases/download/v1.8.0/ValueSuggest-1.8.0.zip
unzip ValueSuggest-1.8.0.zip

wget https://github.com/zerocrates/PdfEmbedS/releases/download/v1.2.0/PdfEmbed-1.2.0.zip
unzip PdfEmbed-1.2.0.zip

wget https://github.com/biblibre/omeka-s-module-Search/releases/download/v0.9.0/Search-0.9.0.zip
unzip Search-0.9.0.zip
rm Search-0.9.0.zip
wget https://github.com/biblibre/omeka-s-module-Solr/releases/download/v0.9.0/Solr-0.9.0.zip
unzip Solr-0.9.0.zip
rm Solr-0.9.0.zip
```


## Full-text-search

https://forum.omeka.org/t/what-are-the-best-practices-for-full-text-search-with-omeka-s/5891

https://www.biblibre.com/fr/blog/rechercher-avec-solr-dans-omeka-s-1-installation-et-configuration-minimale/
https://www.biblibre.com/fr/blog/rechercher-avec-solr-dans-omeka-s-2-facettes/

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
Generating PDF is probably not super simple though, generating hocr is probably the safest route, but according to https://ocrmypdf.readthedocs.io/en/latest/advanced.html#the-hocr-renderer the hocr pdf renderer does not handle non-latin script characters.

Kraken arabic model https://github.com/OpenITI/OCR_GS_Data/blob/master/ara/abhath/arabic_generalized.mlmodel
