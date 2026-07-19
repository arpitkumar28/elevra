import 'package:elevra_mobile/main.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('renders Elevra dashboard', (tester) async {
    await tester.pumpWidget(const ElevraApp());
    await tester.pumpAndSettle();
    expect(find.text('Elevra'), findsOneWidget);
  });
}
