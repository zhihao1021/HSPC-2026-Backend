# hspc2026

## Configuration
### Environment Variables
Use `.env` file to set environment variables. See `.env.example` for reference.

| Variable Name | Description | Default Value |
| --- | --- | --- |
| `POSTGRES_DB_URL` | Postgres database URL in the format `postgresql://user:password@host:port/database` | `postgresql://user:password@localhost:5432/database` |
| `POSTGRES_POOL_MIN_SIZE` | Minimum number of connections in the Postgres connection pool | `5` |
| `POSTGRES_POOL_MAX_SIZE` | Maximum number of connections in the Postgres connection pool | `20` |
| `JWT_PRIVATE_KEY` | Private key for signing JWT tokens | None |
| `JWT_PUBLIC_KEY` | Public key for verifying JWT tokens | None |

### Generate ECDSA Keys
To generate ECDSA keys for JWT signing and verification, you can use the following commands in your terminal:

```bash
# Generate a private key
openssl ecparam -genkey -name prime256v1 -noout -out jwt_private.pem
# Extract the public key from the private key
openssl ec -in jwt_private.pem -pubout -out jwt_public.pem
```