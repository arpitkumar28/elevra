class Opportunity {
  const Opportunity({
    required this.id,
    required this.title,
    required this.provider,
    required this.type,
    required this.deadline,
    required this.tags,
    required this.matchScore,
  });

  final String id;
  final String title;
  final String provider;
  final String type;
  final String deadline;
  final List<String> tags;
  final double matchScore;
}
