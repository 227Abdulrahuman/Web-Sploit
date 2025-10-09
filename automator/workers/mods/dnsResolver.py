import dns.resolver
import socket
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class CNAMERecord:
    target: str
    position: int  
    
    def __str__(self):
        return f"CNAME[{self.position}]: {self.target}"


@dataclass
class IPRecord:
    address: str
    version: int 
    
    def __str__(self):
        return f"IPv{self.version}: {self.address}"
    
    @property
    def is_ipv4(self) -> bool:
        return self.version == 4
    
    @property
    def is_ipv6(self) -> bool:
        return self.version == 6


@dataclass
class PTRRecord:
    ip_address: str
    hostname: str
    
    def __str__(self):
        return f"PTR: {self.ip_address} -> {self.hostname}"


@dataclass
class TXTRecord:
    value: str
    
    def __str__(self):
        return f"TXT: {self.value}"
    
    @property
    def is_spf(self) -> bool:
        return self.value.startswith('v=spf1')
    
    @property
    def is_dmarc(self) -> bool:
        return self.value.startswith('v=DMARC1')
    
    @property
    def is_dkim(self) -> bool:
        return self.value.startswith('v=DKIM1')


@dataclass
class DNSRecords:
    domain: str
    cname_chain: List[CNAMERecord] = field(default_factory=list)
    ip_records: List[IPRecord] = field(default_factory=list)
    ptr_records: List[PTRRecord] = field(default_factory=list)
    txt_records: List[TXTRecord] = field(default_factory=list)
    query_timestamp: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    
    @property
    def final_domain(self) -> str:
        if self.cname_chain:
            return self.cname_chain[-1].target
        return self.domain
    
    @property
    def has_cname(self) -> bool:
        return len(self.cname_chain) > 0
    
    @property
    def ipv4_addresses(self) -> List[str]:
        return [ip.address for ip in self.ip_records if ip.is_ipv4]
    
    @property
    def ipv6_addresses(self) -> List[str]:
        return [ip.address for ip in self.ip_records if ip.is_ipv6]
    
    @property
    def spf_records(self) -> List[TXTRecord]:
        return [txt for txt in self.txt_records if txt.is_spf]
    
    def to_dict(self) -> dict:
        return {
            'domain': self.domain,
            'final_domain': self.final_domain,
            'cname_chain': [cname.target for cname in self.cname_chain],
            'ip_addresses': [ip.address for ip in self.ip_records],
            'ipv4_addresses': self.ipv4_addresses,
            'ipv6_addresses': self.ipv6_addresses,
            'ptr_records': [{'ip': ptr.ip_address, 'hostname': ptr.hostname} for ptr in self.ptr_records],
            'txt_records': [txt.value for txt in self.txt_records],
            'query_timestamp': self.query_timestamp.isoformat(),
            'errors': self.errors
        }
    
    def __str__(self):
        lines = [f"DNS Records for: {self.domain}"]
        lines.append(f"Query Time: {self.query_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("-" * 50)
        
        if self.cname_chain:
            lines.append("CNAME Chain:")
            for cname in self.cname_chain:
                lines.append(f"  {cname}")
        
        if self.ip_records:
            lines.append("IP Addresses:")
            for ip in self.ip_records:
                lines.append(f"  {ip}")
        
        if self.ptr_records:
            lines.append("PTR Records:")
            for ptr in self.ptr_records:
                lines.append(f"  {ptr}")
        
        if self.txt_records:
            lines.append("TXT Records:")
            for txt in self.txt_records:
                lines.append(f"  {txt}")
        
        if self.errors:
            lines.append("Errors:")
            for error in self.errors:
                lines.append(f"  - {error}")
        
        return "\n".join(lines)


def get_domain_records(domain: str) -> DNSRecords:
    records = DNSRecords(domain=domain)
    
    current_domain = domain
    visited = set()
    position = 0
    
    while current_domain and current_domain not in visited:
        visited.add(current_domain)
        try:
            cname_answers = dns.resolver.resolve(current_domain, 'CNAME')
            for rdata in cname_answers:
                cname_target = str(rdata.target).rstrip('.')
                records.cname_chain.append(CNAMERecord(target=cname_target, position=position))
                current_domain = cname_target
                position += 1
            break
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            break
        except Exception as e:
            records.errors.append(f"CNAME resolution error for {current_domain}: {str(e)}")
            break
    
    final_domain = records.final_domain
    
    try:
        a_answers = dns.resolver.resolve(final_domain, 'A')
        for rdata in a_answers:
            records.ip_records.append(IPRecord(address=str(rdata), version=4))
    except Exception as e:
        records.errors.append(f"A record resolution error: {str(e)}")
    
    try:
        aaaa_answers = dns.resolver.resolve(final_domain, 'AAAA')
        for rdata in aaaa_answers:
            records.ip_records.append(IPRecord(address=str(rdata), version=6))
    except dns.resolver.NoAnswer:
        pass  
    except Exception as e:
        records.errors.append(f"AAAA record resolution error: {str(e)}")
    
    for ip_record in records.ip_records:
        try:
            ptr_answers = dns.resolver.resolve_address(ip_record.address)
            for rdata in ptr_answers:
                hostname = str(rdata).rstrip('.')
                records.ptr_records.append(PTRRecord(ip_address=ip_record.address, hostname=hostname))
        except Exception as e:
            records.errors.append(f"PTR resolution error for {ip_record.address}: {str(e)}")
    
    try:
        txt_answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in txt_answers:
            txt_value = ''.join([s.decode() if isinstance(s, bytes) else s for s in rdata.strings])
            records.txt_records.append(TXTRecord(value=txt_value))
    except dns.resolver.NoAnswer:
        pass  
    except Exception as e:
        records.errors.append(f"TXT record resolution error: {str(e)}")
    
    return records


if __name__ == "__main__":
    domain = "www.github.com"
    
    dns_records = get_domain_records(domain)
    
    print(dns_records)
    print("\n" + "="*50 + "\n")
    
    print(f"Final domain: {dns_records.final_domain}")
    print(f"Has CNAME: {dns_records.has_cname}")
    print(f"Number of IPv4 addresses: {len(dns_records.ipv4_addresses)}")
    print(f"Number of IPv6 addresses: {len(dns_records.ipv6_addresses)}")
    
    print("\n" + "="*50 + "\n")
    print("As dictionary:")
    import json
    print(json.dumps(dns_records.to_dict(), indent=2))