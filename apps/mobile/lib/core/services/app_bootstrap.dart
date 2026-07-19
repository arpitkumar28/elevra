import 'package:hive_flutter/hive_flutter.dart';

import '../constants/app_constants.dart';

class AppBootstrap {
  const AppBootstrap._();

  static Future<void> initialize() async {
    await Hive.initFlutter();
    await Future.wait([
      Hive.openBox<String>(AppConstants.bookmarkBox),
      Hive.openBox<dynamic>(AppConstants.settingsBox),
    ]);
  }
}
