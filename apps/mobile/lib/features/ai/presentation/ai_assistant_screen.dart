import 'package:flutter/material.dart';

import '../../../shared/widgets/elevra_scaffold.dart';

class AiAssistantScreen extends StatelessWidget {
  const AiAssistantScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ElevraScaffold(
      title: 'AI Assistant',
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Expanded(
              child: Card(
                child: Padding(
                  padding: EdgeInsets.all(18),
                  child: Text(
                    'Ask the Career, Learning, Resume, Exam, Scholarship, Interview, or Recommendation Agent for contextual help.',
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              decoration: InputDecoration(
                hintText: 'Ask Elevra AI',
                suffixIcon: IconButton(
                    onPressed: () {}, icon: const Icon(Icons.send_outlined)),
                border: const OutlineInputBorder(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
