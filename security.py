import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path

class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte))
    ]

crypt32 = ctypes.windll.crypt32

crypt32.CryptProtectData.argtypes = [
    ctypes.POINTER(DATA_BLOB),
    wintypes.LPCWSTR,
    ctypes.POINTER(DATA_BLOB),
    ctypes.c_void_p,
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(DATA_BLOB)
]
crypt32.CryptProtectData.restype = wintypes.BOOL

def encrypt_data(data_dict: dict) -> bytes:
    json_bytes = json.dumps(data_dict).encode('utf-8') # adresa a token v dict převedeny na JSON a následně na surové bajty
    input_blob = DATA_BLOB()
    input_blob.cbData = len(json_bytes)
    input_blob.pbData = ctypes.cast(ctypes.c_char_p(json_bytes), ctypes.POINTER(ctypes.c_byte))
    out_blob = DATA_BLOB()
    success = crypt32.CryptProtectData(ctypes.byref(input_blob), None, None, None, None, 1, ctypes.byref(out_blob)) # samotné šifrování, flag 1 = šifruj potichu bez oken
    
    if success:
        encrypted_bytes = ctypes.string_at(out_blob.pbData, out_blob.cbData) # vytáhnutí zašifrovaných dat z paměti
        ctypes.windll.kernel32.LocalFree(out_blob.pbData) # uvolnění paměti alokované pro výstupní blob
        return encrypted_bytes
    else:
        raise Exception("Šifrování dat selhalo.")


crypt32.CryptUnprotectData.argtypes = [
    ctypes.POINTER(DATA_BLOB),
    ctypes.POINTER(wintypes.LPWSTR),
    ctypes.POINTER(DATA_BLOB),
    ctypes.c_void_p,
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(DATA_BLOB)
]
crypt32.CryptUnprotectData.restype = wintypes.BOOL

def decrypt_data(encrypted_bytes: bytes) -> dict:
    input_blob = DATA_BLOB()
    input_blob.cbData = len(encrypted_bytes)
    input_blob.pbData = ctypes.cast(ctypes.c_char_p(encrypted_bytes), ctypes.POINTER(ctypes.c_byte))
    out_blob = DATA_BLOB()
    success = crypt32.CryptUnprotectData(ctypes.byref(input_blob), None, None, None, None, 1, ctypes.byref(out_blob))
    
    if success:
        decrypted_bytes = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        ctypes.windll.kernel32.LocalFree(out_blob.pbData)
        json_str = decrypted_bytes.decode('utf-8')
        return json.loads(json_str)
    else:
        raise Exception("Dešifrování selhalo.")

APP_DIR = Path(os.environ.get('LOCALAPPDATA', Path.home())) / "Filmana"
AUTH_FILE = APP_DIR / ".filmana_auth"

def save_credentials(api_url: str, token: str):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    data_dict = {"format_version": 1, "api_url": api_url, "token": token}
    temp_file = None
    
    try:
        encrypted_bytes = encrypt_data(data_dict)
        temp_file = AUTH_FILE.with_suffix(".tmp")
        with open(temp_file, "wb") as f:
            f.write(encrypted_bytes)
        temp_file.replace(AUTH_FILE)
    except Exception as e:
        if temp_file and temp_file.exists():
            temp_file.unlink()

def load_credentials() -> dict:
    if not AUTH_FILE.exists():
        return {}
        
    try:
        with open(AUTH_FILE, "rb") as f:
            encrypted_bytes = f.read()
        return decrypt_data(encrypted_bytes)
    except Exception as e:
        return {}