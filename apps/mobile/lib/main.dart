import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

const brand = Color(0xFFF5C542);
const apiUrl = String.fromEnvironment('API_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1');
void main() => runApp(const ElevraApp());

class ApiRepository {
  Future<List<Map<String, dynamic>>> list(String path) async {
    final response = await http
        .get(Uri.parse('$apiUrl/$path'))
        .timeout(const Duration(seconds: 10));
    if (response.statusCode != 200) throw Exception('Could not load content');
    return List<Map<String, dynamic>>.from(jsonDecode(response.body)['items']);
  }

  Future<Map<String, dynamic>> get(String path, String slug) async {
    final response = await http
        .get(Uri.parse('$apiUrl/$path/$slug'))
        .timeout(const Duration(seconds: 10));
    if (response.statusCode != 200) throw Exception('Could not load this item');
    return Map<String, dynamic>.from(jsonDecode(response.body));
  }
}

class ElevraApp extends StatelessWidget {
  const ElevraApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
      title: 'Elevra',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
                  seedColor: brand, brightness: Brightness.light)
              .copyWith(surface: Colors.white),
          scaffoldBackgroundColor: const Color(0xFFFFFCF2),
          useMaterial3: true,
          appBarTheme: const AppBarTheme(
              backgroundColor: Color(0xFFFFFCF2),
              foregroundColor: Color(0xFF172039),
              elevation: 0,
              centerTitle: false),
          cardTheme: const CardThemeData(
              color: Colors.white,
              elevation: 0,
              margin: EdgeInsets.zero,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.all(Radius.circular(18))))),
      home: const Shell());
}

class Shell extends StatefulWidget {
  const Shell({super.key});
  @override
  State<Shell> createState() => _ShellState();
}

class _ShellState extends State<Shell> {
  int tab = 0;
  @override
  Widget build(BuildContext context) {
    final screens = [
      const Home(),
      const Explore(),
      const PlaceholderScreen(
          icon: Icons.bookmark_outline,
          title: 'Saved',
          body: 'Saving requires an Elevra account.'),
      const PlaceholderScreen(
          icon: Icons.notifications_none,
          title: 'Notifications',
          body: 'No notifications yet.'),
      const PlaceholderScreen(
          icon: Icons.person_outline,
          title: 'Profile',
          body: 'Sign in to personalize your Elevra experience.')
    ];
    return Scaffold(
        body: screens[tab],
        bottomNavigationBar: NavigationBar(
            selectedIndex: tab,
            onDestinationSelected: (v) => setState(() => tab = v),
            destinations: const [
              NavigationDestination(
                  icon: Icon(Icons.home_outlined), label: 'Home'),
              NavigationDestination(
                  icon: Icon(Icons.explore_outlined), label: 'Explore'),
              NavigationDestination(
                  icon: Icon(Icons.bookmark_outline), label: 'Saved'),
              NavigationDestination(
                  icon: Icon(Icons.notifications_none), label: 'Alerts'),
              NavigationDestination(
                  icon: Icon(Icons.person_outline), label: 'Profile')
            ]));
  }
}

class Home extends StatelessWidget {
  const Home({super.key});
  @override
  Widget build(BuildContext c) => SafeArea(
          child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 18, 20, 28),
              children: [
            Row(children: [
              Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12)),
                  child: const Icon(Icons.menu_rounded, size: 20)),
              const Spacer(),
              Text('Elevra',
                  style: Theme.of(c).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w900, letterSpacing: -.6)),
              const Spacer(),
              Badge(
                  smallSize: 7,
                  child: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12)),
                      child: const Icon(Icons.notifications_none_rounded,
                          size: 20)))
            ]),
            const SizedBox(height: 22),
            const Text('INDIA’S OPPORTUNITY HUB',
                style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 1.4,
                    color: Color(0xFFD99400))),
            const SizedBox(height: 8),
            Text('Your Career &\nExam Companion',
                style: Theme.of(c).textTheme.displaySmall?.copyWith(
                    fontWeight: FontWeight.w900,
                    height: 1.03,
                    letterSpacing: -1,
                    color: const Color(0xFF172039))),
            const SizedBox(height: 12),
            const Text(
                'Find verified updates, plan your preparation, and never miss a deadline.',
                style: TextStyle(color: Color(0xFF64748B), height: 1.5)),
            const SizedBox(height: 20),
            TextField(
                decoration: InputDecoration(
                    prefixIcon: const Icon(Icons.search),
                    hintText: 'Search exams, jobs, courses...',
                    filled: true,
                    fillColor: Colors.white,
                    contentPadding: const EdgeInsets.symmetric(vertical: 3),
                    border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: BorderSide.none))),
            const SizedBox(height: 14),
            Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                    color: const Color(0xFF172039),
                    borderRadius: BorderRadius.circular(18)),
                child: const Row(children: [
                  Icon(Icons.notifications_active_outlined,
                      color: Color(0xFFF5C542)),
                  SizedBox(width: 12),
                  Expanded(
                      child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                        Text('9 deadlines this week',
                            style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w800)),
                        SizedBox(height: 2),
                        Text('Get timely reminders for what matters.',
                            style: TextStyle(
                                fontSize: 12, color: Color(0xFFCBD5E1)))
                      ])),
                  Icon(Icons.arrow_forward_rounded, color: Color(0xFFF5C542))
                ])),
            const SizedBox(height: 26),
            Row(children: [
              Text('Explore categories',
                  style: Theme.of(c)
                      .textTheme
                      .titleMedium
                      ?.copyWith(fontWeight: FontWeight.w900)),
              const Spacer(),
              const Text('View all',
                  style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFFD99400)))
            ]),
            const SizedBox(height: 12),
            const Wrap(spacing: 10, runSpacing: 10, children: [
              _Category('Exams', Icons.school_outlined),
              _Category('Jobs', Icons.work_outline),
              _Category('Internships', Icons.rocket_launch_outlined),
              _Category('Scholarships', Icons.workspace_premium_outlined)
            ]),
            const SizedBox(height: 28),
            Row(children: [
              Text('Trending now',
                  style: Theme.of(c)
                      .textTheme
                      .titleMedium
                      ?.copyWith(fontWeight: FontWeight.w900)),
              const Spacer(),
              const Text('See all',
                  style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFFD99400)))
            ]),
            const SizedBox(height: 12),
            const _LinkCard(
                title: 'UPSC CSE 2025',
                body: 'Application date and official notice.',
                icon: Icons.account_balance_outlined),
            const SizedBox(height: 12),
            const _LinkCard(
                title: 'Latest opportunities',
                body: 'Jobs, internships, scholarships and more.',
                icon: Icons.rocket_launch_outlined)
          ]));
}

class _Category extends StatelessWidget {
  final String label;
  final IconData icon;
  const _Category(this.label, this.icon);
  @override
  Widget build(BuildContext c) => Container(
      width: (MediaQuery.of(c).size.width - 50) / 2,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFF1F2F4))),
      child: Row(children: [
        Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
                color: const Color(0xFFFFF3CC),
                borderRadius: BorderRadius.circular(10)),
            child: Icon(icon, color: const Color(0xFFD99400), size: 19)),
        const SizedBox(width: 9),
        Expanded(
            child: Text(label,
                style:
                    const TextStyle(fontSize: 12, fontWeight: FontWeight.w700)))
      ]));
}

class Explore extends StatelessWidget {
  const Explore({super.key});
  @override
  Widget build(BuildContext c) => DefaultTabController(
      length: 2,
      child: Scaffold(
          appBar: AppBar(
              title: const Text('Explore'),
              bottom: const TabBar(
                  tabs: [Tab(text: 'Exams'), Tab(text: 'Opportunities')])),
          body: const TabBarView(children: [
            ContentList(path: 'exams', isExam: true),
            ContentList(path: 'opportunities', isExam: false)
          ])));
}

class ContentList extends StatefulWidget {
  final String path;
  final bool isExam;
  const ContentList({super.key, required this.path, required this.isExam});
  @override
  State<ContentList> createState() => _ContentListState();
}

class _ContentListState extends State<ContentList> {
  final repo = ApiRepository();
  late Future<List<Map<String, dynamic>>> future;
  @override
  void initState() {
    super.initState();
    future = repo.list(widget.path);
  }

  Future<void> refresh() async =>
      setState(() => future = repo.list(widget.path));
  @override
  Widget build(BuildContext c) => FutureBuilder(
      future: future,
      builder: (c, s) {
        if (s.connectionState != ConnectionState.done)
          return const Center(child: CircularProgressIndicator());
        if (s.hasError)
          return Center(
              child: Column(mainAxisSize: MainAxisSize.min, children: [
            Text('${s.error}'),
            FilledButton(onPressed: refresh, child: const Text('Try again'))
          ]));
        final rows = s.data ?? [];
        if (rows.isEmpty)
          return const Center(child: Text('No results right now.'));
        return RefreshIndicator(
            onRefresh: refresh,
            child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: rows.length,
                itemBuilder: (c, i) {
                  final x = rows[i];
                  final title = widget.isExam ? x['name'] : x['title'];
                  final sub =
                      widget.isExam ? x['conducting_body'] : x['organization'];
                  return Card(
                      child: ListTile(
                          title: Text(title ?? ''),
                          subtitle: Text(
                              '${sub ?? 'To be announced'}\n${widget.isExam ? x['category'] : x['type']}'),
                          isThreeLine: true,
                          trailing: x['verified'] == true
                              ? const Icon(Icons.verified, color: Colors.green)
                              : null,
                          onTap: () => Navigator.push(
                              c,
                              MaterialPageRoute(
                                  builder: (_) => Detail(
                                      path: widget.path,
                                      slug: x['slug'],
                                      isExam: widget.isExam)))));
                }));
      });
}

class Detail extends StatefulWidget {
  final String path, slug;
  final bool isExam;
  const Detail(
      {super.key,
      required this.path,
      required this.slug,
      required this.isExam});
  @override
  State<Detail> createState() => _DetailState();
}

class _DetailState extends State<Detail> {
  late Future<Map<String, dynamic>> future;
  final repo = ApiRepository();
  @override
  void initState() {
    super.initState();
    future = repo.get(widget.path, widget.slug);
  }

  @override
  Widget build(BuildContext c) => FutureBuilder(
      future: future,
      builder: (c, s) {
        if (s.connectionState != ConnectionState.done)
          return const Scaffold(
              body: Center(child: CircularProgressIndicator()));
        if (s.hasError)
          return Scaffold(
              appBar: AppBar(), body: Center(child: Text('${s.error}')));
        final x = s.data!;
        final title = widget.isExam ? x['name'] : x['title'];
        return Scaffold(
            appBar: AppBar(),
            body: ListView(padding: const EdgeInsets.all(20), children: [
              Text(title,
                  style: Theme.of(c)
                      .textTheme
                      .headlineSmall
                      ?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              if (x['verified'] == true)
                const Chip(
                    label: Text('Verified source'),
                    avatar: Icon(Icons.verified, color: Colors.green)),
              const SizedBox(height: 20),
              Text('Overview', style: Theme.of(c).textTheme.titleLarge),
              Text(x['description'] ??
                  'Details will be updated from the official source.'),
              const SizedBox(height: 20),
              Text(widget.isExam ? 'Important dates' : 'Eligibility',
                  style: Theme.of(c).textTheme.titleLarge),
              Text(widget.isExam
                  ? 'Application deadline: ${x['application_deadline'] ?? 'To be announced'}\nExam date: ${x['exam_date'] ?? 'To be announced'}'
                  : x['eligibility'] ??
                      'Eligibility details will be updated from the official source.'),
              const SizedBox(height: 24),
              FilledButton(
                  onPressed: () => ScaffoldMessenger.of(c).showSnackBar(
                      const SnackBar(
                          content: Text(
                              'Open the official source in your browser.'))),
                  child: Text(widget.isExam
                      ? 'Visit official website'
                      : 'Apply on official website'))
            ]));
      });
}

class PlaceholderScreen extends StatelessWidget {
  final IconData icon;
  final String title, body;
  const PlaceholderScreen(
      {super.key, required this.icon, required this.title, required this.body});
  @override
  Widget build(BuildContext c) => SafeArea(
      child: Center(
          child: Padding(
              padding: const EdgeInsets.all(30),
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                Icon(icon, size: 48),
                const SizedBox(height: 16),
                Text(title, style: Theme.of(c).textTheme.headlineSmall),
                const SizedBox(height: 8),
                Text(body, textAlign: TextAlign.center)
              ]))));
}

class _LinkCard extends StatelessWidget {
  final String title, body;
  final IconData icon;
  const _LinkCard(
      {required this.title, required this.body, required this.icon});

  @override
  Widget build(BuildContext context) => Card(
        child: Container(
          decoration: BoxDecoration(
            border: Border.all(color: const Color(0xFFF0F1F3)),
            borderRadius: BorderRadius.circular(18),
          ),
          child: ListTile(
            contentPadding: const EdgeInsets.all(18),
            leading: Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: const Color(0xFFFFF3CC),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: const Color(0xFFD99400)),
            ),
            title: Text(title,
                style: const TextStyle(fontWeight: FontWeight.w800)),
            subtitle: Padding(
                padding: const EdgeInsets.only(top: 4), child: Text(body)),
            trailing: const Icon(Icons.chevron_right_rounded),
          ),
        ),
      );
}
