import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Spacer(),
              Text('Elevra', style: Theme.of(context).textTheme.displayMedium),
              const SizedBox(height: 12),
              Text(
                'AI Powered Student Operating System',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 16),
              const Text(
                'Personalized opportunities, learning plans, reminders, and AI guidance built for mobile-first student workflows.',
              ),
              const Spacer(),
              FilledButton(
                onPressed: () => context.go('/'),
                child: const Text('Continue'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
