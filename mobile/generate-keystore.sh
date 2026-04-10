#!/bin/bash
# =============================================
# TUDOaqui - Gerar Keystore de Assinatura
# =============================================
# Executar APENAS UMA VEZ. Guardar o keystore e senhas em local seguro!

set -e

KEYSTORE_DIR="keystore"
KEYSTORE_FILE="$KEYSTORE_DIR/tudoaqui-release.keystore"
ALIAS="tudoaqui"

mkdir -p "$KEYSTORE_DIR"

if [ -f "$KEYSTORE_FILE" ]; then
    echo "AVISO: Keystore ja existe em $KEYSTORE_FILE"
    echo "Se quer gerar um novo, apague o ficheiro primeiro."
    exit 1
fi

echo "=== Gerar Keystore de Assinatura ==="
echo "Preencha os dados solicitados (para a Play Store):"
echo ""

keytool -genkey -v \
    -keystore "$KEYSTORE_FILE" \
    -alias "$ALIAS" \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000

echo ""
echo "=== Keystore gerado com sucesso! ==="
echo "Ficheiro: $KEYSTORE_FILE"
echo ""
echo "=== SHA-256 Fingerprint (para assetlinks.json) ==="
keytool -list -v -keystore "$KEYSTORE_FILE" -alias "$ALIAS" 2>/dev/null | grep "SHA256:"
echo ""
echo "IMPORTANTE: Guarde o keystore e as senhas em local seguro!"
echo "Sem o keystore NAO consegue actualizar a app na Play Store."
