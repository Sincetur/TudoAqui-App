# TUDOaqui - Guia Compilar APK e Publicar Play Store

## Visao Geral

A app Android TUDOaqui usa **TWA (Trusted Web Activity)** para envolver o site PWA
numa app nativa Android. O utilizador instala a app da Play Store e ela abre
o site `app.tudoaqui.ao` em modo fullscreen (sem barra do browser).

## Estrutura do Projecto

```
mobile/
  android/                    # Projecto Android Studio
    app/
      build.gradle            # Configuracao da app
      src/main/
        AndroidManifest.xml   # Manifest com TWA config
        res/
          mipmap-*/           # Icones em varias resolucoes
          drawable/           # Splash icon
          values/             # Cores, strings, estilos
    build.gradle              # Config Gradle raiz
    settings.gradle           # Settings
    gradle/wrapper/           # Gradle wrapper
  assets/
    playstore-icon.png        # Icone 512x512 para Play Store
    feature-graphic.png       # Banner 1024x500 para Play Store
  assetlinks.json             # Digital Asset Links (copiar para servidor)
  twa-manifest.json           # Config TWA (ref Bubblewrap)
  generate-keystore.sh        # Gerar keystore de assinatura
  build-apk.sh                # Script de build automatico
  PLAYSTORE-LISTING.md        # Ficha da Play Store pronta
```

## Pre-Requisitos

1. **Computador com:**
   - JDK 17+ (`java -version` para verificar)
   - Android Studio (recomendado) ou Android SDK (API 34)
   - Git

2. **Contas:**
   - Google Play Developer ($25 USD unica vez) em `sincesoft1@gmail.com`
   - Registar em: https://play.google.com/console

3. **Dominio online:**
   - `app.tudoaqui.ao` tem de estar acessivel com HTTPS
   - O site PWA tem de estar publicado

## Passo 1: Configurar Ambiente

### Opcao A: Android Studio (Recomendado)
1. Instalar Android Studio: https://developer.android.com/studio
2. Abrir o projecto: `File > Open > mobile/android/`
3. Esperar o Gradle sync completar

### Opcao B: Linha de Comando
```bash
# Instalar JDK 17
sudo apt install openjdk-17-jdk

# Instalar Android SDK
# Download: https://developer.android.com/studio#command-tools
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin
sdkmanager "platforms;android-34" "build-tools;34.0.0"
```

## Passo 2: Gerar Keystore

```bash
cd mobile
./generate-keystore.sh
```

Dados solicitados:
- **Password**: Escolha uma senha forte (guardar!)
- **Nome**: TUDOaqui Lda
- **Organizacao**: TUDOaqui
- **Cidade**: Luanda
- **Pais**: AO

Anote o **SHA-256 fingerprint** que aparece no final.

## Passo 3: Configurar Digital Asset Links

1. Copie o ficheiro `assetlinks.json` para o servidor web:
   ```
   https://app.tudoaqui.ao/.well-known/assetlinks.json
   ```

2. Substitua `SUBSTITUIR_PELO_SEU_SHA256_FINGERPRINT` pelo SHA-256 do passo 2:
   ```json
   [{
     "relation": ["delegate_permission/common.handle_all_urls"],
     "target": {
       "namespace": "android_app",
       "package_name": "ao.tudoaqui.app",
       "sha256_cert_fingerprints": ["AB:CD:12:34:..."]
     }
   }]
   ```

3. Verificar: `curl https://app.tudoaqui.ao/.well-known/assetlinks.json`

Isto remove a barra do browser e faz a app parecer 100% nativa.

## Passo 4: Activar Assinatura no build.gradle

Editar `android/app/build.gradle` e descomentar as linhas de signing:

```gradle
signingConfigs {
    release {
        storeFile file('keystore/tudoaqui-release.keystore')
        storePassword 'SUA_SENHA'
        keyAlias 'tudoaqui'
        keyPassword 'SUA_SENHA'
    }
}

buildTypes {
    release {
        signingConfig signingConfigs.release
        ...
    }
}
```

## Passo 5: Build

```bash
cd mobile
./build-apk.sh
```

Ou via Android Studio: `Build > Generate Signed Bundle / APK`

Ficheiros gerados:
- `app-debug.apk` - Para testar no dispositivo
- `app-release.apk` - APK assinado
- `app-release.aab` - AAB para Play Store (formato obrigatorio)

## Passo 6: Testar no Dispositivo

```bash
# Via USB
adb install android/app/build/outputs/apk/debug/app-debug.apk

# Ou transferir o APK e instalar manualmente
```

Verificar:
- App abre em modo fullscreen (sem barra URL)
- Login OTP funciona
- Navegacao entre paginas fluida
- Splash screen vermelho/preto aparece

## Passo 7: Publicar na Play Store

### 7.1 Criar a App na Console

1. Ir a https://play.google.com/console
2. Login com `sincesoft1@gmail.com`
3. `Criar app` > Preencher dados basicos

### 7.2 Upload do AAB

1. Ir a `Producao > Criar nova versao`
2. Upload do `app-release.aab`
3. Preencher notas da versao

### 7.3 Ficha da Loja

Usar o conteudo do ficheiro `PLAYSTORE-LISTING.md`:
- Titulo: TUDOaqui - SuperApp Angola
- Descricao curta e longa
- Screenshots (tirar do browser em modo mobile)
- Icone: `assets/playstore-icon.png`
- Feature graphic: `assets/feature-graphic.png`

### 7.4 Classificacao de Conteudo

- Preencher questionario IARC
- Categoria: Compras (ou Estilo de Vida)
- Publico-alvo: 16+

### 7.5 Submeter para Revisao

- A Google revisa em 1-7 dias uteis
- Primeira submissao pode demorar mais

## Passo 8: Publicar no iOS (Futuro)

Para iOS, e necessario:
1. Conta Apple Developer ($99/ano)
2. Mac com Xcode
3. Usar PWA Builder (https://www.pwabuilder.com/) para gerar projecto iOS
4. Ou usar Capacitor/Ionic para wrapper

## Actualizacoes Futuras

A vantagem do TWA: actualizar a app e simplesmente actualizar o site!
Nao precisa publicar nova versao na Play Store para mudancas de conteudo.

So precisa nova versao na Play Store quando mudar:
- Icone da app
- Permissoes
- Package name
- Versao minima do Android
