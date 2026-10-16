"use client";

import Link from "next/link";
import type { Route } from "next";
import React, { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import {
  type Application,
  type Exam,
  type Notification,
  type Opportunity,
  type ProfileUpdate,
  type StudentProfile,
  type TestDetail,
  type TestSubmission,
} from "@elevra/api-client";
import { usePathname } from "next/navigation";
import { authenticatedApi, useAuth } from "./auth-provider";

const inputClass =
  "mt-1 w-full rounded-xl border border-[#d8e1da] bg-white px-4 py-3 text-sm outline-none focus:border-[#56816d] focus:ring-2 focus:ring-[#d5e7cf]";

export function ProfilePage() {
  const { withSession } = useAuth();
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [draft, setDraft] = useState<ProfileUpdate>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await withSession((token) => authenticatedApi.getProfile(token));
      setProfile(data);
      setDraft({
        display_name: data.display_name ?? "",
        phone: data.phone ?? "",
        city: data.city ?? "",
        state: data.state ?? "",
        country: data.country ?? "",
        education_level: data.education_level ?? "",
        institution: data.institution ?? "",
        degree: data.degree ?? "",
        stream: data.stream ?? "",
        graduation_year: data.graduation_year ?? undefined,
        exam_interests: data.exam_interests ?? [],
        opportunity_interests: data.opportunity_interests ?? [],
        preferred_locations: data.preferred_locations ?? [],
        remote_preference: data.remote_preference ?? false,
        career_interests: data.career_interests ?? [],
        target_roles: data.target_roles ?? [],
        skills: data.skills ?? [],
        experience_level: data.experience_level ?? "",
        notification_preferences: data.notification_preferences ?? {},
      });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load your profile.");
    } finally {
      setLoading(false);
    }
  }, [withSession]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");
    try {
      const updated = await withSession((token) => authenticatedApi.updateProfile(draft, token));
      setProfile(updated);
      setMessage("Your profile has been saved.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to save your profile.");
    } finally {
      setSaving(false);
    }
  }

  function update<K extends keyof ProfileUpdate>(key: K, value: ProfileUpdate[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  const textFields: Array<[keyof ProfileUpdate, string]> = [
    ["display_name", "Display name"],
    ["phone", "Phone"],
    ["city", "City"],
    ["state", "State"],
    ["country", "Country"],
    ["education_level", "Education level"],
    ["institution", "Institution"],
    ["degree", "Degree"],
    ["stream", "Stream"],
    ["experience_level", "Experience level"],
  ];

  if (loading)
    return (
      <main className="mx-auto max-w-4xl px-5 py-12" aria-live="polite">
        Loading your profile…
      </main>
    );
  if (error && !profile)
    return <AccountError title="Profile unavailable" message={error} retry={() => void load()} />;
  return (
    <main className="mx-auto max-w-4xl px-5 py-12 lg:px-8">
      <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">Account</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight">Your profile</h1>
      <p className="mt-3 text-[#63736c]">
        Update the details and preferences saved to your student profile.
      </p>
      <form
        onSubmit={save}
        className="mt-8 space-y-7 rounded-3xl border border-[#e3e9e4] bg-white p-6 sm:p-8"
      >
        <section>
          <h2 className="text-lg font-semibold">Personal and education details</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {textFields.map(([key, label]) => (
              <label key={key} htmlFor={`profile-${key}`} className="text-sm font-semibold">
                {label}
                <input
                  id={`profile-${key}`}
                  name={key}
                  value={String(draft[key] ?? "")}
                  onChange={(event) => update(key, event.target.value)}
                  className={inputClass}
                />
              </label>
            ))}
            <label htmlFor="profile-graduation-year" className="text-sm font-semibold">
              Graduation year
              <input
                id="profile-graduation-year"
                type="number"
                min={1950}
                max={2100}
                value={draft.graduation_year ?? ""}
                onChange={(event) =>
                  update("graduation_year", event.target.value ? Number(event.target.value) : null)
                }
                className={inputClass}
              />
            </label>
          </div>
        </section>
        <section>
          <h2 className="text-lg font-semibold">Interests and preferences</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {(
              [
                ["exam_interests", "Exam interests"],
                ["opportunity_interests", "Opportunity interests"],
                ["preferred_locations", "Preferred locations"],
                ["career_interests", "Career interests"],
                ["target_roles", "Target roles"],
                ["skills", "Skills"],
              ] as Array<
                [
                  (
                    | "exam_interests"
                    | "opportunity_interests"
                    | "preferred_locations"
                    | "career_interests"
                    | "target_roles"
                    | "skills"
                  ),
                  string,
                ]
              >
            ).map(([key, label]) => (
              <label key={key} htmlFor={`profile-${key}`} className="text-sm font-semibold">
                {label}
                <input
                  id={`profile-${key}`}
                  value={(draft[key] ?? []).join(", ")}
                  onChange={(event) =>
                    update(
                      key,
                      event.target.value
                        .split(",")
                        .map((item) => item.trim())
                        .filter(Boolean),
                    )
                  }
                  className={inputClass}
                  aria-describedby={`help-${key}`}
                />
                <span id={`help-${key}`} className="mt-1 block text-xs font-normal text-[#63736c]">
                  Separate items with commas.
                </span>
              </label>
            ))}
          </div>
          <label className="mt-5 flex items-start gap-3 text-sm">
            <input
              type="checkbox"
              checked={draft.remote_preference ?? false}
              onChange={(event) => update("remote_preference", event.target.checked)}
              className="mt-0.5 h-4 w-4 accent-[#145b48]"
            />
            <span>
              <span className="font-semibold">Prefer remote opportunities</span>
              <span className="mt-1 block text-xs text-[#63736c]">
                Used to tailor your opportunity preferences.
              </span>
            </span>
          </label>
        </section>
        {error && (
          <p
            role="alert"
            className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
          >
            {error}
          </p>
        )}
        {message && (
          <p role="status" className="rounded-xl bg-[#eef4e8] px-4 py-3 text-sm text-[#28483b]">
            {message}
          </p>
        )}
        <button
          disabled={saving}
          className="rounded-xl bg-[#145b48] px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
        >
          {saving ? "Saving…" : "Save profile"}
        </button>
      </form>
    </main>
  );
}

type Bookmark = { id: string; entity_type: string; entity_id: string; created_at: string };
type ResolvedBookmark = Bookmark & { title?: string; href?: string };
type Attempt = {
  id: string;
  test_id: string;
  score?: number;
  total_questions: number;
  started_at: string;
  submitted_at?: string;
};

export function DashboardPage() {
  const { user, withSession } = useAuth();
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [attempts, setAttempts] = useState<Attempt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [savedItems, trackedApplications, userNotifications, testAttempts] = await Promise.all([
        withSession((token) => authenticatedApi.listBookmarks(token)),
        withSession((token) => authenticatedApi.listApplications(token)),
        withSession((token) => authenticatedApi.listNotifications(token)),
        withSession((token) => authenticatedApi.listTestAttempts(token)),
      ]);
      setBookmarks(savedItems);
      setApplications(trackedApplications);
      setNotifications(userNotifications);
      setAttempts(testAttempts);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load your account data.");
    } finally {
      setLoading(false);
    }
  }, [withSession]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading)
    return (
      <main className="mx-auto max-w-7xl px-5 py-12" aria-live="polite">
        Loading your dashboard…
      </main>
    );
  if (error)
    return <AccountError title="Dashboard unavailable" message={error} retry={() => void load()} />;
  return (
    <main className="mx-auto max-w-7xl px-5 py-12 lg:px-8">
      <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">Your account</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight">
        Welcome, {user?.name || "student"}.
      </h1>
      <p className="mt-3 text-[#63736c]">
        A summary of the saved items, applications, notifications and practice records in your
        account.
      </p>
      <section className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ["Saved items", bookmarks.length, "/saved"],
          ["Applications", applications.length, "#applications"],
          ["Notifications", notifications.length, "#notifications"],
          ["Practice attempts", attempts.length, "/tests"],
        ].map(([label, value, href]) => (
          <a
            key={String(label)}
            href={String(href)}
            className="rounded-2xl border border-[#e3e9e4] bg-white p-5 transition hover:border-[#b7c9b8]"
          >
            <span className="text-sm text-[#63736c]">{label}</span>
            <strong className="mt-2 block text-3xl font-semibold">{value}</strong>
          </a>
        ))}
      </section>
      <section id="applications" className="mt-8 rounded-2xl border border-[#e3e9e4] bg-white p-6">
        <h2 className="text-xl font-semibold">Application tracking</h2>
        {applications.length ? (
          <ul className="mt-4 divide-y divide-[#edf0ec]">
            {applications.map((application) => (
              <li
                key={application.id}
                className="flex flex-wrap items-center justify-between gap-3 py-4"
              >
                <div>
                  <p className="font-semibold">{application.title}</p>
                  <p className="mt-1 text-sm text-[#63736c]">
                    {application.organization || "Organization not provided"}
                  </p>
                </div>
                <span className="rounded-full bg-[#eef4e8] px-3 py-1 text-xs font-semibold text-[#42634e]">
                  {application.status.replaceAll("_", " ")}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 text-sm text-[#63736c]">
            No applications are being tracked yet. You can add one from an opportunity detail page.
          </p>
        )}
      </section>
      <section id="notifications" className="mt-5 rounded-2xl border border-[#e3e9e4] bg-white p-6">
        <h2 className="text-xl font-semibold">Notifications</h2>
        {notifications.length ? (
          <ul className="mt-4 divide-y divide-[#edf0ec]">
            {notifications.map((notification) => (
              <NotificationRow
                key={notification.id}
                notification={notification}
                onRead={async () => {
                  await withSession((token) =>
                    authenticatedApi.markNotificationRead(notification.id, token),
                  );
                  setNotifications((current) =>
                    current.map((item) =>
                      item.id === notification.id
                        ? { ...item, read_at: new Date().toISOString() }
                        : item,
                    ),
                  );
                }}
              />
            ))}
          </ul>
        ) : (
          <p className="mt-3 text-sm text-[#63736c]">
            No notifications have been sent to this account.
          </p>
        )}
      </section>
      <section className="mt-5 rounded-2xl border border-[#e3e9e4] bg-white p-6">
        <h2 className="text-xl font-semibold">Recent practice</h2>
        {attempts.length ? (
          <ul className="mt-4 divide-y divide-[#edf0ec]">
            {attempts.slice(0, 5).map((attempt) => (
              <li key={attempt.id} className="flex flex-wrap justify-between gap-2 py-3 text-sm">
                <Link
                  href={`/tests/${attempt.test_id}`}
                  className="font-semibold text-[#145b48] underline underline-offset-4"
                >
                  Practice test
                </Link>
                <span className="text-[#63736c]">
                  {attempt.submitted_at
                    ? `${attempt.score ?? 0} / ${attempt.total_questions} correct`
                    : "In progress"}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 text-sm text-[#63736c]">
            No test attempts are recorded yet.{" "}
            <Link href="/tests" className="font-semibold text-[#145b48]">
              Browse practice tests
            </Link>
          </p>
        )}
      </section>
    </main>
  );
}

function NotificationRow({
  notification,
  onRead,
}: {
  notification: Notification;
  onRead: () => Promise<void>;
}) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <li className="flex flex-wrap items-start justify-between gap-3 py-4">
      <div>
        <p className="font-semibold">{notification.title}</p>
        <p className="mt-1 text-sm leading-6 text-[#63736c]">{notification.body}</p>
        {error && (
          <p role="alert" className="mt-1 text-xs text-red-700">
            {error}
          </p>
        )}
      </div>
      {notification.read_at ? (
        <span className="text-xs text-[#63736c]">Read</span>
      ) : (
        <button
          disabled={busy}
          onClick={async () => {
            setBusy(true);
            setError("");
            try {
              await onRead();
            } catch (cause) {
              setError(cause instanceof Error ? cause.message : "Unable to update notification.");
            } finally {
              setBusy(false);
            }
          }}
          className="text-sm font-semibold text-[#145b48] underline underline-offset-4"
        >
          {busy ? "Saving…" : "Mark read"}
        </button>
      )}
    </li>
  );
}

export function NotificationsPage() {
  const { withSession } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setNotifications(await withSession((token) => authenticatedApi.listNotifications(token)));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load notifications.");
    } finally {
      setLoading(false);
    }
  }, [withSession]);
  useEffect(() => {
    void load();
  }, [load]);
  async function markRead(id: string) {
    await withSession((token) => authenticatedApi.markNotificationRead(id, token));
    setNotifications((items) =>
      items.map((item) => (item.id === id ? { ...item, read_at: new Date().toISOString() } : item)),
    );
  }
  if (loading)
    return (
      <main className="mx-auto max-w-4xl px-5 py-12" aria-live="polite">
        Loading notifications…
      </main>
    );
  if (error)
    return (
      <AccountError title="Notifications unavailable" message={error} retry={() => void load()} />
    );
  return (
    <main className="mx-auto max-w-4xl px-5 py-12 lg:px-8">
      <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">Your account</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight">Notifications</h1>
      {notifications.length ? (
        <ul className="mt-8 divide-y divide-[#edf0ec] rounded-2xl border border-[#e3e9e4] bg-white px-5">
          {notifications.map((notification) => (
            <NotificationRow
              key={notification.id}
              notification={notification}
              onRead={() => markRead(notification.id)}
            />
          ))}
        </ul>
      ) : (
        <div className="mt-8 rounded-2xl border border-dashed border-[#cbd8ce] bg-white p-8 text-center text-sm text-[#63736c]">
          You have no notifications yet.
        </div>
      )}
    </main>
  );
}

export function PracticeTestPage({ testId }: { testId: string }) {
  const { withSession } = useAuth();
  const [test, setTest] = useState<TestDetail | null>(null);
  const [attemptId, setAttemptId] = useState("");
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<TestSubmission | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const item = await authenticatedApi.getTest(testId);
      setTest(item);
      const history = await withSession((token) => authenticatedApi.listTestAttempts(token));
      const active = history.find((attempt) => attempt.test_id === testId && !attempt.submitted_at);
      if (active) {
        setAttemptId(active.id);
        const existing = await withSession((token) =>
          authenticatedApi.getTestAttempt(active.id, token),
        );
        setAnswers(
          Object.fromEntries(
            existing.answers
              .filter((answer) => answer.option_id)
              .map((answer) => [answer.question_id, answer.option_id as string]),
          ),
        );
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load this practice test.");
    } finally {
      setLoading(false);
    }
  }, [testId, withSession]);
  useEffect(() => {
    void load();
  }, [load]);
  async function start() {
    setBusy(true);
    setError("");
    try {
      const started = await withSession((token) => authenticatedApi.startTest(testId, token));
      setAttemptId(started.attempt_id);
      setTest(started.test);
      setMessage("Your attempt is ready. Answers are saved as you choose them.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to start this test.");
    } finally {
      setBusy(false);
    }
  }
  async function choose(questionId: string, optionId: string) {
    if (!attemptId) return;
    setAnswers((current) => ({ ...current, [questionId]: optionId }));
    setError("");
    try {
      await withSession((token) =>
        authenticatedApi.saveTestAnswer(attemptId, questionId, optionId, token),
      );
      setMessage("Answer saved.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to save your answer.");
    }
  }
  async function submit() {
    if (!attemptId) return;
    setBusy(true);
    setError("");
    try {
      setResult(await withSession((token) => authenticatedApi.submitTest(attemptId, token)));
      setAttemptId("");
      setMessage("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to submit your test.");
    } finally {
      setBusy(false);
    }
  }
  if (loading)
    return (
      <main className="mx-auto max-w-4xl px-5 py-12" aria-live="polite">
        Loading practice test…
      </main>
    );
  if (error && !test)
    return (
      <AccountError title="Practice test unavailable" message={error} retry={() => void load()} />
    );
  if (!test) return null;
  return (
    <main className="mx-auto max-w-4xl px-5 py-12 lg:px-8">
      <Link href="/tests" className="text-sm font-semibold text-[#145b48]">
        ← Back to practice tests
      </Link>
      <p className="mt-6 text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">
        {test.duration_minutes} minutes
      </p>
      <h1 className="mt-2 text-4xl font-semibold tracking-tight">{test.title}</h1>
      {test.description && <p className="mt-3 leading-7 text-[#63736c]">{test.description}</p>}
      {result ? (
        <section className="mt-8 rounded-2xl border border-[#e3e9e4] bg-white p-7" role="status">
          <h2 className="text-2xl font-semibold">Attempt submitted</h2>
          <p className="mt-2 text-[#63736c]">
            Score: {result.score} of {result.total_questions}
          </p>
          <Link
            href="/dashboard"
            className="mt-5 inline-flex font-semibold text-[#145b48] underline"
          >
            View your dashboard
          </Link>
        </section>
      ) : !attemptId ? (
        <section className="mt-8 rounded-2xl border border-[#e3e9e4] bg-white p-7">
          <p className="text-[#63736c]">
            This test has {test.questions.length} questions. Start when you’re ready; your attempt
            will be tied to your account.
          </p>
          <button
            disabled={busy}
            onClick={() => void start()}
            className="mt-5 rounded-xl bg-[#145b48] px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
          >
            {busy ? "Starting…" : "Start or continue test"}
          </button>
        </section>
      ) : (
        <div className="mt-8 space-y-4">
          {test.questions.map((question, index) => (
            <fieldset
              key={question.id}
              className="rounded-2xl border border-[#e3e9e4] bg-white p-6"
            >
              <legend className="px-1 font-semibold">
                {index + 1}. {question.text}
              </legend>
              <div className="mt-4 grid gap-2">
                {question.options.map((option) => (
                  <label
                    key={option.id}
                    className="flex cursor-pointer items-start gap-3 rounded-xl border border-[#e3e9e4] p-3 hover:bg-[#f7f8f4]"
                  >
                    <input
                      type="radio"
                      name={question.id}
                      value={option.id}
                      checked={answers[question.id] === option.id}
                      onChange={() => void choose(question.id, option.id)}
                      className="mt-1 accent-[#145b48]"
                    />
                    <span>{option.text}</span>
                  </label>
                ))}
              </div>
            </fieldset>
          ))}
          <button
            disabled={busy}
            onClick={() => void submit()}
            className="rounded-xl bg-[#145b48] px-5 py-3 text-sm font-semibold text-white disabled:opacity-60"
          >
            {busy ? "Submitting…" : "Submit attempt"}
          </button>
        </div>
      )}
      {error && (
        <p role="alert" className="mt-4 rounded-xl bg-red-50 p-4 text-sm text-red-800">
          {error}
        </p>
      )}
      {message && (
        <p role="status" className="mt-4 text-sm text-[#42634e]">
          {message}
        </p>
      )}
    </main>
  );
}

export function SavedPage() {
  const { withSession } = useAuth();
  const [items, setItems] = useState<ResolvedBookmark[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const saved = await withSession((token) => authenticatedApi.listBookmarks(token));
      const resolved = await Promise.all(
        saved.map(async (item): Promise<ResolvedBookmark> => {
          try {
            if (item.entity_type === "exam") {
              const record = await authenticatedApi.getExam(item.entity_id);
              return { ...item, title: record.name, href: `/exams/${record.slug}` };
            }
            if (item.entity_type === "course") {
              const record = await authenticatedApi.getCourse(item.entity_id);
              return { ...item, title: record.title, href: `/courses/${record.id}` };
            }
            if (item.entity_type === "current_affair") {
              const record = await authenticatedApi.getCurrentAffair(item.entity_id);
              return { ...item, title: record.title, href: `/current-affairs/${record.id}` };
            }
            const record = await authenticatedApi.getOpportunity(item.entity_id);
            const base =
              item.entity_type === "internship"
                ? "/internships"
                : item.entity_type === "scholarship"
                  ? "/scholarships"
                  : item.entity_type === "competition"
                    ? "/competitions"
                    : "/jobs";
            return { ...item, title: record.title, href: `${base}/${record.slug}` };
          } catch {
            return item;
          }
        }),
      );
      setItems(resolved);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to load saved items.");
    } finally {
      setLoading(false);
    }
  }, [withSession]);
  useEffect(() => {
    void load();
  }, [load]);
  async function remove(id: string) {
    await withSession((token) => authenticatedApi.deleteBookmark(id, token));
    setItems((current) => current.filter((item) => item.id !== id));
  }
  if (loading)
    return (
      <main className="mx-auto max-w-4xl px-5 py-12" aria-live="polite">
        Loading saved items…
      </main>
    );
  if (error)
    return (
      <AccountError title="Saved items unavailable" message={error} retry={() => void load()} />
    );
  return (
    <main className="mx-auto max-w-4xl px-5 py-12 lg:px-8">
      <p className="text-xs font-bold uppercase tracking-[.16em] text-[#668b59]">Your account</p>
      <h1 className="mt-3 text-4xl font-semibold tracking-tight">Saved items</h1>
      <p className="mt-3 text-[#63736c]">Items saved to your Elevra account.</p>
      {items.length ? (
        <ul className="mt-8 divide-y divide-[#edf0ec] rounded-2xl border border-[#e3e9e4] bg-white px-5">
          {items.map((item) => (
            <li key={item.id} className="flex flex-wrap items-center justify-between gap-3 py-4">
              <div>
                {item.href ? (
                  <Link
                    href={item.href as Route}
                    className="font-semibold text-[#145b48] underline underline-offset-4"
                  >
                    {item.title}
                  </Link>
                ) : (
                  <p className="font-semibold">{item.title || "Saved listing unavailable"}</p>
                )}
                <p className="mt-1 text-xs capitalize text-[#63736c]">
                  {item.entity_type.replaceAll("_", " ")}
                </p>
                <p className="mt-1 text-xs text-[#63736c]">Record ID: {item.entity_id}</p>
              </div>
              <button
                onClick={() =>
                  void remove(item.id).catch((cause) =>
                    setError(
                      cause instanceof Error ? cause.message : "Unable to remove saved item.",
                    ),
                  )
                }
                className="text-sm font-semibold text-[#145b48] underline underline-offset-4"
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <div className="mt-8 rounded-2xl border border-dashed border-[#cbd8ce] bg-white p-8 text-center">
          <p className="font-semibold">No saved items yet.</p>
          <Link href="/explore" className="mt-4 inline-flex text-sm font-semibold text-[#145b48]">
            Explore opportunities →
          </Link>
        </div>
      )}
      {error && (
        <p role="alert" className="mt-4 text-sm text-red-700">
          {error}
        </p>
      )}
    </main>
  );
}

export function OpportunityAccountActions({
  item,
  isExam,
}: {
  item: Exam | Opportunity;
  isExam: boolean;
}) {
  const pathname = usePathname();
  const { status, withSession } = useAuth();
  const [bookmarkId, setBookmarkId] = useState("");
  const [tracked, setTracked] = useState(false);
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const opportunity = item as Opportunity;
  const bookmarkType = isExam
    ? "exam"
    : opportunity.type === "hackathon"
      ? "competition"
      : opportunity.type;
  const canBookmark = ["exam", "job", "internship", "scholarship", "competition"].includes(
    bookmarkType,
  );

  useEffect(() => {
    if (status !== "authenticated") return;
    void withSession((token) => authenticatedApi.listBookmarks(token))
      .then((bookmarks) => {
        const match = bookmarks.find(
          (bookmark) => bookmark.entity_type === bookmarkType && bookmark.entity_id === item.id,
        );
        setBookmarkId(match?.id || "");
      })
      .catch((cause) =>
        setError(cause instanceof Error ? cause.message : "Unable to check saved status."),
      );
    if (!isExam) {
      void withSession((token) => authenticatedApi.listApplications(token))
        .then((applications) => {
          setTracked(applications.some((application) => application.opportunity_id === item.id));
        })
        .catch((cause) =>
          setError(
            cause instanceof Error ? cause.message : "Unable to check application tracking.",
          ),
        );
    }
  }, [bookmarkType, isExam, item.id, status, withSession]);

  if (status !== "authenticated") {
    return (
      <Link
        href={`/login?next=${encodeURIComponent(pathname)}`}
        className="rounded-xl border border-[#d8e1da] px-4 py-2 text-sm font-semibold text-[#28483b]"
      >
        Sign in to save or track
      </Link>
    );
  }

  async function toggleBookmark() {
    setBusy("bookmark");
    setError("");
    setMessage("");
    try {
      if (bookmarkId) {
        await withSession((token) => authenticatedApi.deleteBookmark(bookmarkId, token));
        setBookmarkId("");
        setMessage("Removed from saved items.");
      } else {
        const bookmark = await withSession((token) =>
          authenticatedApi.createBookmark(bookmarkType, item.id, token),
        );
        setBookmarkId(bookmark.id);
        setMessage("Saved to your account.");
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to update saved items.");
    } finally {
      setBusy("");
    }
  }

  async function trackApplication() {
    setBusy("application");
    setError("");
    setMessage("");
    try {
      await withSession((token) =>
        authenticatedApi.createApplication(
          {
            opportunity_id: item.id,
            title: opportunity.title,
            organization: opportunity.organization,
            external_url: opportunity.application_url,
            status: "saved",
          },
          token,
        ),
      );
      setTracked(true);
      setMessage("Added to your application tracker as saved.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to track this opportunity.");
    } finally {
      setBusy("");
    }
  }

  return (
    <div className="flex flex-wrap gap-3">
      <button
        disabled={!canBookmark || busy !== ""}
        onClick={() => void toggleBookmark()}
        title={
          canBookmark
            ? undefined
            : "Saving this opportunity type is not supported by the account API."
        }
        className="rounded-xl border border-[#d8e1da] px-4 py-2 text-sm font-semibold text-[#28483b] disabled:opacity-60"
      >
        {busy === "bookmark" ? "Saving…" : bookmarkId ? "Saved" : "Save"}
      </button>
      {!isExam && (
        <button
          disabled={tracked || busy !== ""}
          onClick={() => void trackApplication()}
          className="rounded-xl border border-[#d8e1da] px-4 py-2 text-sm font-semibold text-[#28483b] disabled:opacity-60"
        >
          {tracked
            ? "In application tracker"
            : busy === "application"
              ? "Adding…"
              : "Track application"}
        </button>
      )}
      {(message || error) && (
        <p
          className={`w-full text-sm ${error ? "text-red-700" : "text-[#42634e]"}`}
          role={error ? "alert" : "status"}
        >
          {error || message}
        </p>
      )}
    </div>
  );
}

function AccountError({
  title,
  message,
  retry,
}: {
  title: string;
  message: string;
  retry: () => void;
}) {
  return (
    <main className="mx-auto max-w-4xl px-5 py-12">
      <section className="rounded-2xl border border-[#e3e9e4] bg-white p-7">
        <h1 className="text-2xl font-semibold">{title}</h1>
        <p className="mt-2 text-sm text-[#63736c]">{message}</p>
        <button
          onClick={retry}
          className="mt-5 rounded-xl bg-[#145b48] px-5 py-3 text-sm font-semibold text-white"
        >
          Try again
        </button>
      </section>
    </main>
  );
}
