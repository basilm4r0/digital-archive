import os
import time
import omeka
import ocr

KEY_IDENTITY = os.environ['KEY_IDENTITY']
KEY_CREDENTIAL = os.environ['KEY_CREDENTIAL']

print("Starting worker")
omeka_api = omeka.OmekaSGateway("http://omeka", key_identity=KEY_IDENTITY, key_credential=KEY_CREDENTIAL)

MONITORED_CLASS_IDS = []
for class_term in os.environ['CLASSES_TO_MONITOR'].split(','):
    class_id = omeka_api.get_resource_class_id(class_term)
    print(f"Monitoring class {class_term} (id={class_id})")
    MONITORED_CLASS_IDS.append(class_id)

ocr_processor = ocr.OCRProcessor(omeka_api)


while True:
    for class_id in MONITORED_CLASS_IDS:
        for item in omeka_api.list_items(resource_class_id=class_id, sort_by="modified", sort_order="desc"):
            try:
                item_id = item['o:id']
                was_processed = ocr_processor.process_item(item['o:id'])
                if not was_processed:
                    print(f"Finished processing items associated with class_id={class_id}")
                    break
            except Exception as e:
                print(f"Failed processing item {item_id}. Reason {e}")

    time.sleep(10.0)
