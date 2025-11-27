from flask import Flask, render_template, request
import math

app = Flask(__name__)

def calc_mortgage(loan_amount, annual_rate, years, extra_monthly=0.0):
    # monthly rate
    r = annual_rate / 100.0 / 12.0
    n = years * 12
    if r == 0:
        monthly = loan_amount / n
    else:
        monthly = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    monthly_with_extra = monthly + extra_monthly

    # Build amortization (first 360 rows max to avoid huge output)
    balance = loan_amount
    amort = []
    month = 0
    total_interest = 0.0
    while balance > 0.005 and month < 1000:
        month += 1
        interest = balance * r
        principal = min(monthly_with_extra - interest, balance)
        if principal < 0:
            principal = 0
        balance -= principal
        total_interest += interest
        amort.append({
            'month': month,
            'payment': round(monthly_with_extra, 2),
            'principal': round(principal, 2),
            'interest': round(interest, 2),
            'balance': round(balance if balance>0 else 0, 2)
        })
        # safety break if something weird
        if month > n + 100:
            break

    total_paid = sum(row['payment'] for row in amort)
    return {
        'monthly_payment': round(monthly, 2),
        'monthly_with_extra': round(monthly_with_extra, 2),
        'num_payments': len(amort),
        'total_paid': round(total_paid, 2),
        'total_interest': round(total_interest, 2),
        'amortization': amort[:360]  # limit shown rows
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    inputs = {}
    if request.method == 'POST':
        try:
            loan = float(request.form.get('loan', 0))
            rate = float(request.form.get('rate', 0))
            years = int(request.form.get('years', 0))
            extra = float(request.form.get('extra', 0))
            inputs = {'loan': loan, 'rate': rate, 'years': years, 'extra': extra}
            result = calc_mortgage(loan, rate, years, extra)
        except Exception as e:
            result = {'error': str(e)}
    return render_template('index.html', result=result, inputs=inputs)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
