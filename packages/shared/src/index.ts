// Shared domain primitives that are safe to use across web, admin, and services tooling.
import { z } from "zod";

export const OpportunityTypeSchema = z.enum([
  "scholarship",
  "internship",
  "competition",
  "course",
  "exam",
]);

export type OpportunityType = z.infer<typeof OpportunityTypeSchema>;

export const OpportunityStatusSchema = z.enum([
  "draft",
  "pending_review",
  "approved",
  "rejected",
  "archived",
]);

export type OpportunityStatus = z.infer<typeof OpportunityStatusSchema>;

export const OpportunitySchema = z.object({
  id: z.string(),
  type: OpportunityTypeSchema,
  status: OpportunityStatusSchema,
  title: z.string(),
  provider_name: z.string(),
  description: z.string(),
  country: z.string().nullable(),
  grade_levels: z.array(z.string()),
  tags: z.array(z.string()),
  source_url: z.string().url().nullable(),
  deadline_at: z.string().nullable(),
  popularity_score: z.number(),
});

export type Opportunity = z.infer<typeof OpportunitySchema>;

export const StudentProfileSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  full_name: z.string().min(1),
  graduation_year: z.number().int().min(2020).max(2100).optional(),
  interests: z.array(z.string()).default([]),
  roles: z.array(z.string()).default([]),
  permissions: z.array(z.string()).default([]),
});

export type StudentProfile = z.infer<typeof StudentProfileSchema>;

export const AiAgentSchema = z.object({
  key: z.enum([
    "career",
    "learning",
    "resume",
    "exam",
    "scholarship",
    "interview",
    "recommendation",
  ]),
  name: z.string(),
  purpose: z.string(),
  tools: z.array(z.string()),
  guardrails: z.array(z.string()),
});

export type AiAgent = z.infer<typeof AiAgentSchema>;

export const PaginationMetaSchema = z.object({
  page: z.number().int().min(1),
  page_size: z.number().int().min(1),
  total: z.number().int().min(0),
});

export type PaginationMeta = z.infer<typeof PaginationMetaSchema>;

export const ApiErrorSchema = z.object({
  code: z.string(),
  message: z.string(),
  requestId: z.string().optional(),
});

export type ApiError = z.infer<typeof ApiErrorSchema>;
