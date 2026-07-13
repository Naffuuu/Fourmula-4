from app.services.seating_algorithm import generate_seating


def make_roster(n, base_height=150):
    return [
        {"name": f"Student {i}", "roll_number": f"R{i}", "height_cm": base_height + i * 2, "constraints": None}
        for i in range(n)
    ]


def test_basic_grid_places_every_student():
    roster = make_roster(6)
    plan = generate_seating(
        roster=roster, rows=3, cols=2, podium_position=(0, 0), kuddus_seat=(2, 1), aisle_columns=[]
    )
    placed_names = {
        cell["student_name"] for row in plan.grid for cell in row if cell["student_name"]
    }
    assert placed_names == {s["name"] for s in roster}


def test_column_heights_are_non_decreasing_front_to_back():
    roster = make_roster(9)
    plan = generate_seating(
        roster=roster, rows=3, cols=3, podium_position=(0, 0), kuddus_seat=(2, 2), aisle_columns=[]
    )
    for col in range(3):
        heights = [
            plan.grid[row][col]["height_cm"]
            for row in range(3)
            if plan.grid[row][col]["height_cm"] is not None
        ]
        assert heights == sorted(heights)


def test_front_row_required_student_is_pinned_regardless_of_height():
    roster = make_roster(6, base_height=140)
    # Make the tallest student require the front row despite their height.
    roster[-1]["height_cm"] = 200
    roster[-1]["constraints"] = {"front_row_required": True, "reason": "vision"}

    plan = generate_seating(
        roster=roster, rows=3, cols=2, podium_position=(0, 0), kuddus_seat=(2, 1), aisle_columns=[]
    )
    front_row_names = {cell["student_name"] for cell in plan.grid[0]}
    assert roster[-1]["name"] in front_row_names


def test_aisle_columns_are_never_seated():
    roster = make_roster(4)
    plan = generate_seating(
        roster=roster, rows=2, cols=3, podium_position=(0, 0), kuddus_seat=(1, 2), aisle_columns=[1]
    )
    for row in plan.grid:
        assert row[1]["is_aisle"] is True
        assert row[1]["student_name"] is None


def test_oversized_roster_reports_unplaced_students_in_notes():
    roster = make_roster(20)
    plan = generate_seating(
        roster=roster, rows=2, cols=2, podium_position=(0, 0), kuddus_seat=(1, 1), aisle_columns=[]
    )
    assert any("unplaced" in note.lower() for note in plan.notes)
