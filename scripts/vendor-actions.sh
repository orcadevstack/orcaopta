#!/bin/bash
set -e

echo "Vendoring GitHub Actions into .github/actions/ ..."

mkdir -p .github/actions

# List of actions to vendor
ACTIONS=(
  "actions/checkout@v4"
  "actions/setup-python@v5"
  "actions/upload-artifact@v4"
  "azure/setup-kubectl@v3"
  "azure/setup-helm@v3"
)

for ACTION in "${ACTIONS[@]}"; do
  NAME=$(echo "$ACTION" | cut -d'/' -f2 | cut -d'@' -f1)
  VERSION=$(echo "$ACTION" | cut -d'@' -f2)

  TARGET=".github/actions/$NAME"
  REPO="https://github.com/${ACTION%@*}.git"

  echo "Vendoring $ACTION → $TARGET"

  rm -rf "$TARGET"
  git clone --depth 1 --branch "$VERSION" "$REPO" "$TARGET"
  rm -rf "$TARGET/.git"
done

echo "All actions vendored successfully."
