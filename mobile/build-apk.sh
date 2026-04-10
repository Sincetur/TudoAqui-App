#!/bin/bash
# =============================================
# TUDOaqui - Build APK e AAB
# =============================================
# Pre-requisitos:
# - JDK 17+ instalado
# - Android SDK (API 34) instalado
# - Keystore gerado (./generate-keystore.sh)

set -e

echo "=== TUDOaqui Android Build ==="

cd android

# Verificar gradlew
if [ ! -f "gradlew" ]; then
    echo "A gerar Gradle wrapper..."
    gradle wrapper --gradle-version=8.5
fi

chmod +x gradlew

echo ""
echo "=== Build Debug APK ==="
./gradlew assembleDebug
echo "APK Debug: android/app/build/outputs/apk/debug/app-debug.apk"

echo ""
echo "=== Build Release APK ==="
./gradlew assembleRelease
echo "APK Release: android/app/build/outputs/apk/release/app-release.apk"

echo ""
echo "=== Build AAB (para Play Store) ==="
./gradlew bundleRelease
echo "AAB: android/app/build/outputs/bundle/release/app-release.aab"

echo ""
echo "=== Build Completo! ==="
echo ""
echo "Ficheiros gerados:"
echo "  Debug APK:   android/app/build/outputs/apk/debug/app-debug.apk"
echo "  Release APK: android/app/build/outputs/apk/release/app-release.apk"
echo "  Release AAB: android/app/build/outputs/bundle/release/app-release.aab"
echo ""
echo "Para publicar na Play Store, use o ficheiro AAB (.aab)"
