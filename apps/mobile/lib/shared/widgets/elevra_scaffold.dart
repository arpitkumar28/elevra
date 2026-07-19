import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class ElevraScaffold extends StatelessWidget {
  const ElevraScaffold({
    required this.title,
    required this.child,
    super.key,
    this.actions = const [],
  });

  final String title;
  final Widget child;
  final List<Widget> actions;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title), actions: actions),
      body: SafeArea(child: child),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex(context),
        onDestinationSelected: (index) {
          switch (index) {
            case 0:
              context.go('/');
            case 1:
              context.go('/opportunities');
            case 2:
              context.go('/ai');
            case 3:
              context.go('/planner');
            case 4:
              context.go('/profile');
          }
        },
        destinations: const [
          NavigationDestination(
              icon: Icon(Icons.dashboard_outlined), label: 'Home'),
          NavigationDestination(
              icon: Icon(Icons.explore_outlined), label: 'Discover'),
          NavigationDestination(
              icon: Icon(Icons.auto_awesome_outlined), label: 'AI'),
          NavigationDestination(
              icon: Icon(Icons.event_note_outlined), label: 'Plan'),
          NavigationDestination(
              icon: Icon(Icons.person_outline), label: 'Profile'),
        ],
      ),
    );
  }

  int _selectedIndex(BuildContext context) {
    final path = GoRouterState.of(context).uri.path;
    if (path.startsWith('/opportunities')) return 1;
    if (path.startsWith('/ai')) return 2;
    if (path.startsWith('/planner')) return 3;
    if (path.startsWith('/profile') || path.startsWith('/settings')) return 4;
    return 0;
  }
}
