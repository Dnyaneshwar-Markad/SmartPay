import pandas as pd
from datetime import datetime
import os

def generate_excel_report(df, budget_allocation, monthly_budget, save_path="expense_report.xlsx"):
    """
    Generates an Excel report for the given transactions DataFrame.

    Args:
        df (pd.DataFrame): Must contain ['date', 'amount', 'category', 'type'] columns
        budget_allocation (dict): e.g., {"Food": 0.2, "Rent": 0.3}
        monthly_budget (float): Total budget amount for the month
        save_path (str): File name/path to save Excel file (default: auto-named by date)
    """
    try:
        # Auto filename based on date if not changed
        if save_path == "expense_report.xlsx":
            today_str = datetime.now().strftime("%Y_%m_%d")
            save_path = f"expense_report_{today_str}.xlsx"

        writer = pd.ExcelWriter(save_path, engine='xlsxwriter')
        workbook = writer.book

        # ------------------ Sheet 1: Summary ------------------
        total_income = df[df['type'] == 'income']['amount'].sum() if 'income' in df['type'].values else 0
        total_expenses = df[df['type'] == 'expense']['amount'].sum()
        savings = total_income - total_expenses if total_income else monthly_budget - total_expenses

        summary_data = {
            'Total Income': [total_income if total_income else monthly_budget],
            'Total Expenses': [total_expenses],
            'Savings': [savings]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

        # ------------------ Sheet 2: Budget Analysis ------------------
        actuals = df[df['type'] == 'expense'].groupby('category')['amount'].sum().to_dict()
        budget_table = []

        for category, percent in budget_allocation.items():
            allocated = round(monthly_budget * percent, 2)
            spent = round(actuals.get(category, 0), 2)
            remaining = round(allocated - spent, 2)
            status = "✅ Within Budget" if remaining >= 0 else "⚠️ Over Budget"
            budget_table.append({
                'Category': category,
                'Budgeted': allocated,
                'Spent': spent,
                'Remaining': remaining,
                'Status': status
            })

        budget_df = pd.DataFrame(budget_table)
        budget_df.to_excel(writer, sheet_name='Budget Analysis', index=False)

        # Apply conditional formatting to 'Status' column (E = col 4)
        worksheet = writer.sheets['Budget Analysis']
        status_col = 4
        worksheet.conditional_format(1, status_col, len(budget_df), status_col, {
            'type': 'text',
            'criteria': 'containing',
            'value': 'Over Budget',
            'format': workbook.add_format({'font_color': 'red', 'bold': True})
        })
        worksheet.conditional_format(1, status_col, len(budget_df), status_col, {
            'type': 'text',
            'criteria': 'containing',
            'value': 'Within Budget',
            'format': workbook.add_format({'font_color': 'green', 'bold': True})
        })

        # ------------------ Sheet 3: Category Summary (optional) ------------------
        if 'expense' in df['type'].values:
            category_summary = df[df['type'] == 'expense'].groupby('category')['amount'].agg(['count', 'sum']).reset_index()
            category_summary.rename(columns={'count': 'Transactions', 'sum': 'Total Spent'}, inplace=True)
            category_summary.to_excel(writer, sheet_name='Category Summary', index=False)

        # ------------------ Sheet 4: Full Transactions Log ------------------
        df.to_excel(writer, sheet_name='Transactions', index=False)

        # Save the Excel file
        writer.close()
        print(f"[✔] Excel report saved to {save_path}")

    except Exception as e:
        print(f"[❌] Failed to generate Excel report: {e}")
