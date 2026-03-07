# Threat Intelligence Reference: Common Attack Indicators

## Document ID: TI-REF-001
## Classification: INTERNAL | Last Updated: 2025-02-01

---

## Known Malicious IP Ranges

### TOR Exit Nodes (sample)
- 185.220.101.0/24 - Tor2web relay cluster
- 185.220.100.0/24 - Known TOR exit range
- 185.107.47.0/24 - TOR project relays

### Active C2 Infrastructure (Q1 2025)
- 194.165.16.101 - Cobalt Strike C2 (APT29 campaign)
- 91.219.236.0/24 - APT41 infrastructure
- 45.142.212.0/24 - Ransomware staging servers

---

## MITRE ATT&CK Quick Reference

### Initial Access
- T1078 - Valid Accounts: Attackers use stolen credentials
- T1190 - Exploit Public-Facing Application
- T1566 - Phishing (T1566.001 Spearphishing Attachment)

### Execution  
- T1059.001 - PowerShell
- T1059.003 - Windows Command Shell
- T1204 - User Execution

### Persistence
- T1547.001 - Boot/Logon Autostart: Registry Run Keys
- T1136 - Create Account
- T1078 - Valid Accounts (persistence use)

### Privilege Escalation
- T1055 - Process Injection (T1055.012 - Process Hollowing)
- T1548 - Abuse Elevation Control Mechanism

### Defense Evasion
- T1055 - Process Injection
- T1036 - Masquerading
- T1027 - Obfuscated Files or Information

### Credential Access
- T1110.004 - Brute Force: Credential Stuffing
- T1555 - Credentials from Password Stores
- T1003 - OS Credential Dumping

### Lateral Movement
- T1021.001 - Remote Services: Remote Desktop Protocol
- T1021.002 - Remote Services: SMB/Windows Admin Shares

### Exfiltration
- T1041 - Exfiltration Over C2 Channel
- T1567 - Exfiltration Over Web Service

### Impact
- T1486 - Data Encrypted for Impact (Ransomware)
- T1529 - System Shutdown/Reboot

---

## IOC Pattern Library

### Process Injection Indicators
```
Suspicious: svchost.exe spawning explorer.exe
Suspicious: explorer.exe with network connections to non-Microsoft IPs
Suspicious: PowerShell with -EncodedCommand flag + high entropy base64
Alert: LSASS memory access from non-system process
```

### Credential Attack Patterns
```
Credential Stuffing: High volume of Sign-in failures from single IP
Password Spray: Low-volume failures across many accounts
Kerberoasting: ServiceTicket requests for multiple SPNs in short time
```

### Cloud-Specific IOCs (Azure)
```
Key Vault bulk access: >20 secret reads in <10 minutes
Suspicious service principal: new SPN with Owner role in Azure AD
Risky sign-ins: Azure AD Identity Protection P2 risk score >60
```

---

## Known Threat Actor TTPs

### APT29 (Cozy Bear)
- Commonly uses: Cobalt Strike, SUNBURST-style supply chain
- Target sectors: Government, Defense, Think tanks
- Initial access preference: Spearphishing, supply chain compromise
- Common C2: HTTPS + domain fronting via CDN

### Lazarus Group (DPRK)
- Commonly uses: Custom RATs, PowerShell Empire
- Target sectors: Finance, Cryptocurrency
- Initial access preference: Social engineering via LinkedIn/Slack
- Common C2: Custom HTTP/S protocols

### REvil/Sodinokibi (Ransomware)
- Common entry: Kaseya-style MSP compromise, exposed RDP
- Lateral movement: BloodHound AD enum + DCSync
- Exfil before encrypt: 48-72h average dwell time before ransom
