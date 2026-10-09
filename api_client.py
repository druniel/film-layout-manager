import time
import requests
from requests.exceptions import HTTPError, Timeout, RequestException
from PySide6.QtCore import QThread, Signal
import json

class ApiWorker(QThread):
    success = Signal(str)
    error = Signal(str, dict)
    token_expired = Signal()
    
    def __init__(self, api_url, token, homepage, payload, recovery_state = None):
        super().__init__()
        self.api_url = api_url.rstrip("/")
        self.token = token
        self.homepage = homepage
        self.payload = payload
        self.state = recovery_state or {"draft_id": None, "completed_sections": []}
        
    def _make_request(self, method: str, endpoint: str, retry: bool = True, **kwargs):
        url = f"{self.api_url}{endpoint}"
        
        if "headers" not in kwargs:
            kwargs["headers"] = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
            
        max_retries = 3 if retry else 1
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = requests.request(method, url, timeout = 10, **kwargs)
                response.raise_for_status()
                return response.json()
            except HTTPError as e:
                if e.response is None:
                    raise Exception(f"Chyba komunikace (bez odpovědi serveru): {e}")
                status = e.response.status_code
                if status == 401:
                    self.token_expired.emit()
                    return None
                elif status == 403:
                    raise Exception("Chyba oprávnění: Nemáte přístup k této akci.")
                elif status >= 500:
                    last_error = e
                else:
                    raise Exception(f"Chyba API ({status}): {e.response.text}")
            except RequestException as e:
                last_error = e
                
            if retry and attempt < max_retries -1:
                time.sleep(2)
        
        raise Exception(f"Chyba komunikace s API: {max_retries} pokusů selhalo. Poslední chyba: {last_error}")
        
    def run(self):
        try:
            country_map = {"cz": 60, "sk": 202}
            country_id = country_map.get(self.homepage, 60)
            
            if not self.state["draft_id"]:
                homepages_data = self._make_request("GET", f"/admin/homepages?country={country_id}")
                if homepages_data is None: return
                if not homepages_data:
                    raise Exception("Pro tuto zemi nebyla nalezena žádná homepage.")    
                if len(homepages_data) > 1:
                    raise Exception("Server vrátil více homepages. Výběr není jednoznačný.")
                homepage_info = homepages_data[0]
                if homepage_info.get("draft"):
                    raise Exception("V CMS je už aktivní draft.")

                current_id = homepage_info["current"]["id"]
                current_name = homepage_info["current"]["name"]
                current_detail = self._make_request("GET", f"/admin/homepages/{current_id}")
                if current_detail is None: return
                server_section_names = [s.get("name") for s in current_detail.get("sections", [])]
            
                for cat_name in self.payload.keys():
                    occurrences = server_section_names.count(cat_name)
                    if occurrences == 0:
                        raise Exception(f"Kategorie '{cat_name}' na aktuální homepage neexistuje.")
                    elif occurrences > 1:
                        raise Exception(f"Kategorie '{cat_name}' se na homepage vyskytuje vícekrát ({occurrences}x). Mapování není jednoznačné.")
            
                draft_payload = {"country": country_id, "name": current_name, "template": current_id}
                try:
                    draft_data = self._make_request("POST", "/admin/homepages", json = draft_payload)
                    if draft_data is None: return
                except Timeout:
                    check_data = self._make_request("GET", f"/admin/homepages?country={country_id}")
                    if check_data and check_data[0].get("draft"):
                        draft_data = self._make_request("GET", f"/admin/homepages/{check_data[0]['draft']['id']}")
                        if draft_data is None: return
                    else:
                        raise Exception("Spojení při vytváření draftu vypršelo a draft nebyl nalezen. Zkuste to znovu.")
                self.state["draft_id"] = draft_data["id"]
            else:
                draft_data = self._make_request("GET", f"/admin/homepages/{self.state['draft_id']}")
                if draft_data is None: return
                if draft_data.get("date_published_from") is not None:
                    raise Exception("Přerušený draft již byl mezitím publikován. Nelze pokračovat.")
            
            for section in draft_data.get("sections", []):
                section_name = section.get("name")
                section_id = section.get("id")
                is_landing_page = section.get("landing_page", False)
                
                if section_name in self.payload and section_id not in self.state["completed_sections"]:
                    section_detail = self._make_request("GET", f"/admin/sections/{section_id}")
                    if section_detail is None: return
                    hints_data = self._make_request("GET", f"/admin/sections/{section_id}/hints?limit=10000")
                    if hints_data is None: return
                    valid_ids = {item["id"] for item in hints_data}
                    plays_list = self.payload[section_name]
                    
                    for film_id in plays_list:
                        if film_id not in valid_ids:
                            raise Exception(f"Validace selhala u sekce '{section_name}': Film s ID {film_id} neexistuje, nebo do této kategorie žánrově nepatří. Zkontrolujte zdrojový Excel.")
                    
                    custom_names_list = [{"id": i["play_id"], "name": custom_name} for i in section_detail.get("items", []) for custom_name in i.get("custom_names", []) if i["play_id"] in plays_list]
                    if not all(isinstance(film_id, int) for film_id in plays_list):
                        raise Exception(f"Kritická chyba: Do sekce '{section_name}' se snažíte odeslat nečíselné ID.")
                    if len(plays_list) != len(set(plays_list)):
                        raise Exception(f"Kritická chyba: Do sekce '{section_name}' se snažíte odeslat duplicitní ID.")
                    update_payload = {"custom_names": custom_names_list, "landing_page": is_landing_page, "names": section_detail.get("names", []), "plays": plays_list}
                    print(f"\n--- ODESÍLÁM PAYLOAD PRO SEKCI: {section_name} (ID: {section_id}) ---")
                    print(json.dumps(update_payload, indent=2, ensure_ascii=False))
                    print("---------------------------------------------------\n")
                    self._make_request("PUT", f"/admin/sections/{section['id']}", json = update_payload)
                    self.state["completed_sections"].append(section_id)
                    
            verify_draft = self._make_request("GET", f"/admin/homepages/{self.state['draft_id']}")
            if verify_draft is None: return
            if verify_draft.get("date_published_from") is not None:
                raise Exception("Kritická chyba: Draft byl publikován!")
            
            for s in verify_draft.get("sections", []):
                name = s.get("name")
                if name in self.payload:
                    uploaded_plays = [i["play_id"] for i in s.get("items", [])]
                    if uploaded_plays != self.payload[name]:
                        raise Exception(f"Ověření selhalo! Sekce '{name}' na serveru neodpovídá odeslaným datům.")
                    if s.get("id") not in self.state["completed_sections"]:
                        raise Exception(f"Kritická chyba: Sekce '{s.get('name')}' nebyla aktualizována.")
            
            self.success.emit(f"Úspěšně aktualizováno.")
            
        except Exception as e:
            self.error.emit(str(e), self.state)