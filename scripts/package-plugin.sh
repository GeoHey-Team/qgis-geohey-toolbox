#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

PLUGIN_DIR_NAME="geohey_toolbox"
DIST_DIR="$REPO_ROOT/dist"
BUILD_ROOT="$DIST_DIR/build"
STAGE_DIR="$BUILD_ROOT/$PLUGIN_DIR_NAME"
VERSION=$(awk -F= '/^version=/{print $2; exit}' "$REPO_ROOT/metadata.txt")
ZIP_NAME="$PLUGIN_DIR_NAME-$VERSION.zip"
ZIP_PATH="$DIST_DIR/$ZIP_NAME"

rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR/china_offset"

cp "$REPO_ROOT/__init__.py" "$STAGE_DIR/"
cp "$REPO_ROOT/geohey_toolbox.py" "$STAGE_DIR/"
cp "$REPO_ROOT/geohey_toolbox_provider.py" "$STAGE_DIR/"
cp "$REPO_ROOT/metadata.txt" "$STAGE_DIR/"
cp "$REPO_ROOT/icon.png" "$STAGE_DIR/"
cp "$REPO_ROOT/LICENSE" "$STAGE_DIR/"

cp "$REPO_ROOT/china_offset/__init__.py" "$STAGE_DIR/china_offset/"
cp "$REPO_ROOT/china_offset/coord_algorithm.py" "$STAGE_DIR/china_offset/"
cp "$REPO_ROOT/china_offset/transform.py" "$STAGE_DIR/china_offset/"

if [ -d "$REPO_ROOT/i18n" ]; then
    QM_COUNT=$(find "$REPO_ROOT/i18n" -maxdepth 1 -type f -name '*.qm' | wc -l | tr -d ' ')
    if [ "$QM_COUNT" -gt 0 ]; then
        mkdir -p "$STAGE_DIR/i18n"
        find "$REPO_ROOT/i18n" -maxdepth 1 -type f -name '*.qm' -exec cp {} "$STAGE_DIR/i18n/" \;
    fi
fi

mkdir -p "$DIST_DIR"
rm -f "$ZIP_PATH"

(
    cd "$BUILD_ROOT"
    zip -rq "$ZIP_PATH" "$PLUGIN_DIR_NAME"
)

echo "Created $ZIP_PATH"
