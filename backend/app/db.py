"""
Acesso ao Supabase via REST API.
Suporta chaves novas (sb_secret_...) com header apikey e legadas (JWT) com Bearer.
"""
import os
from dotenv import load_dotenv

load_dotenv()

_SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
_SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
# Chaves sb_* devem usar só header apikey (não Bearer)
_USE_APIKEY_ONLY = _SUPABASE_KEY.startswith("sb_") if _SUPABASE_KEY else False


def _headers():
    h = {
        "apikey": _SUPABASE_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if not _USE_APIKEY_ONLY:
        h["Authorization"] = f"Bearer {_SUPABASE_KEY}"
    return h


def _rest(table: str):
    return f"{_SUPABASE_URL}/rest/v1/{table}"


class _Table:
    def __init__(self, name: str):
        self._name = name
        self._url = _rest(name)

    def select(self, columns: str = "*"):
        return _Query(self._name, self._url, select=columns)

    def insert(self, data: dict):
        return _Insert(self._name, self._url, data)

    def update(self, data: dict):
        return _Update(self._name, self._url, data)

    def delete(self):
        return _Delete(self._name, self._url)


class _Result:
    def __init__(self, data):
        self.data = data


class _Query:
    def __init__(self, table: str, base_url: str, select: str):
        self._url = base_url
        self._params: list[tuple[str, str]] = [("select", select)]
        self._single = False

    def order(self, col: str, asc: bool = True):
        self._params.append(("order", f"{col}.{'asc' if asc else 'desc'}"))
        return self

    def eq(self, col: str, val):
        if isinstance(val, bool):
            val = str(val).lower()
        self._params.append((col, f"eq.{val}"))
        return self

    def gte(self, col: str, val):
        self._params.append((col, f"gte.{val}"))
        return self

    def lte(self, col: str, val):
        self._params.append((col, f"lte.{val}"))
        return self

    def single(self):
        self._single = True
        return self

    def execute(self):
        import httpx
        qs = "&".join(f"{k}={v}" for k, v in self._params)
        r = httpx.get(f"{self._url}?{qs}", headers=_headers(), timeout=30)
        r.raise_for_status()
        data = r.json()
        if self._single:
            data = data[0] if isinstance(data, list) and len(data) else None
        return _Result(data)


class _Insert:
    def __init__(self, table: str, base_url: str, data: dict):
        self._url = base_url
        self._data = data

    def select(self):
        return self

    def single(self):
        return self

    def execute(self):
        import httpx
        h = {**_headers(), "Prefer": "return=representation"}
        r = httpx.post(self._url, json=self._data, headers=h, timeout=30)
        r.raise_for_status()
        data = r.json()
        out = data[0] if isinstance(data, list) and data else data
        return _Result(out)


class _Update:
    def __init__(self, table: str, base_url: str, data: dict):
        self._url = base_url
        self._data = data
        self._filter_col = self._filter_val = None

    def eq(self, col: str, val):
        self._filter_col, self._filter_val = col, val
        return self

    def select(self):
        return self

    def single(self):
        return self

    def execute(self):
        import httpx
        if not self._filter_col:
            raise ValueError("update precisa de .eq(col, val)")
        qs = f"{self._filter_col}=eq.{self._filter_val}"
        h = {**_headers(), "Prefer": "return=representation"}
        r = httpx.patch(f"{self._url}?{qs}", json=self._data, headers=h, timeout=30)
        r.raise_for_status()
        data = r.json()
        out = data[0] if isinstance(data, list) and data else None
        return _Result(out)


class _Delete:
    def __init__(self, table: str, base_url: str):
        self._url = base_url
        self._filter_col = self._filter_val = None

    def eq(self, col: str, val):
        self._filter_col, self._filter_val = col, val
        return self

    def execute(self):
        import httpx
        if not self._filter_col:
            raise ValueError("delete precisa de .eq(col, val)")
        qs = f"{self._filter_col}=eq.{self._filter_val}"
        r = httpx.delete(f"{self._url}?{qs}", headers=_headers(), timeout=30)
        r.raise_for_status()
        return _Result(None)


class _Client:
    def table(self, name: str):
        return _Table(name)


def get_supabase():
    if not _SUPABASE_URL or not _SUPABASE_KEY:
        raise ValueError("Defina SUPABASE_URL e SUPABASE_KEY no .env")
    return _Client()
