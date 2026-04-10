# TUDOaqui Flutter App - Guia de Build

## Arquitectura

```
lib/
  main.dart                    # Entry point + Role-based routing
  config/
    api_config.dart           # Todos os endpoints da API
    theme.dart                # Tema dark (cores TUDOaqui)
  models/
    user.dart                 # UserModel (roles, labels)
    partner.dart              # PartnerModel + PaymentModel
  services/
    api_service.dart          # HTTP client com auth token
    auth_service.dart         # Login OTP, auto-login, state
  modules/
    auth/
      login_screen.dart       # Login OTP (+244)
    cliente/
      home_screen.dart        # Dashboard cliente (8 modulos, explorar, pagamentos, perfil)
    motorista/
      motorista_home.dart     # Dashboard motorista (online/offline, corridas, ganhos, perfil)
    motoqueiro/
      motoqueiro_home.dart    # Dashboard motoqueiro (entregas, ganhos)
    proprietario/
      proprietario_home.dart  # Dashboard proprietario (pedidos, produtos, receita)
    guia/
      guia_home.dart          # Dashboard guia turista (experiencias, reservas)
    common/
      agente_home.dart        # Dashboard agentes (imobiliario + viagem, reutilizavel)
  widgets/
    common.dart               # StatusBadge, TCard, StatCard, PrimaryButton, EmptyState, formatPrice
```

## Routing por Role

O `main.dart` direcciona automaticamente para o dashboard correcto:

| Role               | Ecra Home            | Tabs                                     |
|--------------------|----------------------|------------------------------------------|
| cliente            | ClienteHome          | Inicio, Explorar, Pagamentos, Perfil     |
| motorista          | MotoristaHome        | Inicio, Corridas, Ganhos, Perfil         |
| motoqueiro         | MotoqueiroHome       | Inicio, Entregas, Ganhos, Perfil         |
| proprietario/staff | ProprietarioHome     | Dashboard, Pedidos, Produtos, Perfil     |
| guia_turista       | GuiaHome             | Inicio, Experiencias, Reservas, Perfil   |
| agente_imobiliario | AgenteHome(imob)     | Inicio, Imoveis, Clientes, Perfil       |
| agente_viagem      | AgenteHome(viagem)   | Inicio, Pacotes, Clientes, Perfil       |
| admin              | ClienteHome          | Dashboard completo                       |

## Pre-Requisitos

1. Flutter SDK 3.2+ (https://flutter.dev/docs/get-started/install)
2. Android Studio ou VS Code com extensao Flutter
3. Dispositivo Android/iOS ou emulador

## Setup

```bash
cd mobile/flutter/tudoaqui

# Instalar dependencias
flutter pub get

# Verificar setup
flutter doctor

# Executar em modo debug
flutter run

# Build APK release
flutter build apk --release

# Build AAB para Play Store
flutter build appbundle --release

# Build iOS (requer Mac)
flutter build ios --release
```

## Configuracao API

Editar `lib/config/api_config.dart`:
```dart
static const String baseUrl = 'https://api.tudoaqui.ao/api/v1';
```

Para desenvolvimento local:
```dart
static const String baseUrl = 'http://10.0.2.2:8001/api/v1'; // Android emulator
```

## Tema

Cores configuradas em `lib/config/theme.dart`:
- Primary: #C62828 (Vermelho TUDOaqui)
- Accent: #FFD600 (Amarelo)
- Background: #0D0D0D (Preto)
- Surface: #1A1A1A

## Features Implementadas

### Login OTP
- Input telefone com prefixo +244
- Envio e verificacao de OTP
- Auto-login com token guardado
- Error handling

### Dashboards por Role
- **Cliente**: Grid de 8 modulos, search, promos, pagamentos
- **Motorista**: Toggle online/offline, stats corridas/ganhos, procura de corridas
- **Motoqueiro**: Toggle online/offline, stats entregas/ganhos
- **Proprietario**: Dashboard pedidos, produtos, receita, catalogo
- **Guia Turista**: Experiencias, reservas, receita
- **Agentes**: Imoveis/pacotes, clientes, receita (componente reutilizavel)

### Servicos
- ApiService com interceptor de auth, error handling, token refresh
- AuthService com state management (Provider)
- Secure storage para tokens

## Proximos Passos

1. Integrar cada modulo com endpoints reais do backend
2. Implementar mapas GPS para motorista/motoqueiro (Google Maps)
3. Real-time updates com WebSockets (corridas, entregas)
4. Push notifications (FCM)
5. Upload de fotos (camera + galeria)
6. Modo offline (SQLite local)
