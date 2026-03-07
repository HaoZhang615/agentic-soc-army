# Incident Response Playbook: Credential-Based Attack

## Playbook ID: IR-CRED-001
## Version: 2.1 | Last Updated: 2025-01-15
## Author: SOC Team | Classification: INTERNAL

---

## 1. Trigger Conditions

Activate this playbook when ANY of the following are detected:
- Credential stuffing: >10 failed logins within 5 minutes from the same IP
- Password spray: >5 failed logins across >10 accounts within 10 minutes  
- MFA fatigue / push bombing: >5 MFA prompts to a single user within 30 minutes
- Successful login from known-bad IP (TOR, botnet, threat-intel flagged)

---

## 2. Immediate Containment (T+0 to T+15 min)

### 2.1 User Account Actions
1. Revoke all active sessions for affected user (Azure AD > User > Revoke sessions)
2. Force MFA re-registration
3. If account belongs to a privileged role: disable account immediately pending review

### 2.2 Network Actions
1. Block source IP at perimeter firewall + NSG
2. Query SIEM for other users authenticating from same IP (lateral spread check)
3. Check if IP is TOR/VPN using threat intel feed

### 2.3 Evidence Preservation
1. Export sign-in logs for past 48 hours for affected user
2. Capture all associated IP addresses and User-Agent strings
3. Create incident ticket with priority mapping:
   - Privileged account → P1
   - Standard user, no MFA bypass → P2
   - Standard user, MFA bypassed → P1

---

## 3. Investigation (T+15 to T+60 min)

### 3.1 Scope Assessment
**Query Azure Sentinel (KQL):**
```kql
SigninLogs
| where TimeGenerated > ago(48h)
| where UserPrincipalName == "<affected_user>"
| project TimeGenerated, IPAddress, Location, ResultType, ResultDescription, UserAgent, ConditionalAccessStatus
| order by TimeGenerated desc
```

### 3.2 Lateral Movement Check
```kql
SigninLogs
| where TimeGenerated > ago(48h)  
| where IPAddress in ("suspect_ips")
| summarize UniqueUsers = dcount(UserPrincipalName), AuthAttempts = count() by IPAddress
```

### 3.3 Post-Auth Actions Review
If login was successful, check:
- Azure AD audit logs for role/permission changes
- Key Vault access logs
- SharePoint/OneDrive download volume
- Email forwarding rules created

---

## 4. MITRE ATT&CK Mapping

| Technique | ID | Description |
|-----------|-----|-------------|
| Valid Accounts | T1078 | Attacker uses compromised credentials |
| Brute Force: Credential Stuffing | T1110.004 | Automated testing of leaked credentials |
| Multi-Factor Authentication Interception | T1111 | MFA fatigue or real-time phishing |
| Initial Access via Valid Accounts | T1078 | Successful auth = initial access |

---

## 5. Eradication & Recovery

1. Reset all passwords for affected accounts
2. Review and remove any persistence mechanisms (email rules, OAuth grants)
3. Rotate secrets/certificates for affected service principals
4. Re-enable account with conditional access policy enforcing trusted location
5. Brief affected user on phishing/social engineering indicators

---

## 6. Lessons Learned Checklist

- [ ] Was MFA enforced and did it fail?
- [ ] Was the IP on any threat intel blocklist pre-alert?
- [ ] Time from first indicator to detection?
- [ ] Time from detection to containment?
- [ ] Were there any missed detection opportunities?

---

## Related Playbooks
- IR-PERSIST-001: Persistence Mechanism Discovery
- IR-EXFIL-002: Data Exfiltration Response  
- IR-PRIV-003: Privileged Account Compromise
