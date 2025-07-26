from datetime import datetime, timedelta
from collections import defaultdict

def generate_reminders(transactions, user_budget):
    reminders = []

    # Group by category to calculate budget usage
    category_spending = defaultdict(float)
    today = datetime.today()

    # Handle both DataFrame and list of dicts
    if hasattr(transactions, "iterrows"):
        iterator = (row for _, row in transactions.iterrows())
    else:
        iterator = transactions

    for txn in iterator:
        # Use .get for dict, .get or .get(key, default) for Series, or fallback
        category = txn["category"] if "category" in txn else "Other"
        amount = float(txn["amount"]) if "amount" in txn else 0
        category_spending[category] += amount

        # Subscription reminder (basic logic using keywords)
        description = txn["description"].lower() if "description" in txn else txn["merchant"].lower() if "merchant" in txn else ""
        date_str = txn["date"] if "date" in txn else ""
        if any(keyword in description for keyword in ["netflix", "spotify", "prime", "emi", "subscription"]):
            try:
                txn_date = datetime.strptime(date_str, "%Y-%m-%d")
                next_due = txn_date + timedelta(days=30)

                if 0 <= (next_due - today).days <= 5:  # due within 5 days
                    reminders.append({
                        "type": "Subscription Due",
                        "message": f"Your {txn.get('description', '')} payment is due on {next_due.strftime('%d %b %Y')}",
                        "date": next_due.strftime("%Y-%m-%d"),
                        "priority": "High"
                    })
            except:
                continue

    # Budget over-usage alert
    for category, used in category_spending.items():
        budget = user_budget.get(category, 0) if hasattr(user_budget, "get") else 0
        if budget > 0 and used >= 0.9 * budget:
            reminders.append({
                "type": "Budget Alert",
                "message": f"You've used ₹{used:.2f} of your ₹{budget} budget for {category}.",
                "date": today.strftime("%Y-%m-%d"),
                "priority": "Medium" if used < budget else "High"
            })

    return reminders