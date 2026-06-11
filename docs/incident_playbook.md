# Incident Playbook — Phishing Detection (Medical Clients)

This playbook describes the operational steps to follow when the phishing detection system raises an alert.
It is tailored for healthcare organizations (Epic/Cerner/Medidata).

## Goals
- Contain threat quickly and reduce patient risk
- Preserve evidence for investigation and compliance
- Restore normal operations with minimal data exposure

## Roles
- SOC: security operations team (triage, containment)
- IT: mail gateway / network engineers (blocking, removal)
- Clinical leads: notify affected clinicians
- Privacy Officer / Compliance: oversee PHI handling

## Triage steps (first 15 minutes)
1. Confirm alert details: email id, sender, URL, affected software.
2. Quarantine the email copy in mail gateway and user's mailbox.
3. Block the URL/domain at the gateway and proxy (add to `blocklist.txt`).
4. Notify SOC and IT via existing incident channel; include alert metadata.

## Containment (15–60 minutes)
1. Check for credential usage: correlate with EHR access logs (see `integrations/ehr_logs.py` for ingestion).
2. If credentials likely compromised, force password reset for affected accounts and enable MFA.
3. Isolate affected machines (if click-through is suspected) and snapshot for forensics.

## Eradication & Recovery (1–24 hours)
1. Remove phishing emails from mailboxes (server-side remove) and confirm removal.
2. Patch systems, update gateway filters, and restore any modified configurations.
3. Re-enable access once verified; document user notifications and password resets.

## Notification & Reporting
- Notify affected clinicians with clear instructions (what to do, what not to do).
- Prepare a compliance report with redacted logs (use `utils/privacy.redact`) for retention.
- If PHI was exposed, engage Privacy Officer per HIPAA rules.

## Evidence preservation
- Preserve original email headers, raw message, and snapshots of affected endpoints.
- Store evidence in a write-once location with access controls.

## Post-incident
- Review detection performance and mark false positives/negatives.
- Add indicators (URLs, domains) to blocklist and SIEM rules.
- Run a tabletop exercise within 7 days and update playbook accordingly.

## Minimal SOP (for clinical staff)
- Do NOT open attachments or follow links in suspicious emails.
- If you clicked a link, immediately contact IT/SOC and provide the email timestamp.
- If requested to provide credentials, contact IT directly (do not reply to the email).

## Templates
- Incident notification message sample (to clinicians):

```
Subject: Security alert — potential phishing attempt (ACTION REQUIRED)

Dear Colleague,

We identified a suspicious email that may target our EHR systems. Please DO NOT open attachments or follow links in this email. If you clicked the link, please contact IT/SOC immediately at ext. 1234.

Thank you,
Security Operations
```

---

For the technical team: integrate `integrations/siem.py` and `integrations/email_gateway.py` with your SOC and mail gateway. Use `utils/privacy.redact` when producing compliance reports. If you want, I can convert this playbook into a printable PDF or confluence-ready page.
