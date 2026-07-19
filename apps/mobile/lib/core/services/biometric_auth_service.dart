import 'package:local_auth/local_auth.dart';

class BiometricAuthService {
  BiometricAuthService({LocalAuthentication? localAuthentication})
      : _localAuthentication = localAuthentication ?? LocalAuthentication();

  final LocalAuthentication _localAuthentication;

  Future<bool> authenticate() {
    return _localAuthentication.authenticate(
      localizedReason: 'Unlock Elevra',
      options:
          const AuthenticationOptions(biometricOnly: false, stickyAuth: true),
    );
  }
}
