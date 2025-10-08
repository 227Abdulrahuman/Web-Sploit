#!/usr/bin/env python3

import subprocess
import json
import sqlite3
import requests
import dns.resolver
import socket
import hashlib
import os
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from typing import Set, Tuple, List, Optional

class ReconDatabase:
    def __init__(self, db_path: str = "recon.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._init_tables()
    
    def _init_tables(self):
        """Initialize database tables"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dns_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT NOT NULL,
                record_type TEXT NOT NULL,
                record_value TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(hostname, record_type, record_value)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS open_ports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT NOT NULL,
                port INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(hostname, port)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subdomains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subdomain TEXT NOT NULL UNIQUE,
                base_domain TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS endpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parameter TEXT NOT NULL UNIQUE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS js_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def insert_dns_record(self, hostname: str, record_type: str, record_value: str):
        try:
            self.cursor.execute(
                'INSERT OR IGNORE INTO dns_records (hostname, record_type, record_value) VALUES (?, ?, ?)',
                (hostname, record_type, record_value)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
    
    def insert_open_port(self, hostname: str, port: int):
        try:
            self.cursor.execute(
                'INSERT OR IGNORE INTO open_ports (hostname, port) VALUES (?, ?)',
                (hostname, port)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
    
    def insert_subdomain(self, subdomain: str, base_domain: str):
        try:
            self.cursor.execute(
                'INSERT OR IGNORE INTO subdomains (subdomain, base_domain) VALUES (?, ?)',
                (subdomain, base_domain)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
    
    def insert_endpoint(self, endpoint: str):
        try:
            self.cursor.execute('INSERT OR IGNORE INTO endpoints (endpoint) VALUES (?)', (endpoint,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
    
    def insert_parameter(self, parameter: str):
        try:
            self.cursor.execute('INSERT OR IGNORE INTO parameters (parameter) VALUES (?)', (parameter,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
    
    def js_file_exists(self, url: str) -> bool:
        self.cursor.execute('SELECT COUNT(*) FROM js_files WHERE url = ?', (url,))
        return self.cursor.fetchone()[0] > 0
    
    def insert_js_file(self, url: str, file_path: str, file_hash: str):
        try:
            self.cursor.execute(
                'INSERT OR IGNORE INTO js_files (url, file_path, file_hash) VALUES (?, ?, ?)',
                (url, file_path, file_hash)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
    
    def close(self):
        self.conn.close()


class URLRecon:
    def __init__(self, url: str, base_domain: str, db: ReconDatabase, js_dir: str = "js_files"):
        self.url = url
        self.base_domain = base_domain
        self.db = db
        self.js_dir = js_dir
        self.parsed_url = urlparse(url)
        self.hostname = self.parsed_url.netloc
        
        # Create JS directory if it doesn't exist
        Path(self.js_dir).mkdir(exist_ok=True)
    
    def get_dns_records(self):
        """Get DNS records for hostname"""
        print(f"[*] Gathering DNS records for {self.hostname}")
        
        # Get A records (IP addresses)
        ips = []
        try:
            answers = dns.resolver.resolve(self.hostname, 'A')
            for rdata in answers:
                ip = str(rdata)
                ips.append(ip)
                self.db.insert_dns_record(self.hostname, 'A', ip)
                print(f"    [+] A: {ip}")
        except Exception as e:
            print(f"    [-] No A records found: {e}")
        
        # Get CNAME records
        cname_ips = []
        try:
            answers = dns.resolver.resolve(self.hostname, 'CNAME')
            for rdata in answers:
                cname = str(rdata).rstrip('.')
                self.db.insert_dns_record(self.hostname, 'CNAME', cname)
                print(f"    [+] CNAME: {cname}")
                
                # If no IP found, get IP of CNAME
                if not ips:
                    try:
                        cname_answers = dns.resolver.resolve(cname, 'A')
                        for cname_rdata in cname_answers:
                            cname_ip = str(cname_rdata)
                            cname_ips.append(cname_ip)
                            self.db.insert_dns_record(cname, 'A', cname_ip)
                            print(f"    [+] CNAME A: {cname_ip}")
                    except Exception as e:
                        print(f"    [-] Could not resolve CNAME IP: {e}")
        except Exception as e:
            print(f"    [-] No CNAME records found: {e}")
        
        # Use IPs from CNAME if no direct IPs found
        if not ips and cname_ips:
            ips = cname_ips
        
        # Get PTR records for IPs
        for ip in ips:
            try:
                ptr = socket.gethostbyaddr(ip)[0]
                self.db.insert_dns_record(self.hostname, 'PTR', ptr)
                print(f"    [+] PTR: {ptr}")
            except Exception as e:
                print(f"    [-] No PTR record for {ip}: {e}")
        
        # Get TXT records
        try:
            answers = dns.resolver.resolve(self.hostname, 'TXT')
            for rdata in answers:
                txt = str(rdata)
                self.db.insert_dns_record(self.hostname, 'TXT', txt)
                print(f"    [+] TXT: {txt}")
        except Exception as e:
            print(f"    [-] No TXT records found: {e}")
    
    def scan_ports(self):
        """Scan for open ports using naabu"""
        print(f"\n[*] Scanning ports for {self.hostname}")
        try:
            result = subprocess.run(
                ['naabu', '-Pn', '-silent', '-host', self.hostname],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            for line in result.stdout.strip().split('\n'):
                if line and ':' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        port = int(parts[1])
                        self.db.insert_open_port(self.hostname, port)
                        print(f"    [+] Open port: {port}")
        except subprocess.TimeoutExpired:
            print("    [-] Port scan timed out")
        except FileNotFoundError:
            print("    [-] naabu not found. Please install it.")
        except Exception as e:
            print(f"    [-] Port scan failed: {e}")
    
    def enumerate_wayback(self):
        """Enumerate URLs from Wayback Machine"""
        print(f"\n[*] Enumerating Wayback Machine for {self.hostname}")
        
        subdomains = set()
        endpoints = set()
        parameters = set()
        
        wayback_url = f"https://web.archive.org/cdx/search/cdx?url={self.hostname}/*&collapse=urlkey&fl=original"
        
        try:
            response = requests.get(wayback_url, timeout=30)
            if response.status_code == 200:
                urls = response.text.strip().split('\n')
                print(f"    [+] Found {len(urls)} URLs")
                
                for url in urls:
                    if not url:
                        continue
                    
                    try:
                        parsed = urlparse(url)
                        hostname = parsed.netloc
                        path = parsed.path
                        query = parsed.query
                        
                        # Only process if hostname contains base domain
                        if self.base_domain in hostname:
                            # Extract subdomain
                            subdomains.add(hostname)
                            self.db.insert_subdomain(hostname, self.base_domain)
                            
                            # Extract endpoint (only for matching domain)
                            if path:
                                endpoints.add(path)
                                self.db.insert_endpoint(path)
                            
                            # Extract parameters (only for matching domain)
                            if query:
                                params = parse_qs(query)
                                for param in params.keys():
                                    parameters.add(param)
                                    self.db.insert_parameter(param)
                    except Exception as e:
                        continue
                
                print(f"    [+] Subdomains: {len(subdomains)}")
                print(f"    [+] Endpoints: {len(endpoints)}")
                print(f"    [+] Parameters: {len(parameters)}")
            else:
                print(f"    [-] Wayback API returned status {response.status_code}")
        except Exception as e:
            print(f"    [-] Wayback enumeration failed: {e}")
    
    def crawl_with_katana(self):
        """Crawl URL with Katana"""
        print(f"\n[*] Crawling with Katana: {self.url}")
        
        subdomains = set()
        endpoints = set()
        parameters = set()
        js_files = []
        
        try:
            result = subprocess.run(
                ['katana', '-u', self.url, '-silent'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            urls = result.stdout.strip().split('\n')
            print(f"    [+] Found {len(urls)} URLs")
            
            for url in urls:
                if not url:
                    continue
                
                try:
                    parsed = urlparse(url)
                    hostname = parsed.netloc
                    path = parsed.path
                    query = parsed.query
                    
                    # Only process if hostname contains base domain
                    if self.base_domain in hostname:
                        # Extract subdomain
                        subdomains.add(hostname)
                        self.db.insert_subdomain(hostname, self.base_domain)
                        
                        # Extract endpoint (only for matching domain)
                        if path:
                            endpoints.add(path)
                            self.db.insert_endpoint(path)
                        
                        # Extract parameters (only for matching domain)
                        if query:
                            params = parse_qs(query)
                            for param in params.keys():
                                parameters.add(param)
                                self.db.insert_parameter(param)
                        
                        # Check if it's a JS file (only for matching domain)
                        if path.endswith('.js') or '.js?' in url:
                            js_files.append(url)
                except Exception as e:
                    continue
            
            print(f"    [+] Subdomains: {len(subdomains)}")
            print(f"    [+] Endpoints: {len(endpoints)}")
            print(f"    [+] Parameters: {len(parameters)}")
            print(f"    [+] JS files: {len(js_files)}")
            
            # Download JS files
            self.download_js_files(js_files)
            
        except subprocess.TimeoutExpired:
            print("    [-] Katana crawl timed out")
        except FileNotFoundError:
            print("    [-] katana not found. Please install it.")
        except Exception as e:
            print(f"    [-] Katana crawl failed: {e}")
    
    def download_js_files(self, js_urls: List[str]):
        """Download JS files"""
        print(f"\n[*] Downloading JS files")
        
        for js_url in js_urls:
            # Check if already downloaded
            if self.db.js_file_exists(js_url):
                print(f"    [~] Already downloaded: {js_url}")
                continue
            
            try:
                # Create filename from URL
                parsed = urlparse(js_url)
                filename = parsed.path.replace('/', '_')
                if not filename:
                    filename = hashlib.md5(js_url.encode()).hexdigest()
                if not filename.endswith('.js'):
                    filename += '.js'
                
                filepath = os.path.join(self.js_dir, filename)
                
                # Download file
                response = requests.get(js_url, timeout=30)
                if response.status_code == 200:
                    content = response.content
                    file_hash = hashlib.sha256(content).hexdigest()
                    
                    # Save file
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    
                    # Store in database
                    self.db.insert_js_file(js_url, filepath, file_hash)
                    print(f"    [+] Downloaded: {filename}")
                else:
                    print(f"    [-] Failed to download {js_url}: Status {response.status_code}")
            except Exception as e:
                print(f"    [-] Failed to download {js_url}: {e}")
    
    def run(self):
        """Run all reconnaissance tasks"""
        print(f"\n{'='*60}")
        print(f"Starting reconnaissance for: {self.url}")
        print(f"Base domain: {self.base_domain}")
        print(f"{'='*60}\n")
        
        self.get_dns_records()
        self.scan_ports()
        self.enumerate_wayback()
        self.crawl_with_katana()
        
        print(f"\n{'='*60}")
        print("Reconnaissance complete!")
        print(f"{'='*60}\n")


def main():
    import sys
    
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <URL> <BASE_DOMAIN>")
        print(f"Example: {sys.argv[0]} https://www.example.com example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    base_domain = sys.argv[2]
    
    # Initialize database
    db = ReconDatabase()
    
    try:
        # Run reconnaissance
        recon = URLRecon(url, base_domain, db)
        recon.run()
    finally:
        # Close database connection
        db.close()


if __name__ == "__main__":
    main()