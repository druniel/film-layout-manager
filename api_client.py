import time
import requests
from PySide6.QtCore import QThread, Signal

class ApiWorker(QThread):
    success = Signal(str)
    error = Signal(str)
    
    def __init__(self, api_url, token, homepage, payload):
        super().__init__()
        self.api_url = api_url
        self.token = token
        self.homepage = homepage
        self.payload = payload
        
    def _make_request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.api_url}{endpoint}"
        
        if "headers" not in kwargs:
            kwargs["headers"] = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
            
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = requests.request(method, url, timeout = 10, **kwargs)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                last_error = e
                time.sleep(2)
        
        raise Exception(f"Chyba komunikace s API: {max_retries} pokusů selhalo. Poslední chyba: {last_error}")
        
    def run(self):
        try:
            country_map = {"cz": 60, "sk": 202}
            country_id = country_map.get(self.homepage, 60)
            homepages_data = self._make_request("GET", f"/admin/homepages?country={country_id}")
            homepage_info = homepages_data[0]
            
            if homepage_info.get("draft"):
                raise Exception("V CMS je už aktivní draft.")

            current_id = homepage_info["current"]["id"]
            current_name = homepage_info["current"]["name"]
            draft_payload = {"country": country_id, "name": current_name, "template": current_id}
            draft_data = self._make_request("POST", "/admin/homepages", json = draft_payload)
            updated_count = 0
            
            for section in draft_data.get("sections", []):
                section_name = section.get("name")
                
                if section_name in self.payload:
                    section_detail = self._make_request("GET", f"/admin/sections/{section['id']}")
                    custom_names_list = []
                    
                    for item in section_detail.get("items", []):
                        for custom_name in item.get("custom_names", []):
                            custom_names_list.append({"id": item["play_id"], "name": custom_name})
                    
                    update_payload = {"custom_names": custom_names_list, "landing_page": section_detail.get("landing_page", False), "names": section_detail.get("names", []), "plays": self.payload[section_name]}
                    self._make_request("PUT", f"/admin/sections/{section['id']}", json = update_payload)
                    updated_count += 1
            self.success.emit(f"Úspěšně aktualizováno {updated_count} sekcí.")
            
        except Exception as e:
            self.error.emit(str(e))