# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.1.x-pro | Yes |
| < 2.1 | Limited |

## Reporting a Vulnerability

Please report security issues privately.

- Open a private security advisory on this repository if available, or
- Contact the owner via the profile listed on the main FathiMind repository.

Do not open public issues for security-sensitive findings.

## Scope

This is a pure analysis library (no network, no secrets handling, no external calls).  
The main risks are related to:

- Incorrect interpretation of confidence scores as absolute certainty
- Supply-chain attacks if the package is installed from an untrusted source

Always verify the source and review the fingerprint of critical decisions.
