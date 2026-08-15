import type { MetadataRoute } from "next";
export default function sitemap(): MetadataRoute.Sitemap {
  return [
    "",
    "/explore",
    "/exams",
    "/jobs",
    "/internships",
    "/scholarships",
    "/competitions",
    "/career",
  ].map((path) => ({ url: `https://elevra.app${path}`, lastModified: new Date() }));
}
