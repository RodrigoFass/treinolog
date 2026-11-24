"""adiciona nutricionista, plano alimentar e peso

Revision ID: d7b1f1a5ee64
Revises: 467b55e00931
Create Date: 2026-11-23 22:12:35.368426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7b1f1a5ee64'
down_revision = '467b55e00931'
branch_labels = None
depends_on = None


def upgrade():
    # Perfil de nutricionista, vinculo aluno -> nutricionista,
    # plano alimentar, refeicoes marcadas e peso do aluno
    op.create_table('meal_plans',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nutritionist_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.Column('goal', sa.String(length=120), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['nutritionist_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('meal_plans', schema=None) as batch_op:
        batch_op.create_index('ix_meal_plans_student_active', ['student_id', 'is_active'], unique=False)

    op.create_table('weight_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('day', sa.Date(), nullable=False),
    sa.Column('weight_kg', sa.Numeric(precision=5, scale=2, asdecimal=False), nullable=False),
    sa.CheckConstraint('weight_kg > 0 AND weight_kg < 400', name='ck_weight_logs_weight'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id', 'day', name='uq_weight_logs_student_day')
    )
    op.create_table('meals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('plan_id', sa.Integer(), nullable=False),
    sa.Column('position', sa.SmallInteger(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.Column('time', sa.String(length=5), nullable=True),
    sa.Column('foods', sa.Text(), nullable=False),
    sa.Column('kcal', sa.SmallInteger(), nullable=True),
    sa.CheckConstraint('kcal IS NULL OR kcal BETWEEN 0 AND 5000', name='ck_meals_kcal'),
    sa.ForeignKeyConstraint(['plan_id'], ['meal_plans.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('plan_id', 'position', name='uq_meals_plan_position')
    )
    op.create_table('meal_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('meal_id', sa.Integer(), nullable=False),
    sa.Column('day', sa.Date(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['meal_id'], ['meals.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id', 'meal_id', 'day', name='uq_meal_logs_student_meal_day')
    )
    with op.batch_alter_table('meal_logs', schema=None) as batch_op:
        batch_op.create_index('ix_meal_logs_student_day', ['student_id', 'day'], unique=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nutritionist_id', sa.Integer(), nullable=True))
        batch_op.alter_column('role',
               existing_type=sa.Enum('personal', 'aluno', name='user_role', create_constraint=True),
               type_=sa.Enum('personal', 'aluno', 'nutricionista', name='user_role', create_constraint=True),
               existing_nullable=False)
        batch_op.create_foreign_key('fk_users_nutritionist_id', 'users', ['nutritionist_id'], ['id'], ondelete='SET NULL')



def downgrade():
    # Perfil de nutricionista, vinculo aluno -> nutricionista,
    # plano alimentar, refeicoes marcadas e peso do aluno
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_nutritionist_id', type_='foreignkey')
        batch_op.alter_column('role',
               existing_type=sa.Enum('personal', 'aluno', 'nutricionista', name='user_role', create_constraint=True),
               type_=sa.Enum('personal', 'aluno', name='user_role', create_constraint=True),
               existing_nullable=False)
        batch_op.drop_column('nutritionist_id')

    with op.batch_alter_table('meal_logs', schema=None) as batch_op:
        batch_op.drop_index('ix_meal_logs_student_day')

    op.drop_table('meal_logs')
    op.drop_table('meals')
    op.drop_table('weight_logs')
    with op.batch_alter_table('meal_plans', schema=None) as batch_op:
        batch_op.drop_index('ix_meal_plans_student_active')

    op.drop_table('meal_plans')
