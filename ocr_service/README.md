# OCR Service

The OCR service has a relatively simple behaviour:

- It checks for items with the property `PROPERTY_TO_MONITOR` (default: `sabil:documentProcessingStatus`) equal to `TO_BE_PROCESSED`
- For each of the items found:
    - It first "cleans" it: removing previously generated pages items, and previous OCRized media
    - The item should be valid: only one PDF media attached to it.
    - It performs the OCR with `ocrmypdf` (i.e. Tesseract 5) on each page separately
        - The languages used for the OCR are defined thanks to the `dcterms:language` values of the original item. Each language is assumed to be a text entry (a litteral) whose lower-case version starts by one of the language mapped in `languages.json` to their ISO 639-2 codes (used by tesseract) (for instance `Arabic <skjshkds>` is valid as `arabic` is in `languages.json`). If no `dcterms:language` are available, the combination of `english` and `arabic` is used.
        - It creates a separate item (of class `CLASS_GENERATED_PAGE`, default: `sabil:GeneratedPage`) for each page with the OCRized text as `bibo:content` field, a `dcterms:title` derived from the title of the original item, and a OCRized PDF of the page attached as media to it.
        - The individual OCRized PDF pages are merged together in a single file which is attached as media to the original item, this media has class `CLASS_PROCESSED_MEDIA` (default: `sabil:ProcessedMedia`). The original input media file is set as private to be hidden from public viewing.
        - The `PROPERTY_TO_MONITOR` of the original item is set to `PROCESSED`
    - If processing of the item failed
        - The `PROPERTY_TO_MONITOR` of the original item is set to `FAILURE`
        - An error message is attached (privately) to the original item with `PROPERTY_ERROR_MESSAGE` (default: `sabil:documentProcessingFailureMessage`)
- Reprocessing of an item can then be done by setting its `PROPERTY_TO_MONITOR` back to `TO_BE_PROCESSED`

