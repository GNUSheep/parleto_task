from django.db import models, connection
from collections import defaultdict

def report_turnover_by_year_month(period_begin: str, period_end: str):
    # period_begin and period_end format "YYYY-MM-DD" 

    # TODO: TASK → make report using 1 database query without any math in python

    report = defaultdict(lambda: {"incomes": defaultdict(float), "expenses": defaultdict(float)})

    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT 
                    strftime('%Y-%m', statement.date) AS year_month,
                    item.currency,
                    SUM(CASE WHEN item.amount > 0 THEN item.amount ELSE 0 END) AS incomes,
                    SUM(CASE WHEN item.amount < 0 THEN -1 * item.amount ELSE 0 END) AS expenses
                FROM statements_statementitem item
                JOIN statements_statement statement ON item.statement_id = statement.id
                WHERE statement.date BETWEEN '{}' AND '{}'
                GROUP BY 
                    year_month, item.currency
                ORDER BY 
                    year_month, item.currency
            """.format(period_begin, period_end))

            r = cur.fetchall()

            for (date, currency, income, expenses) in r:
                income = float(income or 0)
                expenses = float(expenses or 0)

                report[date]['incomes'][currency] = income
                report[date]['expenses'][currency] = expenses
    except Exception as e:
        raise Exception(f'Error while trying to create an report from {period_begin} to {period_end}: {e}')

    return dict(report)

class Account(models.Model):
    name = models.CharField(max_length=100)
    currency = models.CharField(max_length=3)
    # TODO: TASK → add field balance that will update automatically 
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}[{self.currency}], balance → {self.balance}'


class Statement(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    date = models.DateField()
    # TODO: TASK → make sure that account and date is unique on database level

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["account", "date"],
                name="unique_statement"
            )
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.account} → {self.date}'
    

class StatementItem(models.Model):
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3)
    title = models.CharField(max_length=100)
    # TODO:  TASK → add field comments (type text)
    comments = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)    

    def __str__(self):
        return f'[{self.statement}] {self.amount} {self.currency} → {self.title} {self.comments}'
