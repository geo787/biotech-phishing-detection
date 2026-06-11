"""SIEM / SOC webhook integration (simple, stdlib only).

Usage:
  export SIEM_WEBHOOK=https://siem.example/webhook
  from integrations.siem import send_alert
  send_alert({ 'event': 'phishing', ... })

If no webhook is configured, alerts are written to `alerts.log` as fallback.
"""
import json
import os
import urllib.request
import urllib.error
import time

WEBHOOK_URL = os.environ.get('SIEM_WEBHOOK')
FALLBACK_LOG = os.environ.get('SIEM_FALLBACK_LOG', 'alerts.log')


def _write_fallback(alert, error=None):
    entry = {
        'timestamp': int(time.time()),
        'alert': alert,
        'error': str(error) if error else None
    }
    try:
        with open(FALLBACK_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        # last resort: ignore
        pass


def send_alert(alert: dict) -> bool:
    """Send alert to configured SIEM webhook. Return True on success."""
    if not WEBHOOK_URL:
        _write_fallback(alert, error='no webhook configured')
        return False

    data = json.dumps(alert, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(WEBHOOK_URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            # Accept any 2xx as success
            if 200 <= resp.getcode() < 300:
                return True
            else:
                _write_fallback(alert, error=f'http {resp.getcode()}')
                return False
    except urllib.error.HTTPError as e:
        _write_fallback(alert, error=f'http {e.code}')
        return False
    except Exception as e:
        _write_fallback(alert, error=e)
        return False
