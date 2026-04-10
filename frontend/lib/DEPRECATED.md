# PROJECTO FLUTTER DESCONTINUADO

Esta pasta contém a **Fase 1.1** do Flutter (BLoC pattern, apenas módulo Taxi).

## Projecto activo

O projecto Flutter activo e completo está em:

```
mobile/flutter/tudoaqui/
```

Inclui:
- 7 dashboards por role (cliente, motorista, motoqueiro, proprietário, guia, agente imob., agente viagem)
- Google Maps com dark theme, tracking GPS em tempo real
- WebSocket service com reconexão automática
- Provider state management
- Android + iOS configurados

## Migração

Se precisas de funcionalidades desta pasta, encontra os equivalentes em:

| Aqui | Projecto activo |
|------|-----------------|
| `features/auth/` | `mobile/flutter/tudoaqui/lib/modules/auth/` |
| `features/ride/` | `mobile/flutter/tudoaqui/lib/modules/motorista/` |
| `core/api/api_client.dart` | `mobile/flutter/tudoaqui/lib/services/api_service.dart` |
| `core/api/websocket_service.dart` | `mobile/flutter/tudoaqui/lib/services/websocket_service.dart` |

Esta pasta será removida numa versão futura.
