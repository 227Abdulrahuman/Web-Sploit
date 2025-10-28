from ninja import Schema
from typing import List, Dict #

class VulnerabilitySchema(Schema):
    name: str
    path: str
    desc: str

class HostScanSchema(Schema):
    hostname: str
    ip: str | None = None
    ports: list[dict[str, str]] | list[str] = []
    cnames: list[str] = []
    ptr: str | None = None
    txt: str | None = None
    subs: list[str] = []
    live_subs: list[str] = []
    waf: str | None = None
    technology: str | None = None
    crawled_urls: list[str] = []
    archived_urls: list[str] = []
    virustotal_urls: list[str] = []
    all_urls: list[str] = []
    parameters: list[str] = []
    endpoints: list[dict[str, str]] = []
    js_files: list[str] = []
    js_secrets: list[str] = []
    js_urls: list[str] = []
    js_endpoints: list[str] = []
    vuln: VulnerabilitySchema | None = None

class ErrorSchema(Schema):
    message: str

