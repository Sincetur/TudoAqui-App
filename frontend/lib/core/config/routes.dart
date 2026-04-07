import 'package:flutter/material.dart';

import '../../features/auth/screens/splash_screen.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/otp_screen.dart';
import '../../features/home/screens/home_screen.dart';
import '../../features/ride/screens/request_ride_screen.dart';
import '../../features/ride/screens/ride_tracking_screen.dart';
import '../../features/profile/screens/profile_screen.dart';

/// Rotas da aplicação
class AppRoutes {
  AppRoutes._();
  
  // Auth
  static const String splash = '/';
  static const String login = '/login';
  static const String otp = '/otp';
  
  // Main
  static const String home = '/home';
  static const String profile = '/profile';
  
  // Ride
  static const String requestRide = '/ride/request';
  static const String rideTracking = '/ride/tracking';
  static const String rideHistory = '/ride/history';
  static const String rideDetails = '/ride/details';
  
  // Driver
  static const String driverHome = '/driver/home';
  static const String driverEarnings = '/driver/earnings';
  
  // Route generator
  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case splash:
        return _buildRoute(const SplashScreen(), settings);
      
      case login:
        return _buildRoute(const LoginScreen(), settings);
      
      case otp:
        final args = settings.arguments as Map<String, dynamic>?;
        return _buildRoute(
          OTPScreen(telefone: args?['telefone'] ?? ''),
          settings,
        );
      
      case home:
        return _buildRoute(const HomeScreen(), settings);
      
      case profile:
        return _buildRoute(const ProfileScreen(), settings);
      
      case requestRide:
        return _buildRoute(const RequestRideScreen(), settings);
      
      case rideTracking:
        final args = settings.arguments as Map<String, dynamic>?;
        return _buildRoute(
          RideTrackingScreen(rideId: args?['rideId']),
          settings,
        );
      
      default:
        return _buildRoute(
          Scaffold(
            body: Center(
              child: Text('Rota não encontrada: ${settings.name}'),
            ),
          ),
          settings,
        );
    }
  }
  
  static PageRoute _buildRoute(Widget page, RouteSettings settings) {
    return MaterialPageRoute(
      builder: (_) => page,
      settings: settings,
    );
  }
}
