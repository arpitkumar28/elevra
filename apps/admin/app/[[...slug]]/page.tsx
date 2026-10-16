"use client";

import { AdminWorkspace } from "../content-manager";

export default function AdminPage({ params }: { params: { slug?: string[] } }) {
  return <AdminWorkspace route={params.slug?.[0] || "dashboard"} />;
}
