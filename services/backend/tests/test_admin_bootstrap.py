from app.commands.bootstrap_admin import AdminBootstrapError, create_initial_admin
from app.models.user import User


def test_bootstrap_creates_first_admin_with_hashed_password(db):
    admin = create_initial_admin(
        db,
        name="Initial Admin",
        email="owner@example.com",
        password="StrongPassword123",
    )

    assert admin.role == "admin"
    assert admin.is_admin is True
    assert admin.is_active is True
    assert admin.email_verified is False
    assert admin.password_hash != "StrongPassword123"
    assert db.query(User).filter(User.id == admin.id).one().password_hash == admin.password_hash


def test_bootstrap_refuses_to_create_a_second_admin(db):
    db.add(
        User(
            name="Existing Admin",
            email="admin@example.com",
            password_hash="already-hashed",
            is_admin=True,
            role="admin",
            is_active=True,
        )
    )
    db.commit()

    try:
        create_initial_admin(
            db,
            name="Another Admin",
            email="another@example.com",
            password="StrongPassword123",
        )
    except AdminBootstrapError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("bootstrap must refuse when an admin exists")


def test_bootstrap_never_promotes_an_existing_student(db):
    db.add(
        User(
            name="Student",
            email="student@example.com",
            password_hash="already-hashed",
            is_admin=False,
            role="student",
            is_active=True,
        )
    )
    db.commit()

    try:
        create_initial_admin(
            db,
            name="Student",
            email="student@example.com",
            password="StrongPassword123",
        )
    except AdminBootstrapError as exc:
        assert "never promotes" in str(exc)
    else:
        raise AssertionError("bootstrap must not promote an existing account")


def test_bootstrap_rejects_weak_password_without_creating_user(db):
    try:
        create_initial_admin(
            db,
            name="Initial Admin",
            email="owner@example.com",
            password="weak",
        )
    except AdminBootstrapError as exc:
        assert "at least 12 characters" in str(exc).lower()
    else:
        raise AssertionError("bootstrap must reject weak passwords")

    assert db.query(User).count() == 0
