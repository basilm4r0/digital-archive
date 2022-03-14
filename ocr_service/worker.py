import os
import time
import omeka
import ocr

KEY_IDENTITY = os.environ['KEY_IDENTITY']
KEY_CREDENTIAL = os.environ['KEY_CREDENTIAL']

print("Starting worker")
omeka_api = omeka.OmekaSGateway("http://omeka", key_identity=KEY_IDENTITY, key_credential=KEY_CREDENTIAL)


while True:

    print(len(omeka_api.list_items()), len(omeka_api.list_medias()))
    time.sleep(2.0)
