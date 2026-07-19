import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../shared/widgets/elevra_scaffold.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ElevraScaffold(
      title: 'Today',
      actions: [
        IconButton(
          onPressed: () => context.go('/notifications'),
          icon: const Icon(Icons.notifications_outlined),
        ),
        IconButton(
          onPressed: () => context.go('/settings'),
          icon: const Icon(Icons.settings_outlined),
        ),
      ],
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: const [
          _MetricCard(
              title: 'Opportunity matches',
              value: '128',
              icon: Icons.explore_outlined),
          SizedBox(height: 12),
          _MetricCard(
              title: 'Exam readiness',
              value: '72%',
              icon: Icons.school_outlined),
          SizedBox(height: 12),
          _MetricCard(
              title: 'Planner focus blocks',
              value: '5',
              icon: Icons.event_note_outlined),
        ],
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard(
      {required this.title, required this.value, required this.icon});

  final String title;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          children: [
            Icon(icon, size: 32),
            const SizedBox(width: 16),
            Expanded(
                child: Text(title,
                    style: Theme.of(context).textTheme.titleMedium)),
            Text(value, style: Theme.of(context).textTheme.headlineSmall),
          ],
        ),
      ),
    );
  }
}
