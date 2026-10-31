# Supabase PostgreSQL trust root

`supabase-prod-ca-2021.crt` is the public Supabase Root 2021 CA downloaded from:
https://supabase-downloads.s3-ap-southeast-1.amazonaws.com/prod/ssl/prod-ca-2021.crt

File SHA-256: `700723581420dd1ac98fd7e9ac529f0ef210eadcaf87fc868a3ad7d114c2f3b7`.

The file contains a public CA certificate, never a password or private key.
Strict DB connections use this bundled root unless the URL supplies sslrootcert
or the operator sets PGSSLROOTCERT. Other providers need their appropriate trust
roots via one of these explicit settings. Development's default is unchanged.

Refresh from the provider's authenticated HTTPS distribution on a CA rotation;
review and repeat hostname/CA rejection tests before release. Never replace it
with an unverified leaf certificate or weaken sslmode on certificate failures.

Documentation: https://supabase.com/docs/guides/database/psql
