import { useState } from "react";
import { Sparkles, CheckCircle2, XCircle } from "lucide-react";
import PageWrapper from "../../components/layout/PageWrapper";
import Card, { CardHeader } from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import api from "../../lib/apiClient";
import { useToast } from "../../context/ToastContext";

export default function SyllabusPage() {
  const { push } = useToast();
  const [rawText, setRawText] = useState("");
  const [testDate, setTestDate] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [plan, setPlan] = useState(null);

  const submit = async () => {
    if (rawText.trim().length < 20) {
      push({ type: "error", message: "Paste in more of the syllabus text (20+ characters)." });
      return;
    }
    if (!testDate) {
      push({ type: "error", message: "Pick the test date so the study plan can be time-blocked." });
      return;
    }
    setSubmitting(true);
    try {
      const { data } = await api.post("/syllabus", { raw_text: rawText, test_date: testDate });
      setPlan(data);
    } catch (err) {
      push({ type: "error", message: "Could not generate a study plan. Try again." });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <PageWrapper maxWidth="max-w-3xl">
      <h1 className="font-display text-2xl font-extrabold mb-1">Syllabus Negotiator</h1>
      <p className="text-ink-soft mb-6">
        Paste the bloated syllabus text — we'll filter it down to what's actually examinable and build a study plan.
      </p>

      <Card className="mb-6">
        <CardHeader title="Syllabus input" />
        <div className="flex flex-col gap-4">
          <textarea
            rows={8}
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            className="w-full rounded-xl border-2 border-primary-100 bg-paper-soft px-4 py-2.5 text-sm focus:border-primary-500 focus:bg-paper-card focus:outline-none"
            placeholder="Paste the raw syllabus text here..."
          />
          <Input label="Test date" type="date" value={testDate} onChange={(e) => setTestDate(e.target.value)} />
          <Button icon={Sparkles} loading={submitting} onClick={submit}>
            Negotiate syllabus
          </Button>
        </div>
      </Card>

      {plan && (
        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader title="Summary" />
            <ul className="list-disc list-inside text-sm text-ink-soft space-y-1">
              {plan.summary_bullets.map((b, i) => (
                <li key={i}>{b}</li>
              ))}
            </ul>
          </Card>

          <div className="grid sm:grid-cols-2 gap-6">
            <Card>
              <CardHeader title="Examinable" action={<CheckCircle2 className="w-5 h-5 text-success-500" />} />
              <ul className="text-sm text-ink-soft space-y-1.5">
                {plan.filtered_examinable_topics.map((t, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-success-500">•</span> {t}
                  </li>
                ))}
              </ul>
            </Card>
            <Card>
              <CardHeader title="Dropped (non-examinable)" action={<XCircle className="w-5 h-5 text-ink-faint" />} />
              <ul className="text-sm text-ink-faint space-y-1.5">
                {plan.dropped_non_examinable_topics.length === 0 ? (
                  <li>Nothing dropped.</li>
                ) : (
                  plan.dropped_non_examinable_topics.map((t, i) => (
                    <li key={i} className="flex gap-2 line-through">
                      {t}
                    </li>
                  ))
                )}
              </ul>
            </Card>
          </div>

          <Card>
            <CardHeader title="Study plan" subtitle="Time-blocked until your test date" />
            <div className="flex flex-col divide-y divide-primary-50">
              {plan.study_plan.map((day) => (
                <div key={day.date} className="py-3 flex items-start justify-between gap-4">
                  <div>
                    <p className="font-semibold text-sm">{day.date}</p>
                    <p className="text-sm text-ink-soft">{day.topics.join(", ")}</p>
                  </div>
                  <span className="text-xs font-semibold text-primary-600 whitespace-nowrap">
                    {day.estimated_hours}h
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </PageWrapper>
  );
}
