from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from django.db import transaction

from .gmail_service import fetch_bank_emails
from .expense_parser import parse_expense_from_email_llm
from ..models import Card, Expense, Category

def get_billing_cycle_dates(target_month_int, target_year_int, cut_off_day):
    """
    Given a target month/year and a cut_off_day, calculates:
    - End Date: cut_off_day of the target_month/year
    - Start Date: cut_off_day + 1 of the PREVIOUS month
    """
    # Create the end date first
    # Handle cases where cut_off_day is 31 but month has 30 days
    try:
        end_date = date(target_year_int, target_month_int, cut_off_day)
    except ValueError:
        # e.g., April 31st -> April 30th
        # Find the last day of the target month
        next_month = date(target_year_int, target_month_int, 1) + relativedelta(months=1)
        end_date = next_month - timedelta(days=1)
        
        # If the cut-off day was smaller than the last day, we wouldn't be here, 
        # so end_date is now correctly bounded to the end of the month
        if cut_off_day < end_date.day:
             end_date = end_date.replace(day=cut_off_day)

    # Start date is the cut_off_day + 1 of the previous month
    prev_month_date = end_date - relativedelta(months=1)
    
    # Safely try to get cut_off_day + 1
    start_day = cut_off_day + 1
    try:
        start_date = date(prev_month_date.year, prev_month_date.month, start_day)
    except ValueError:
        # It could be that cut_off_day was 31, +1 = 32 -> wrap to 1st of next month?
        # Actually if cut_off_day is the end of the month, start day is the 1st of the next month
        next_month_after_prev = prev_month_date + relativedelta(months=1)
        start_date = date(next_month_after_prev.year, next_month_after_prev.month, 1)
        
    return start_date, end_date

@transaction.atomic
def sync_card_expenses(card_id, target_month_int, target_year_int):
    """
    Main workflow for the email-agen sync.
    Fetches emails, parses them, and saves to the DB.
    """
    card = Card.objects.get(id=card_id)
    
    if not card.mail or not card.mail_subject:
        return 0, "Card is missing email or subject configuration."
        
    start_date, end_date = get_billing_cycle_dates(
        target_month_int, target_year_int, card.cut_off_day
    )
    
    emails = fetch_bank_emails(card.mail, card.mail_subject, start_date, end_date)
    
    if not emails:
        return 0, f"No emails found from {start_date} to {end_date}."
        
    # Get or create a default category for these synced expenses
    category, _ = Category.objects.get_or_create(
        user=card.user,
        name="Gastos Sincronizados",
        defaults={"budget": 0}
    )
    
    expenses_created = 0
    errors = 0
    
    for email in emails:
        # Check if we already synced this by looking at unique identifiable fields, 
        # but right now we don't have a specific `email_id` field. We'll add a simple guard:
        # (Though robust check would need an `email_id` field on Expense model. For now, we trust the sync or check by exact amount + date + card)
        
        parsed_data = parse_expense_from_email_llm(email['body'], email['date'])
        
        if parsed_data.get("amount") and parsed_data["amount"] > 0:
            # Simple duplication prevention strategy
            exists = Expense.objects.filter(
                card=card,
                amount=parsed_data["amount"],
                date=parsed_data["date"],
                name=parsed_data["merchant"]
            ).exists()
            
            if not exists:
                Expense.objects.create(
                    name=parsed_data["merchant"],
                    amount=parsed_data["amount"],
                    date=parsed_data["date"],
                    category=category,
                    type="card",
                    card=card
                )
                expenses_created += 1
            else:
                 pass # Already exists
        else:
             errors += 1
             
    msg = f"Created {expenses_created} expenses."
    if errors > 0:
        msg += f" Failed to parse {errors} emails."
        
    return expenses_created, msg
