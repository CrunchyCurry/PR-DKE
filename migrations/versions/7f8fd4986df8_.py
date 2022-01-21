"""empty message

Revision ID: 7f8fd4986df8
Revises: 9d42cd78c4a1
Create Date: 2022-01-18 07:56:30.120387

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f8fd4986df8'
down_revision = '9d42cd78c4a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('railway', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['starts_at', 'ends_at'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('railway', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###