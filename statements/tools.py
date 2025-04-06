import csv

from django.db import transaction
from django.core.exceptions import ValidationError
from statements.models import Account, Statement, StatementItem

def statement_import(file_handler):
    idx = 0
    # TODO: TASK → in case of errors database must not change
    # TODO: TASK → optimize database queries during import

    statements_items = []

    # I decided to use transaction.atomic() to ensure that every maked change in database is valid, I am fully
    # aware of it memeory usage, when dealing with large inputs, but it's not that bad in compare with safety of this solution
    try:
        with transaction.atomic():
            for row in csv.DictReader(file_handler):
                account = Account.objects.get_or_create(
                    name=row['account'],
                    defaults={'currency': row['currency']}
                )[0]

                if account.currency != row['currency']:
                    raise ValidationError(f'Invalid currency {row['currency']} for account: {row['account']}')

                statement = Statement.objects.get_or_create(
                    account=account,
                    date=row['date']
                )[0]

                item = StatementItem(
                    statement=statement,
                    amount=row['amount'],
                    currency=row['currency'],
                    title=row.get('title', ''),
                    comments=row.get('comments', ''),
                )
                
                item.full_clean()
                statements_items.append(item)

                idx += 1
    except KeyError as kerr:
        raise KeyError(f"Error at {file_handler.name}, row: {idx + 1}: {kerr}")
    except ValidationError as verr:
        raise ValidationError(f"Error at {file_handler.name}, row: {idx + 1}: {verr}")
    except Exception as e:
        raise Exception(f"Error at {file_handler.name}, row: {idx + 1}: {e}")

    StatementItem.objects.bulk_create(statements_items, batch_size=1000)

    return idx

