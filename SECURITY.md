# Security Policy

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

If you discover a security vulnerability, please report it privately by emailing **vero@eudaimoniatech.io** with the following information:

- **Vulnerability Type**: (e.g., XSS, SQL injection, authentication bypass)
- **Affected Component**: Which part of IntellyWeave is affected?
- **Severity**: How severe is the vulnerability?
- **Description**: Clear description of the vulnerability
- **Steps to Reproduce**: How can the vulnerability be reproduced?
- **Impact**: What could an attacker do with this vulnerability?
- **Proposed Fix** (optional): Do you have a suggested fix?

### Response Timeline

1. **Within 48 hours**: Acknowledgment of your report
2. **Within 7 days**: Initial assessment and validation
3. **Within 30 days**: Development and testing of fix
4. **Within 45 days**: Release of patched version

We request a **90-day responsible disclosure window** before public announcement to allow users time to upgrade.

## Supported Versions

| Version | Security Updates |
|---------|-----------------|
| Latest | Yes |
| Previous | Critical fixes only |
| Older | No |

We recommend using the latest version to receive all security patches.

## Security Best Practices

### For Users

1. **Keep Updated**: Regularly update to the latest version
2. **API Key Management**:
   - Store API keys in environment variables, never hardcode
   - Rotate keys regularly
   - Use separate keys for dev/staging/production
3. **Network Security**:
   - Deploy behind HTTPS/TLS
   - Use firewalls for sensitive environments
   - Restrict API access by IP when possible
4. **Data Protection**:
   - Encrypt sensitive documents at rest
   - Use TLS 1.2+ for all connections

### For Contributors

1. **Dependency Management**:
   - Run `pnpm audit` and `pip audit` to check for vulnerabilities
   - Keep dependencies updated
2. **Code Review**:
   - All changes require review before merge
   - Security-sensitive code gets extra scrutiny
3. **Input Validation**:
   - Validate all user input
   - Sanitize data before storing or displaying

## Third-Party Dependencies

IntellyWeave relies on open-source projects with their own security practices:

**Backend**: FastAPI, Weaviate, LiteLLM, DSPy, GLiNER
**Frontend**: Next.js, Mapbox GL, vis-network, Radix UI

Dependencies are monitored via Renovate for known vulnerabilities.

## Deployment Security

### Local Development
- Use `.env` files for secrets (never commit to git)
- Use localhost only

### Production
- Deploy behind reverse proxy with HTTPS/TLS
- Enable authentication
- Encrypt data in transit and at rest
- Regular backups with tested recovery procedures

## Security Contact

**Email**: vero@eudaimoniatech.io

For non-security questions, use [GitHub Discussions](https://github.com/vericle/intellyweave/discussions).

---

**Last Updated**: December 2025
