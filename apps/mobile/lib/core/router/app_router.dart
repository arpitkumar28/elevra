import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../features/ai/presentation/ai_assistant_screen.dart';
import '../../features/authentication/presentation/onboarding_screen.dart';
import '../../features/dashboard/presentation/dashboard_screen.dart';
import '../../features/notifications/presentation/notifications_screen.dart';
import '../../features/opportunities/presentation/opportunity_detail_screen.dart';
import '../../features/opportunities/presentation/opportunity_feed_screen.dart';
import '../../features/planner/presentation/study_planner_screen.dart';
import '../../features/profile/presentation/profile_screen.dart';
import '../../features/settings/presentation/settings_screen.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/onboarding',
    routes: [
      GoRoute(
          path: '/onboarding',
          builder: (context, state) => const OnboardingScreen()),
      GoRoute(path: '/', builder: (context, state) => const DashboardScreen()),
      GoRoute(
          path: '/opportunities',
          builder: (context, state) => const OpportunityFeedScreen()),
      GoRoute(
        path: '/opportunities/:id',
        builder: (context, state) =>
            OpportunityDetailScreen(id: state.pathParameters['id']!),
      ),
      GoRoute(
          path: '/notifications',
          builder: (context, state) => const NotificationsScreen()),
      GoRoute(
          path: '/ai', builder: (context, state) => const AiAssistantScreen()),
      GoRoute(
          path: '/planner',
          builder: (context, state) => const StudyPlannerScreen()),
      GoRoute(
          path: '/profile', builder: (context, state) => const ProfileScreen()),
      GoRoute(
          path: '/settings',
          builder: (context, state) => const SettingsScreen()),
    ],
  );
});
