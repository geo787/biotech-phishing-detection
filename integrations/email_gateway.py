"""Simple email gateway integration helpers.
Functions to append URLs/domains to `blocklist.txt` and produce example commands
for common gateways.
"""
import os
from urllib.parse import urlparse

BLOCKLIST_FILE = os.environ.get('BLOCKLIST_FILE', 'blocklist.txt')


def _domain_from_url(url: str) -> str:
    try:
        p = urlparse(url)
        if p.netloc:
            return p.netloc
        return url
    except Exception:
        return url


def append_blocklist(url: str) -> None:
    """Append a URL's domain to blocklist file (idempotent append)."""
    domain = _domain_from_url(url)
    # Avoid duplicates in simple way
    existing = set()
    try:
        if os.path.exists(BLOCKLIST_FILE):
            with open(BLOCKLIST_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    existing.add(line.strip())
    except Exception:
        existing = set()

    if domain in existing:
        return
    try:
        with open(BLOCKLIST_FILE, 'a', encoding='utf-8') as f:
            f.write(domain + '\n')
    except Exception:
        pass


def example_commands_for_gateway(gateway: str, domain: str) -> str:
    """Return an example command to block `domain` for a given gateway.
    Supported gateways: 'postfix', 'office365', 'proofpoint'
    """
    gateway = gateway.lower()
    if gateway == 'postfix':
        return f"postmap /etc/postfix/access && echo '{domain} REJECT' >> /etc/postfix/access && postmap /etc/postfix/access && systemctl reload postfix"
    if gateway == 'office365':
        return f"Connect-ExchangeOnline; New-HostedOutboundConnector -Name 'Block {domain}' -ConnectorType OnPremises"
    if gateway == 'proofpoint':
        return f"(Use Proofpoint API) Block sender domain: {domain}"
    return f"# Add {domain} to your gateway blocklist"
