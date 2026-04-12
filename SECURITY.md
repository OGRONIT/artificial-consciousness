# Security Policy

## Supported Scope
This project may process API keys and runtime telemetry. Treat local runtime data as sensitive.

## Reporting a Vulnerability
Please report vulnerabilities privately by opening a security advisory in GitHub or contacting the maintainer directly.

Include:
- Affected file/module
- Reproduction steps
- Impact assessment
- Suggested fix (if available)

## Secret Handling
- Never commit `.env` or plaintext API keys.
- Rotate keys immediately if exposure is suspected.
- Use `.env.example` for public setup examples only.

## Responsible Disclosure
Please allow time for triage and patching before public disclosure.
