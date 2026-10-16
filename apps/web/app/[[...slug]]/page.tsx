import React from "react";
import { notFound } from "next/navigation";
import RouteContent from "./route-content";
import { isKnownWebRoute } from "./route-registry";

type PageProps = { params: { slug?: string[] } };

export default function Page({ params }: PageProps) {
  if (!isKnownWebRoute(params.slug ?? [])) notFound();
  return <RouteContent params={params} />;
}
