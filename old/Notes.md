# Notes (for Benoit)

## Full-text-search

https://forum.omeka.org/t/what-are-the-best-practices-for-full-text-search-with-omeka-s/5891

https://www.biblibre.com/fr/blog/rechercher-avec-solr-dans-omeka-s-1-installation-et-configuration-minimale/
https://www.biblibre.com/fr/blog/rechercher-avec-solr-dans-omeka-s-2-facettes/

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

# CollectiveAccess

Single docker file 1.7.11 https://github.com/GovernoRegionalAcores/collectiveaccess
Docker compose 1.7.8 https://github.com/pkuehne/collectiveaccess

In collectiveaccess repo (which is the compose repo with the version updated to 1.7.11), just build the image `docker build . -t collective` then run `docker-compose -p collectiveaccess up -d`.

Needs to install by going to `127.0.0.1:8080/providence/install`

Collectiveaccess 
- admin, h3r1tag3
