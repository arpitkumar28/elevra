import 'package:hive_flutter/hive_flutter.dart';

import '../constants/app_constants.dart';

class OfflineStore {
  OfflineStore({
    Box<String>? bookmarks,
    Box<dynamic>? settings,
  })  : _bookmarks = bookmarks ?? Hive.box<String>(AppConstants.bookmarkBox),
        _settings = settings ?? Hive.box<dynamic>(AppConstants.settingsBox);

  final Box<String> _bookmarks;
  final Box<dynamic> _settings;

  List<String> bookmarkedOpportunityIds() =>
      _bookmarks.values.toList(growable: false);

  Future<void> toggleBookmark(String opportunityId) async {
    if (_bookmarks.containsKey(opportunityId)) {
      await _bookmarks.delete(opportunityId);
      return;
    }
    await _bookmarks.put(opportunityId, opportunityId);
  }

  T? setting<T>(String key) => _settings.get(key) as T?;

  Future<void> setSetting(String key, Object? value) =>
      _settings.put(key, value);
}
