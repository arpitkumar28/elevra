import { AdminWorkspace } from "../content-manager";

export default async function AdminPage({ params }: { params: Promise<{ slug?: string[] }> }) {
  const { slug } = await params;
  return <AdminWorkspace route={slug?.[0] || "dashboard"} />;
}
