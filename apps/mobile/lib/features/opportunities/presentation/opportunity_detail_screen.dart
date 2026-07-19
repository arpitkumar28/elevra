import 'package:flutter/material.dart';

import '../../../shared/widgets/elevra_scaffold.dart';

class OpportunityDetailScreen extends StatelessWidget {
  const OpportunityDetailScreen({required this.id, super.key});

  final String id;

  @override
  Widget build(BuildContext context) {
    return ElevraScaffold(
      title: 'Opportunity',
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text('Global AI Scholars Program',
              style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 12),
          Text('Reference: $id'),
          const SizedBox(height: 16),
          const Text(
            'A verified opportunity for students with strong AI project portfolios. Elevra tracks requirements, drafts, deadlines, and submission readiness.',
          ),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.bookmark_add_outlined),
            label: const Text('Bookmark'),
          ),
        ],
      ),
    );
  }
}
