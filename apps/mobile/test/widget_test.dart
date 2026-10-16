import 'package:flutter_test/flutter_test.dart';
import 'package:elevra_mobile/main.dart';

void main() {
  testWidgets('renders Elevra home screen', (tester) async {
    await tester.pumpWidget(const ElevraApp());
    expect(find.text('Elevra'), findsOneWidget);
    expect(find.text('Browse exams and opportunities'), findsOneWidget);
    expect(find.text('Keep your next steps in view'), findsOneWidget);
  });
}
