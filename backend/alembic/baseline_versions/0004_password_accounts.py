from alembic import op
import sqlalchemy as sa

revision = "0004_password_accounts"
down_revision = "0003_user_oauth_threads"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE users SET email = lower(trim(email))")
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.add_column("users", sa.Column("password_hash", sa.String(512), nullable=True))
    op.add_column("users", sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("verification_hash", sa.String(64), nullable=True))
    op.add_column("users", sa.Column("verification_expires_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    for column in ("verification_expires_at", "verification_hash", "email_verified_at", "password_hash"):
        op.drop_column("users", column)
    op.drop_constraint("uq_users_email", "users", type_="unique")
