import React from "react";
import { notFound } from "next/navigation";
import RouteContent from "./route-content";
import { isKnownWebRoute } from "./route-registry";

type PageProps = { params: Promise<{ slug?: string[] }> };

export default async function Page({ params }: PageProps) {
  const resolvedParams = await params;
  if (!isKnownWebRoute(resolvedParams.slug ?? [])) notFound();
  return <RouteContent params={resolvedParams} />;
}
