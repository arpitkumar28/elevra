import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_theme.dart';
import '../../../shared/widgets/elevra_scaffold.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final mode = ref.watch(themeModeProvider);
    return ElevraScaffold(
      title: 'Settings',
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          SwitchListTile(
            title: const Text('Dark mode'),
            value: mode == ThemeMode.dark,
            onChanged: (value) {
              ref.read(themeModeProvider.notifier).state =
                  value ? ThemeMode.dark : ThemeMode.light;
            },
          ),
          const ListTile(
            leading: Icon(Icons.fingerprint_outlined),
            title: Text('Biometric login'),
            subtitle: Text('Use device authentication after first sign-in.'),
          ),
          const ListTile(
            leading: Icon(Icons.link_outlined),
            title: Text('Deep links'),
            subtitle: Text('Open opportunities and planner events directly.'),
          ),
        ],
      ),
    );
  }
}
