class AppConfig {
  const AppConfig({
    required this.apiBaseUrl,
    required this.webBaseUrl,
    required this.environment,
  });

  factory AppConfig.fromEnvironment() {
    return const AppConfig(
      apiBaseUrl: String.fromEnvironment(
        'ELEVRA_API_BASE_URL',
        defaultValue: 'http://localhost:8000',
      ),
      webBaseUrl: String.fromEnvironment(
        'ELEVRA_WEB_BASE_URL',
        defaultValue: 'http://localhost:3001',
      ),
      environment: String.fromEnvironment(
        'ELEVRA_ENVIRONMENT',
        defaultValue: 'development',
      ),
    );
  }

  final String apiBaseUrl;
  final String webBaseUrl;
  final String environment;
}

final appConfig = AppConfig.fromEnvironment();
