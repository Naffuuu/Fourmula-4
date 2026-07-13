import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Plus } from "lucide-react";
import PageWrapper from "../../components/layout/PageWrapper";
import Card, { CardHeader } from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Modal from "../../components/ui/Modal";
import api from "../../lib/apiClient";
import { useToast } from "../../context/ToastContext";

export default function LedgerPage() {
  const { push } = useToast();
  const [summary, setSummary] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [type, setType] = useState("cash");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    const { data } = await api.get("/ledger");
    setSummary(data);
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();

    const parsedAmount = Number(amount);
    if (!parsedAmount || parsedAmount <= 0) {
      push({ type: "error", message: "Enter a positive amount or item count." });
      return;
    }

    if (!description.trim()) {
      push({ type: "error", message: "Add a description for the entry." });
      return;
    }

    const normalizedAmount = type === "food" ? Math.max(1, Math.round(parsedAmount)) : parsedAmount;

    setSubmitting(true);
    try {
      await api.post("/ledger", {
        type,
        amount: normalizedAmount,
        item_description: description.trim(),
      });
      setAmount("");
      setDescription("");
      setModalOpen(false);
      push({ type: "success", message: "Entry logged." });
      load();
    } catch (err) {
      const detail = err?.response?.data?.detail;
      const message = Array.isArray(detail) ? detail[0]?.msg || detail[0] : detail || "Could not log entry.";
      push({ type: "error", message });
    } finally {
      setSubmitting(false);
    }
  };

  const chartData = summary?.entries
    ?.slice()
    .reverse()
    .map((e, i) => ({ index: i + 1, amount: e.type === "cash" ? e.amount : 0 })) || [];

  return (
    <PageWrapper maxWidth="max-w-3xl">
      <div className="flex items-center justify-between mb-1">
        <h1 className="font-display text-2xl font-extrabold">Corrupt Economy & Tiffin Ledger</h1>
      </div>
      <p className="text-ink-soft mb-6">Anonymous ledger of forced payments and stolen food.</p>

      <Button icon={Plus} onClick={() => setModalOpen(true)} className="mb-6">
        Log an entry
      </Button>

      {summary && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <StatCard label="Total cash taken" value={`৳${summary.total_cash.toFixed(0)}`} />
            <StatCard label="Food items stolen" value={summary.total_food_items} />
            <StatCard label="= Jhalmuri packets" value={summary.cash_in_jhalmuri_packets} />
            <StatCard label="= Cricket bats" value={summary.cash_in_cricket_bats} />
          </div>

          <Card className="mb-6">
            <CardHeader title="Cash-taken over time" />
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E0E1FD" />
                  <XAxis dataKey="index" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="amount" stroke="#FF6B57" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card>
            <CardHeader title="Entries" />
            <div className="divide-y divide-primary-50">
              {summary.entries.map((e) => (
                <div key={e.id} className="py-2.5 flex justify-between text-sm">
                  <span className="text-ink-soft">{e.item_description}</span>
                  <span className="font-semibold">
                    {e.type === "cash" ? `৳${e.amount.toFixed(0)}` : `${e.amount}x item`}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Log a ledger entry" size="sm">
        <form onSubmit={submit} className="flex flex-col gap-4">
          <div className="grid grid-cols-2 gap-2">
            {["cash", "food"].map((t) => (
              <button
                type="button"
                key={t}
                onClick={() => setType(t)}
                className={`rounded-xl border-2 px-3 py-2 text-sm font-semibold capitalize ${
                  type === t ? "border-primary-500 bg-primary-50 text-primary-700" : "border-primary-100 text-ink-soft"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
          <Input
            label={type === "cash" ? "Amount (BDT)" : "Item count"}
            type="number"
            step={type === "cash" ? "0.01" : "1"}
            min={1}
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
          <Input label="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
          <Button type="submit" loading={submitting} className="w-full">
            Log entry
          </Button>
        </form>
      </Modal>
    </PageWrapper>
  );
}

function StatCard({ label, value }) {
  return (
    <Card padding="p-4">
      <p className="font-display text-xl font-extrabold text-coral-600">{value}</p>
      <p className="text-xs text-ink-faint font-medium uppercase tracking-wide mt-1">{label}</p>
    </Card>
  );
}
