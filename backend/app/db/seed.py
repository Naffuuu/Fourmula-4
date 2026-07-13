"""Demo-ready seed data for local dev / hackathon presentation.

Run with:  docker-compose exec backend python -m app.db.seed

Idempotent: safe to run multiple times, skips rows that already exist by a
natural key (email for users, rule_text for rulebook entries) rather than
duplicating them on every run.
"""

import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.complaint import Complaint, ComplaintCategory, ComplaintStatus, Strike
from app.models.misc import LedgerEntry, LedgerEntryType, RulebookEntry, SosAlert, SosStatus
from app.models.user import User, UserRole

DEMO_PASSWORD = "Password123!"

DEMO_USERS = [
    {"name": "Rafi Student", "email": "rafi@demo.akp", "role": UserRole.student, "roll_number": "2201001"},
    {"name": "Biltu (2nd Captain)", "email": "biltu@demo.akp", "role": UserRole.second_captain, "roll_number": None},
    {"name": "Miltu (3rd Captain)", "email": "miltu@demo.akp", "role": UserRole.third_captain, "roll_number": None},
    {"name": "Rashid Sir", "email": "rashid@demo.akp", "role": UserRole.teacher, "roll_number": None},
]

RULEBOOK_ENTRIES = [
    ("Students may not be charged any fee for seating assignments; seating is allocated free of charge by roster height order unless a medical exemption is on file.", "Section 4.2 — Seating Policy"),
    ("No teacher or student leader may confiscate food brought from home without written parental consent and a logged disciplinary reason.", "Section 7.1 — Tiffin & Food Policy"),
    ("The examinable syllabus for any term must be published in full at least 30 days before the first test date; undisclosed topics may not be tested.", "Section 2.5 — Syllabus Disclosure"),
    ("Physical or extreme physical punishment for sports performance is prohibited under all circumstances.", "Section 9.3 — Sports Conduct"),
    ("Anonymous complaint channels must not be used to identify or retaliate against a submitter; retaliation is grounds for immediate escalation.", "Section 11.1 — Whistleblower Protection"),
    ("Cash collection from students for unofficial purposes (\"class funds\" not approved by administration) is prohibited without receipts and admin sign-off.", "Section 7.4 — Financial Conduct"),
]

LEDGER_SEED = [
    (LedgerEntryType.cash, 50.0, "Forced 'sports fund' contribution"),
    (LedgerEntryType.food, 1.0, "Confiscated tiffin — paratha & egg"),
    (LedgerEntryType.cash, 20.0, "Forced 'exam paper' contribution"),
    (LedgerEntryType.food, 1.0, "Confiscated tiffin — jhalmuri packet"),
]


async def seed():
    async with AsyncSessionLocal() as db:
        for u in DEMO_USERS:
            existing = (await db.execute(select(User).where(User.email == u["email"]))).scalar_one_or_none()
            if existing:
                continue
            from app.core.security import hash_roll_number

            db.add(
                User(
                    name=u["name"],
                    email=u["email"],
                    password_hash=hash_password(DEMO_PASSWORD),
                    role=u["role"],
                    roll_number_hash=hash_roll_number(u["roll_number"]) if u["roll_number"] else None,
                )
            )
        await db.flush()

        for text, section in RULEBOOK_ENTRIES:
            existing = (
                await db.execute(select(RulebookEntry).where(RulebookEntry.rule_text == text))
            ).scalar_one_or_none()
            if not existing:
                db.add(RulebookEntry(rule_text=text, source_section=section, embedding_vector=None))

        existing_complaints = (await db.execute(select(Complaint))).scalars().first()
        if not existing_complaints:
            from app.services.anonymity_service import anonymize_submitter

            c1 = Complaint(
                category=ComplaintCategory.tiffin_theft,
                description="Tiffin confiscated during class without reason given, no consent form on file.",
                anonymized_submitter_ref=anonymize_submitter("seed-user-1"),
                status=ComplaintStatus.resolved,
            )
            c2 = Complaint(
                category=ComplaintCategory.bribes,
                description="Asked to pay for 'extra marks' before the midterm.",
                anonymized_submitter_ref=anonymize_submitter("seed-user-2"),
                status=ComplaintStatus.open,
            )
            db.add_all([c1, c2])
            await db.flush()
            db.add(Strike(complaint_id=c1.id, warning_level=1))

        existing_ledger = (await db.execute(select(LedgerEntry))).scalars().first()
        if not existing_ledger:
            for t, amount, desc in LEDGER_SEED:
                db.add(LedgerEntry(type=t, amount=amount, item_description=desc))

        existing_sos = (await db.execute(select(SosAlert))).scalars().first()
        if not existing_sos:
            db.add(SosAlert(location="2nd Floor Corridor, Block B", status=SosStatus.resolved))

        await db.commit()
    print("Seed complete. Demo login: rafi@demo.akp / biltu@demo.akp / miltu@demo.akp / rashid@demo.akp")
    print(f"Password for all demo accounts: {DEMO_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
