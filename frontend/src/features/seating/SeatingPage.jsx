import { useState } from "react";
import { Plus, Trash2, Wand2 } from "lucide-react";
import PageWrapper from "../../components/layout/PageWrapper";
import Card, { CardHeader } from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Badge from "../../components/ui/Badge";
import api from "../../lib/apiClient";
import { useToast } from "../../context/ToastContext";

const emptyRow = () => ({ name: "", roll_number: "", height_cm: "", front_row_required: false });

export default function SeatingPage() {
  const { push } = useToast();
  const [roster, setRoster] = useState([emptyRow(), emptyRow(), emptyRow(), emptyRow()]);
  const [rows, setRows] = useState(3);
  const [cols, setCols] = useState(3);
  const [podium, setPodium] = useState("0,0");
  const [kuddusSeat, setKuddusSeat] = useState("2,2");
  const [aisleColumns, setAisleColumns] = useState("");
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const updateRow = (i, field, value) => {
    setRoster((r) => r.map((row, idx) => (idx === i ? { ...row, [field]: value } : row)));
  };

  const addRow = () => setRoster((r) => [...r, emptyRow()]);
  const removeRow = (i) => setRoster((r) => r.filter((_, idx) => idx !== i));

  const parsePair = (str) => str.split(",").map((n) => parseInt(n.trim(), 10));

  const submit = async () => {
    const validRoster = roster.filter((r) => r.name && r.roll_number && r.height_cm);
    if (validRoster.length === 0) {
      push({ type: "error", message: "Add at least one complete roster row." });
      return;
    }

    setSubmitting(true);
    try {
      const { data } = await api.post("/seating/generate", {
        roster: validRoster.map((r) => ({
          name: r.name,
          roll_number: r.roll_number,
          height_cm: Number(r.height_cm),
          constraints: r.front_row_required ? { front_row_required: true, reason: "manual" } : null,
        })),
        rows: Number(rows),
        cols: Number(cols),
        podium_position: parsePair(podium),
        kuddus_seat: parsePair(kuddusSeat),
        aisle_columns: aisleColumns
          .split(",")
          .map((n) => n.trim())
          .filter(Boolean)
          .map(Number),
      });
      setResult(data);
      push({ type: "success", message: "Seating chart generated." });
    } catch (err) {
      push({ type: "error", message: err.response?.data?.detail?.[0]?.msg || "Could not generate seating chart." });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <PageWrapper maxWidth="max-w-4xl">
      <h1 className="font-display text-2xl font-extrabold mb-1">Anti-Camouflage Seat Planner</h1>
      <p className="text-ink-soft mb-6">
        Generate a seating chart that maximizes sightline to the podium, front-to-back.
      </p>

      <Card className="mb-6">
        <CardHeader title="Grid setup" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
          <Input label="Rows" type="number" min="1" value={rows} onChange={(e) => setRows(e.target.value)} />
          <Input label="Columns" type="number" min="1" value={cols} onChange={(e) => setCols(e.target.value)} />
          <Input label="Podium (row,col)" value={podium} onChange={(e) => setPodium(e.target.value)} />
          <Input label="Kuddus's seat (row,col)" value={kuddusSeat} onChange={(e) => setKuddusSeat(e.target.value)} />
        </div>
        <Input
          label="Aisle columns (comma-separated, optional)"
          value={aisleColumns}
          onChange={(e) => setAisleColumns(e.target.value)}
          placeholder="e.g. 1"
        />
      </Card>

      <Card className="mb-6">
        <CardHeader
          title="Roster"
          action={
            <Button variant="ghost" size="sm" icon={Plus} onClick={addRow}>
              Add row
            </Button>
          }
        />
        <div className="flex flex-col gap-3">
          {roster.map((r, i) => (
            <div key={i} className="grid grid-cols-[1fr_1fr_90px_auto_auto] gap-2 items-center">
              <input
                className="rounded-lg border-2 border-primary-100 px-3 py-1.5 text-sm focus:border-primary-500 focus:outline-none"
                placeholder="Name"
                value={r.name}
                onChange={(e) => updateRow(i, "name", e.target.value)}
              />
              <input
                className="rounded-lg border-2 border-primary-100 px-3 py-1.5 text-sm focus:border-primary-500 focus:outline-none"
                placeholder="Roll"
                value={r.roll_number}
                onChange={(e) => updateRow(i, "roll_number", e.target.value)}
              />
              <input
                className="rounded-lg border-2 border-primary-100 px-3 py-1.5 text-sm focus:border-primary-500 focus:outline-none"
                placeholder="Height cm"
                type="number"
                value={r.height_cm}
                onChange={(e) => updateRow(i, "height_cm", e.target.value)}
              />
              <label className="flex items-center gap-1.5 text-xs text-ink-soft whitespace-nowrap">
                <input
                  type="checkbox"
                  checked={r.front_row_required}
                  onChange={(e) => updateRow(i, "front_row_required", e.target.checked)}
                />
                Front row
              </label>
              <button onClick={() => removeRow(i)} aria-label="Remove row" className="text-danger-500 hover:text-danger-700">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </Card>

      <Button icon={Wand2} loading={submitting} onClick={submit} className="w-full mb-8">
        Generate seating chart
      </Button>

      {result && (
        <Card>
          <CardHeader
            title="Generated layout"
            action={<Badge tone="success">Sightline score {(result.average_sightline_score * 100).toFixed(0)}%</Badge>}
          />
          <div className="overflow-x-auto">
            <div className="inline-grid gap-1.5" style={{ gridTemplateColumns: `repeat(${cols}, minmax(80px, 1fr))` }}>
              {result.grid.flat().map((seat, i) => (
                <div
                  key={i}
                  className={`rounded-lg p-2 text-xs text-center border-2 ${
                    seat.is_aisle
                      ? "border-dashed border-primary-100 bg-transparent"
                      : seat.sightline_blocked
                      ? "border-danger-500 bg-danger-50"
                      : seat.student_name
                      ? "border-primary-200 bg-primary-50"
                      : "border-primary-100 bg-paper-soft"
                  }`}
                >
                  {seat.is_aisle ? (
                    <span className="text-ink-faint">aisle</span>
                  ) : seat.student_name ? (
                    <>
                      <p className="font-semibold truncate">{seat.student_name}</p>
                      <p className="text-ink-faint">{seat.height_cm}cm</p>
                    </>
                  ) : (
                    <span className="text-ink-faint">empty</span>
                  )}
                </div>
              ))}
            </div>
          </div>
          {result.notes.length > 0 && (
            <ul className="mt-4 text-xs text-ink-soft list-disc list-inside space-y-1">
              {result.notes.map((n, i) => (
                <li key={i}>{n}</li>
              ))}
            </ul>
          )}
        </Card>
      )}
    </PageWrapper>
  );
}
