"""pos_l10n_mx_diot

Revision ID: pos_l10n_mx_diot
Revises:
Create Date: 2015-11-2 12:40:31.791194

"""

# revision identifiers, used by Alembic.
revision = 'pos_l10n_mx_diot'
down_revision = 'pos_l10n_mx_account_tax'
branch_labels = None
depends_on = None

from alembic import op
from sqlalchemy.sql import table, column, update, text
from sqlalchemy import Integer, Boolean

conn = op.get_bind()


def upgrade():
    account_move = table(
        'account_move',
        column('id', Integer),
        column('use_in_diot', Boolean),
    )
    update_account_move = account_move.update().values(
        use_in_diot=True
    )
    conn.execute(update_account_move)

    conn.execute(text(
        """
        UPDATE account_move_line
           SET tax2_id = (
                SELECT id from account_tax
                where account_tax.account_reconcile_id =
                account_move_line.account_id and
                account_tax.account_reconcile_id IS NOT NULL
                LIMIT 1
           )
        """
    ))


def downgrade():
    # TODO: Write this funcition
    pass
