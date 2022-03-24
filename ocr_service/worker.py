import os
import time
import omeka
import ocr

KEY_IDENTITY = os.environ['OMEKA_S_API_KEY_IDENTITY']
KEY_CREDENTIAL = os.environ['OMEKA_S_API_KEY_CREDENTIAL']

print("Starting worker")
omeka_api = omeka.OmekaSGateway("http://omeka", key_identity=KEY_IDENTITY, key_credential=KEY_CREDENTIAL)

PROPERTY_TO_MONITOR = os.environ['PROPERTY_TO_MONITOR']
PROPERTY_ERROR_MESSAGE = os.environ['PROPERTY_ERROR_MESSAGE']
CLASS_GENERATED_PAGE = os.environ['CLASS_GENERATED_PAGE']
CLASS_PROCESSED_MEDIA = os.environ['CLASS_PROCESSED_MEDIA']

ocr_processor = ocr.OCRProcessor(omeka_api, PROPERTY_TO_MONITOR, PROPERTY_ERROR_MESSAGE, CLASS_GENERATED_PAGE, CLASS_PROCESSED_MEDIA)


while True:
    for item in ocr_processor.list_items_to_process():
        item_id = item['o:id']
        ocr_processor.clean_item(item_id)
        ocr_processor.process_item(item_id)

    time.sleep(10.0)
