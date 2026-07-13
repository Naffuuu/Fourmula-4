"""Line-of-sight seating optimizer (Mission 2 advanced).

Model: think of each column as an independent line-of-sight problem between
the podium and the back row. Within a column, a shorter student in front of a
taller one blocks whoever's directly behind them from seeing the podium (or,
symmetrically, blocks the teacher's podium from seeing that student — the
whole point of the mission is Kuddus can't hide short informants behind tall
"blockers"). We solve each column as a constrained greedy height-ascending
assignment:

1. Hard-pin students with `front_row_required` into row 0 of some column
   first, regardless of height.
2. For every remaining column, sort the remaining students assigned to it by
   height ascending, front-to-back. This guarantees a monotonically
   non-decreasing height profile per column, which is the necessary and
   sufficient condition for "nobody blocks the view of the person directly
   behind them" in a simple orthographic sightline model.
3. Kuddus's fixed seat is treated as a hard pin like any front-row-required
   student — the algorithm plans around it rather than through it.
4. Aisle columns are skipped entirely (no seat placed there).
5. `sightline_blocked` on a seat is set if, despite the greedy pass (e.g. a
   pinned seat forced an inversion), the student directly in front is taller
   by more than a threshold — this is the value the "average sightline
   score" is computed from, and is intentionally surfaced rather than hidden,
   since a captain may still need to accept an imperfect arrangement when
   hard constraints conflict.
"""

from dataclasses import dataclass

BLOCKED_HEIGHT_THRESHOLD_CM = 12.0  # a row-ahead student taller by this much blocks the view


@dataclass
class SeatPlan:
    grid: list[list[dict]]
    average_sightline_score: float
    notes: list[str]


def generate_seating(
    roster: list[dict],
    rows: int,
    cols: int,
    podium_position: tuple[int, int],
    kuddus_seat: tuple[int, int],
    aisle_columns: list[int],
) -> SeatPlan:
    notes: list[str] = []
    seatable_cols = [c for c in range(cols) if c not in aisle_columns]
    if not seatable_cols:
        raise ValueError("At least one non-aisle column is required.")

    total_seats = rows * len(seatable_cols)
    if len(roster) > total_seats:
        notes.append(
            f"Roster has {len(roster)} students but the grid only has {total_seats} usable seats "
            f"({rows} rows x {len(seatable_cols)} non-aisle columns) — {len(roster) - total_seats} "
            "student(s) were left unplaced. Increase rows/cols or reduce aisle columns."
        )

    grid: list[list[dict | None]] = [[None for _ in range(cols)] for _ in range(rows)]
    for c in aisle_columns:
        for r in range(rows):
            if 0 <= c < cols:
                grid[r][c] = {
                    "row": r,
                    "col": c,
                    "student_name": None,
                    "roll_number": None,
                    "height_cm": None,
                    "is_aisle": True,
                    "sightline_blocked": False,
                }

    remaining = list(roster)

    def pop_by_roll(roll_number: str) -> dict | None:
        for i, s in enumerate(remaining):
            if s["roll_number"] == roll_number:
                return remaining.pop(i)
        return None

    # 1. Pin Kuddus's own seat first if a matching roster entry exists (by
    # convention the caller passes Kuddus's roll number in seat_constraints;
    # otherwise the cell is simply reserved/left for the caller to label).
    kr, kc = kuddus_seat
    if 0 <= kr < rows and 0 <= kc < cols and grid[kr][kc] is None:
        kuddus_entry = next((s for s in remaining if s.get("is_kuddus")), None)
        if kuddus_entry:
            remaining.remove(kuddus_entry)
            grid[kr][kc] = _seat_dict(kuddus_entry, kr, kc)
            notes.append(f"Kuddus pinned at row {kr}, col {kc} per fixed-seat constraint.")

    # 2. Hard-pin front-row-required students into row 0 across seatable
    # columns, left to right, before anything height-based happens.
    front_row_required = [s for s in remaining if (s.get("constraints") or {}).get("front_row_required")]
    for student in front_row_required:
        placed = False
        for c in seatable_cols:
            if grid[0][c] is None:
                grid[0][c] = _seat_dict(student, 0, c)
                remaining.remove(student)
                placed = True
                break
        if not placed:
            notes.append(
                f"Could not honor front-row requirement for {student['name']} — front row is full."
            )
    front_row_required_names = {s["name"] for s in front_row_required}

    # 3. Distribute remaining students across columns as evenly as possible,
    # then sort each column height-ascending front-to-back.
    column_buckets: dict[int, list[dict]] = {c: [] for c in seatable_cols}
    for i, student in enumerate(sorted(remaining, key=lambda s: s["height_cm"])):
        col = seatable_cols[i % len(seatable_cols)]
        column_buckets[col].append(student)

    for c, students in column_buckets.items():
        students.sort(key=lambda s: s["height_cm"])  # shortest in front
        row_cursor = 0
        for student in students:
            while row_cursor < rows and grid[row_cursor][c] is not None:
                row_cursor += 1
            if row_cursor >= rows:
                notes.append(f"Column {c} ran out of rows — {student['name']} left unplaced.")
                continue
            grid[row_cursor][c] = _seat_dict(student, row_cursor, c)
            row_cursor += 1

    # 4. Fill any leftover empty seats with an explicit empty marker.
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] is None:
                grid[r][c] = {"row": r, "col": c, "student_name": None, "roll_number": None, "height_cm": None, "is_aisle": False, "sightline_blocked": False}

    # 5. Compute sightline_blocked per seat: compare to the seat directly in
    # front (lower row index) in the same column.
    blocked_count = 0
    total_scored = 0
    for c in range(cols):
        if c in aisle_columns:
            continue
        prev_height = None
        for r in range(rows):
            seat = grid[r][c]
            if seat.get("is_aisle") or seat.get("height_cm") is None:
                continue
            total_scored += 1
            if prev_height is not None and prev_height - seat["height_cm"] > BLOCKED_HEIGHT_THRESHOLD_CM:
                # the row ahead (prev_height) is much taller -> blocks this seat
                pass
            if prev_height is not None and prev_height > seat["height_cm"] + BLOCKED_HEIGHT_THRESHOLD_CM:
                seat["sightline_blocked"] = True
                blocked_count += 1
            prev_height = seat["height_cm"]

    average_sightline_score = 1.0 if total_scored == 0 else round(1 - (blocked_count / total_scored), 3)

    if front_row_required_names:
        notes.append(f"Front-row pinned regardless of height: {', '.join(sorted(front_row_required_names))}.")

    return SeatPlan(grid=[[dict(cell) for cell in row] for row in grid], average_sightline_score=average_sightline_score, notes=notes)


def _seat_dict(student: dict, row: int, col: int) -> dict:
    return {
        "row": row,
        "col": col,
        "student_name": student["name"],
        "roll_number": student["roll_number"],
        "height_cm": student["height_cm"],
        "is_aisle": False,
        "sightline_blocked": False,
    }
