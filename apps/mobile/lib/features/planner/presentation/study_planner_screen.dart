import 'package:flutter/material.dart';

import '../../../shared/widgets/elevra_scaffold.dart';

class StudyPlannerScreen extends StatelessWidget {
  const StudyPlannerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ElevraScaffold(
      title: 'Planner',
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: const [
          Card(
            child: ListTile(
              leading: Icon(Icons.calendar_month_outlined),
              title: Text('Physics revision block'),
              subtitle: Text('Today, 6:00 PM - adaptive mock review'),
            ),
          ),
          SizedBox(height: 12),
          Card(
            child: ListTile(
              leading: Icon(Icons.edit_note_outlined),
              title: Text('Scholarship essay review'),
              subtitle: Text('Tomorrow, 8:00 AM - AI critique pass'),
            ),
          ),
        ],
      ),
    );
  }
}
