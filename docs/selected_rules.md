# CIS Benchmark Selected Rules (Level 1 Subset)

This document defines the subset of CIS Benchmark rules implemented in **baseline-monitor**  
for both **Ubuntu 20.04 LTS** and **Windows 10/11** operating systems.

Each rule includes:
- **ID** — unique rule identifier used by agent/backend.
- **Title** — short description.
- **Objective** — what this rule secures.
- **Audit Command** — command executed by the agent to check compliance.
- **Remediation** — how to fix if non-compliant.

---

## Ubuntu 20.04 LTS — Level 1 Subset

| ID | Rule | Objective | Audit Command | Remediation |
|----|------|------------|----------------|--------------|
| **UBU-01** | Disable root SSH login | Prevent direct root login via SSH | `grep "^PermitRootLogin" /etc/ssh/sshd_config` | Set `PermitRootLogin no` and run `sudo systemctl restart sshd` |
| **UBU-02** | Ensure UFW is enabled | Enable host-based firewall | `sudo ufw status` | Run `sudo ufw enable` |
| **UBU-03** | Ensure auditd service is enabled | Enable security auditing | `systemctl is-enabled auditd` | `sudo apt install auditd -y && sudo systemctl enable --now auditd` |
| **UBU-04** | Ensure automatic updates are enabled | Keep security patches up-to-date | `systemctl is-enabled unattended-upgrades` | `sudo apt install unattended-upgrades -y` |
| **UBU-05** | Set password minimum length ≥ 14 | Enforce strong passwords | `grep PASS_MIN_LEN /etc/login.defs` | Set `PASS_MIN_LEN 14` in `/etc/login.defs` |
| **UBU-06** | Set password maximum age ≤ 90 days | Enforce periodic password change | `grep PASS_MAX_DAYS /etc/login.defs` | Set `PASS_MAX_DAYS 90` in `/etc/login.defs` |
| **UBU-07** | Ensure /tmp has noexec option | Prevent execution of binaries in /tmp | `findmnt /tmp` | Add `noexec` option in `/etc/fstab` and remount |
| **UBU-08** | Ensure AppArmor is enabled | Enable process-level protection | `aa-status` | `sudo systemctl enable --now apparmor` |
| **UBU-09** | Ensure rsyslog service is enabled | Enable system logging | `systemctl is-enabled rsyslog` | `sudo apt install rsyslog -y && sudo systemctl enable --now rsyslog` |
| **UBU-10** | Disable IPv6 (if unused) | Reduce network attack surface | `sysctl net.ipv6.conf.all.disable_ipv6` | `sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1` |

---

## Windows 10 / 11 — Level 1 Subset

| ID | Rule | Objective | Audit Command (PowerShell) | Remediation |
|----|------|------------|-----------------------------|--------------|
| **WIN-01** | Disable SMBv1 protocol | Disable legacy SMBv1 vulnerable protocol | `Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol` | `Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol` |
| **WIN-02** | Ensure Windows Defender Antivirus is enabled | Enable real-time protection | `Get-MpComputerStatus | Select-Object AMServiceEnabled,AntispywareEnabled` | `Set-MpPreference -DisableRealtimeMonitoring $false` |
| **WIN-03** | Ensure Firewall is enabled for all profiles | Protect system from unauthorized access | `Get-NetFirewallProfile | Select Name,Enabled` | `Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True` |
| **WIN-04** | Set Account lockout threshold ≤ 5 | Prevent brute-force login attempts | `Get-AccountLockoutPolicy` | `net accounts /lockoutthreshold:5` |
| **WIN-05** | Set password minimum length ≥ 14 | Enforce strong password policy | `net accounts` | `net accounts /minpwlen:14` |
| **WIN-06** | Set password maximum age ≤ 90 days | Require password change regularly | `net accounts` | `net accounts /maxpwage:90` |
| **WIN-07** | Enable User Account Control (UAC) | Restrict silent privilege escalation | `Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Policies\System\EnableLUA` | `Set-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Policies\System -Name EnableLUA -Value 1` |
| **WIN-08** | Enable Audit Logon Events | Record logon/logoff attempts | `auditpol /get /category:* | findstr "Logon"` | `auditpol /set /category:"Logon/Logoff" /success:enable /failure:enable` |
| **WIN-09** | Disable Remote Desktop (if unused) | Reduce remote access attack surface | `Get-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name fDenyTSConnections` | `Set-ItemProperty -Path "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name fDenyTSConnections -Value 1` |
| **WIN-10** | Ensure Automatic Updates are enabled | Keep Windows up-to-date | `Get-Service -Name wuauserv` | `Set-Service -Name wuauserv -StartupType Automatic; Start-Service -Name wuauserv` |

---

## Notes

- The **Audit Command** column defines what each agent will execute locally to verify compliance.  
- The **Remediation** column shows how an administrator can manually fix the issue.  
- All rules are **CIS Level 1** — safe and minimal-impact hardening.  
- This file serves as the **source of truth** for the baseline-monitor project.

---

**Document version:** 1.0  
**Last updated:** October 2025  
**Maintainer:** Nguyen Xuan Bach
