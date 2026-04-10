import UIKit
import Flutter
import GoogleMaps

@UIApplicationMain
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    // Configurar Google Maps API Key via Info.plist
    // Adicionar GOOGLE_MAPS_API_KEY ao Info.plist ou via variavel de ambiente de build
    // Ver mobile/README-BUILD.md para instrucoes
    if let apiKey = Bundle.main.object(forInfoDictionaryKey: "GOOGLE_MAPS_API_KEY") as? String,
       !apiKey.isEmpty {
      GMSServices.provideAPIKey(apiKey)
    } else {
      print("[TUDOaqui] AVISO: GOOGLE_MAPS_API_KEY nao configurada — mapas nao funcionarao")
    }
    GeneratedPluginRegistrant.register(with: self)
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
