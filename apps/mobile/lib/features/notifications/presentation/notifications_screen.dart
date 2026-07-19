import 'package:flutter/material.dart';

import '../../../shared/widgets/elevra_scaffold.dart';

class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ElevraScaffold(
      title: 'Notifications',
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: const [
          Card(
            child: ListTile(
              leading: Icon(Icons.schedule_outlined),
              title: Text('Scholarship deadline moved into priority window'),
              subtitle: Text('Review checklist and essay draft today.'),
            ),
          ),
        ],
      ),
    );
  }
}
