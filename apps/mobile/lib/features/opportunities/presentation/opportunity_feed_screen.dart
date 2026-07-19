import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../shared/models/opportunity.dart';
import '../../../shared/widgets/elevra_scaffold.dart';

const _opportunities = [
  Opportunity(
    id: 'opp_scholarship_global_ai',
    title: 'Global AI Scholars Program',
    provider: 'Elevra Verified Network',
    type: 'Scholarship',
    deadline: '31 Oct 2026',
    tags: ['AI', 'Scholarship', 'Portfolio'],
    matchScore: 0.94,
  ),
  Opportunity(
    id: 'opp_exam_research_lab',
    title: 'Student Research Lab Internship',
    provider: 'Open Research Collective',
    type: 'Internship',
    deadline: '12 Nov 2026',
    tags: ['Research', 'STEM'],
    matchScore: 0.89,
  ),
];

class OpportunityFeedScreen extends StatelessWidget {
  const OpportunityFeedScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ElevraScaffold(
      title: 'Discover',
      child: ListView.separated(
        padding: const EdgeInsets.all(20),
        itemBuilder: (context, index) {
          final opportunity = _opportunities[index];
          return Card(
            child: ListTile(
              contentPadding: const EdgeInsets.all(16),
              title: Text(opportunity.title),
              subtitle: Text(
                  '${opportunity.provider}\nDeadline: ${opportunity.deadline}'),
              isThreeLine: true,
              trailing: Text('${(opportunity.matchScore * 100).round()}%'),
              onTap: () => context.go('/opportunities/${opportunity.id}'),
            ),
          );
        },
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemCount: _opportunities.length,
      ),
    );
  }
}
