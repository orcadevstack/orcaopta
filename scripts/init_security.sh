#!/bin/bash

echo "Initializing Orcaopta Security Framework..."

# Base folder
mkdir -p security

# SSH structure
mkdir -p security/ssh/public
mkdir -p security/ssh/private

# GPG structure
mkdir -p security/gpg/public
mkdir -p security/gpg/private

# Trust policy structure
mkdir -p security/trust

# Trust files
touch security/trust/maintainers.txt
touch security/trust/allowed_signers
touch security/trust/allowed_gpg_keys

# Git signing config
mkdir -p .security
cat << 'EOF' > .security/gitconfig
[user]
    signingkey = security/gpg/public/orcaopta.asc

[gpg]
    program = gpg

[commit]
    gpgsign = true

[tag]
    gpgsign = true
EOF

# Add private keys to .gitignore
echo "security/ssh/private/*" >> .gitignore
echo "security/gpg/private/*" >> .gitignore

echo "Orcaopta Security Framework created."
