from app.services.anonymity_service import anonymize_submitter


def test_anonymize_submitter_is_deterministic():
    ref1 = anonymize_submitter("user-abc-123")
    ref2 = anonymize_submitter("user-abc-123")
    assert ref1 == ref2


def test_anonymize_submitter_different_users_differ():
    ref1 = anonymize_submitter("user-abc-123")
    ref2 = anonymize_submitter("user-xyz-789")
    assert ref1 != ref2


def test_anonymize_submitter_ref_does_not_contain_raw_user_id():
    user_id = "super-secret-user-id-42"
    ref = anonymize_submitter(user_id)
    assert user_id not in ref


def test_anonymize_submitter_ref_has_bucket_prefix():
    ref = anonymize_submitter("some-user")
    assert ref.startswith("b")
    bucket_part = ref.split("-")[0]
    assert bucket_part[1:].isdigit()
