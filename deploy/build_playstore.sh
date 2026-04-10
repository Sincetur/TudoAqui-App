#!/bin/bash
# ============================================================
# TUDOaqui - Build APK/AAB para Google Play Store
# Requer: Flutter SDK instalado
# ============================================================

set -e

FLUTTER_DIR="/app/mobile/flutter/tudoaqui"
cd "$FLUTTER_DIR"

echo "========================================"
echo " TUDOaqui - Play Store Build"
echo "========================================"

# === 1. Verificar keystore ===
if [ ! -f android/key.properties ]; then
  echo ""
  echo "ERRO: android/key.properties nao encontrado!"
  echo ""
  echo "Criar ficheiro com:"
  echo "  storePassword=SUA_SENHA"
  echo "  keyPassword=SUA_SENHA"
  echo "  keyAlias=tudoaqui"
  echo "  storeFile=../../keystore/tudoaqui-release.jks"
  echo ""
  echo "Gerar keystore:"
  echo "  keytool -genkey -v -keystore keystore/tudoaqui-release.jks \\"
  echo "    -keyalg RSA -keysize 2048 -validity 10000 \\"
  echo "    -alias tudoaqui \\"
  echo "    -dname 'CN=TUDOaqui, OU=Nhimi Corporate, O=Nhimi Corporate, L=Luanda, C=AO'"
  exit 1
fi

# === 2. Limpar e obter dependencias ===
echo "[1/4] Limpando e obtendo dependencias..."
flutter clean
flutter pub get

# === 3. Build AAB (Google Play) ===
echo "[2/4] Building AAB para Play Store..."
flutter build appbundle --release

AAB_FILE="$FLUTTER_DIR/build/app/outputs/bundle/release/app-release.aab"
echo "  -> AAB: $(du -sh $AAB_FILE | cut -f1)"

# === 4. Build APK (distribuicao directa) ===
echo "[3/4] Building APK..."
flutter build apk --release --split-per-abi

echo "  -> APKs:"
ls -la build/app/outputs/flutter-apk/app-*-release.apk

# === 5. Resumo ===
echo ""
echo "[4/4] Build concluido!"
echo ""
echo "============================================"
echo " Ficheiros para Play Store:"
echo "============================================"
echo ""
echo " AAB (upload para Play Console):"
echo "   $AAB_FILE"
echo ""
echo " APK (distribuicao directa):"
echo "   build/app/outputs/flutter-apk/app-arm64-v8a-release.apk"
echo "   build/app/outputs/flutter-apk/app-armeabi-v7a-release.apk"
echo ""
echo " Metadata (listing):"
echo "   /app/deploy/playstore/"
echo ""
echo "============================================"
