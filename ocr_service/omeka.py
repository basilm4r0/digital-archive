import requests
import json
import pprint
from typing import Optional, List, Dict, Any

class OmekaSGateway(object):
    def __init__(self, install_location, key_identity, key_credential):
        self.install_location = install_location
        self.key_identity = key_identity
        self.key_credential = key_credential

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
        elif method == "DELETE":
            r = requests.delete(uri, params=auth_params)
        else:
            raise NotImplementedError(f"method='{method}'")
        return r.json()
        
    def create_page(self, data):
        return self._request_endpoint('site_pages', params=data, method="POST")

    def get_item_by_id(self, item_id: int) -> dict:
        return self._request_endpoint(f'items/{item_id}')

    def get_media_by_id(self, media_id: int) -> dict:
        return self._request_endpoint(f'media/{media_id}')

    def delete_item_by_id(self, item_id: int) -> dict:
        return self._request_endpoint(f'items/{item_id}', method="DELETE")

    def delete_media_by_id(self, media_id: int) -> dict:
        return self._request_endpoint(f'media/{media_id}', method="DELETE")

    def get_property_id(self, property_name: str) -> int:
        d = self._request_endpoint('properties', params=dict(term=property_name))
        assert len(d) == 1, f"Could not find property {property_name}"
        return d[0]["o:id"]

    def get_resource_class_id(self, class_name: str) -> int:
        d = self._request_endpoint('resource_classes', params=dict(term=class_name))
        assert len(d) == 1, f"Could not find class {class_name}"
        return d[0]["o:id"]

    def get_resource_template_id(self, property_name: str) -> int:
        d = self._request_endpoint('resource_templates', params=dict(term=property_name))
        assert len(d) == 1, f"Could not find resource_template {property_name}"
        return d[0]["o:id"]

    def list_site_pages(self):
        return self._request_endpoint('site_pages')

    def list_items(self, resource_template_id: Optional[int] = None,
                   resource_class_id: Optional[int] = None, property_filters: Optional[List[Dict[str, Any]]] = None,
                   sort_by="modified", sort_order="desc"):
        params = {}
        if resource_template_id:
            params['resource_template_id'] = resource_template_id
        if resource_class_id:
            params['resource_class_id'] = resource_class_id
        params['sort_by'] = sort_by
        params['sort_order'] = sort_order
        if property_filters:
            for i, property_filter in enumerate(property_filters):
                for k, v in property_filter.items():
                    params[f'property[{i}][{k}]'] = v
                # params[f'property[{i}][property]'] = _id
                # params[f'property[{i}][type]'] = "eq"
                # params[f'property[{i}][text]'] = _term
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

    def add_item(self, data):
        return self._request_endpoint('items', data, method='POST')

    def add_media(self, item_id: int, filename: str, file_data: bytes, mimetype: str, resource_class_id: Optional[int] = None):
        params = {
            "o:ingester": "upload", 
            "file_index": "0", 
            "o:item": {"o:id": item_id}
        }
        if resource_class_id is not None:
            params["o:resource_class"] = {"o:id": resource_class_id}

        files = [
            ('file[0]', (filename, file_data, mimetype))
        ]
        return self._request_endpoint('media', params, method="POST", files=files)
