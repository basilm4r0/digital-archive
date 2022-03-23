import requests
import json
import pprint
from typing import Optional, List

class OmekaSGateway(object):
    def __init__(self, install_location, key_identity, key_credential):
        self.install_location = install_location
        self.key_identity = key_identity
        self.key_credential = key_credential

    def get_final_uri(self, endpoint):
        return endpoint.format(
            self.install_location,
            self.key_identity,
            self.key_credential
        )

    def _request_endpoint(self, endpoint: str, params: Optional[dict] = None, method="GET", files=()):
        if not params:
            params = {}
        uri = f"{self.install_location}/api/{endpoint}"
        auth_params = dict(key_identity=self.key_identity, key_credential=self.key_credential)
        if method == "GET":
            assert len(files) == 0
            r = requests.get(uri, params={**auth_params, **params})
        elif method == "POST":
            if files:
                files = [
                    ('data', (None, json.dumps(params), 'application/json')),
                    *files
                ]
                r = requests.post(uri, params=auth_params, files=files)
            else:
                r = requests.post(uri, params=auth_params, json=params)
        elif method == "PATCH":
            r = requests.patch(uri, params=auth_params, json=params)
        else:
            raise NotImplementedError(f"method='{method}'")
        return r.json()
        
    def create_page(self, data):
        return self._request_endpoint('site_pages', params=data, method="POST")

    def get_page_by_slug(self, slug):
        return next((x for x in self.list_site_pages() if x['o:slug'] == slug), None)

    def get_item_by_title(self, title):
        return next((x for x in self.list_items() if x['o:title'] == title), None)

    def get_item_by_id(self, item_id):
        return self._request_endpoint(f'items/{item_id}')

    def get_media_by_id(self, media_id):
        return self._request_endpoint(f'media/{media_id}')

    def get_property_id(self, property_name: str) -> int:
        d = self._request_endpoint('properties', params=dict(term=property_name))
        assert len(d) == 1, len(d)
        return d[0]["o:id"]

    def get_resource_class_id(self, class_name: str) -> int:
        d = self._request_endpoint('resource_classes', params=dict(term=class_name))
        assert len(d) == 1, len(d)
        return d[0]["o:id"]

    def get_resource_template_id(self, property_name: str) -> int:
        d = self._request_endpoint('resource_templates', params=dict(term=property_name))
        assert len(d) == 1, len(d)
        return d[0]["o:id"]

    def list_site_pages(self):
        return self._request_endpoint('site_pages')

    def list_items(self, resource_template_id: Optional[int] = None, resource_class_id: Optional[int] = None, sort_by="modified", sort_order="desc"):
        params = {}
        if resource_template_id:
            params['resource_template_id'] = resource_template_id
        if resource_class_id:
            params['resource_class_id'] = resource_class_id
        params['sort_by'] = sort_by
        params['sort_order'] = sort_order
        return self._request_endpoint('items', params)

    def list_medias(self, resource_template_id: Optional[int] = None, resource_class_id: Optional[int] = None):
        params = {}
        if resource_template_id:
            params['resource_template_id'] = resource_template_id
        if resource_class_id:
            params['resource_class_id'] = resource_class_id
        return self._request_endpoint('media', params)

    def update_item(self, id_item, data):
        return self._request_endpoint(f'items/{id_item}', data, method='PATCH')

    def update_media(self, id_media, data):
        return self._request_endpoint(f'media/{id_media}', data, method='PATCH')

    # def create_item_with_media(self, item_payload, path, mime_type):
    #     endpoint = "{}/api/items?key_identity={}&key_credential={}"
    #     postdata = {}

    #     final_uri = endpoint.format(
    #         self.install_location,
    #         self.key_identity,
    #         self.key_credential
    #     )

    #     r = requests.post(final_uri, data={'data': json.dumps(item_payload)}, files=[
    #         ('file[0]', (path, open(path, 'rb'), mime_type))
    #     ])

    #     if r.ok:
    #         return r.json()
    #     else:
    #         raise Exception(r.json()['errors']['error'])

    def add_item(self, data):
        return self._request_endpoint('items', data, method='POST')

    def add_media(self, item_id: int, filename: str, file_data: bytes, mimetype: str):
        params = {
            "o:ingester": "upload", 
            "file_index": "0", 
            "o:item": {"o:id": item_id},
            #"o:resource_template": {"o:id": resource_template_id},
        }

        files = [
            ('file[0]', (filename, file_data, mimetype))
        ]
        return self._request_endpoint('media', params, method="POST", files=files)
