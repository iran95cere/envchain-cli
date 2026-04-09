# envchain-cli

A CLI tool for managing and encrypting per-project environment variable sets with profile switching support.

## Features

- 🔐 Encrypted storage of environment variables
- 📁 Per-project configuration management
- 🔄 Profile switching for different environments (dev, staging, prod)
- 🚀 Simple CLI interface
- 🔑 Secure key derivation using industry-standard encryption

## Installation

```bash
pip install envchain-cli
```

Or install from source:

```bash
git clone https://github.com/yourusername/envchain-cli.git
cd envchain-cli
pip install -e .
```

## Usage

```bash
# Initialize a new envchain for your project
envchain init myproject

# Set environment variables for a profile
envchain set myproject --profile dev DATABASE_URL=postgresql://localhost/mydb
envchain set myproject --profile dev API_KEY=secret123

# List all variables in a profile
envchain list myproject --profile dev

# Remove a variable from a profile
envchain unset myproject --profile dev API_KEY

# Execute a command with the environment loaded
envchain exec myproject --profile dev -- python app.py

# Export variables to shell (eval required)
eval $(envchain export myproject --profile prod)

# Switch between profiles
envchain use myproject --profile staging

# Copy variables from one profile to another
envchain copy myproject --from dev --to staging
```

## Configuration

Environment chains are stored encrypted in `~/.envchain/` by default. You can customize the storage location with the `ENVCHAIN_DIR` environment variable.

## Security

All environment variables are encrypted at rest using AES-256-GCM. Master passwords are derived using PBKDF2 with a high iteration count.

## License

MIT License - see [LICENSE](LICENSE) file for details.
