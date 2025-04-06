import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('balance', models.DecimalField(max_digits=20, decimal_places=2, default=0)),
                ('currency', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Statement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='statements.account')),
            ],
        ),
        migrations.AddConstraint(
            model_name="statement",
            constraint=models.UniqueConstraint(
                fields=("account", "date"), 
                name="unique_statement"
            ),
        ),
        migrations.CreateModel(
            name='StatementItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('currency', models.CharField(max_length=3)),
                ('title', models.CharField(max_length=100)),
                ('comments', models.TextField(blank=True, null=True)),
                ('statement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='statements.statement')),
            ],
        ),
        migrations.RunSQL(
            """
            CREATE TRIGGER update_account_balance
            AFTER INSERT ON statements_statementitem
            FOR EACH ROW
            BEGIN
                UPDATE statements_account
                SET balance = balance + NEW.amount 
                WHERE id = (
                    SELECT account_id
                    FROM statements_statement
                    WHERE id = NEW.statement_id 
                );
            END;
            """
        )
    ]
