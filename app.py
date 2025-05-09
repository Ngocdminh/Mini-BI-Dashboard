from flask import Flask, render_template, request
import pandas as pd
import os
import plotly.graph_objs as go
import plotly.io as pio
import base64
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/', methods=['GET', 'POST'])
def index():
    data_summary = None
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            try:
                df = pd.read_csv(filepath)

        # 🧼 Clean column names: remove spaces, make lowercase
                df.columns = [col.strip().lower() for col in df.columns]

        # ✅ Check required columns
                if 'revenue' not in df.columns or 'cost' not in df.columns:
                    return render_template('index.html', summary=None,
                                        error="CSV must contain 'Revenue' and 'Cost' columns (case-insensitive).")

        # Rename for consistent internal use
                df.rename(columns={'revenue': 'Revenue', 'cost': 'Cost'}, inplace=True)

        # Calculate profit
                df['Profit'] = df['Revenue'] - df['Cost']

        # Optional: handle 'Date' column
                if 'date' in df.columns:
                    df['Date'] = pd.to_datetime(df['date'])
                else:
                    df['Date'] = pd.date_range(start='2024-01-01', periods=len(df))

        # Summary stats
                total_revenue = df['Revenue'].sum()
                total_cost = df['Cost'].sum()
                total_profit = df['Profit'].sum()
                profit_margin = (total_profit / total_revenue) * 100 if total_revenue else 0

        # Plot with Plotly
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['Date'], y=df['Revenue'], mode='lines+markers', name='Revenue'))
                fig.add_trace(go.Scatter(x=df['Date'], y=df['Profit'], mode='lines+markers', name='Profit'))
                fig.update_layout(title='Revenue and Profit Over Time', xaxis_title='Date', yaxis_title='Amount')

                img_bytes = fig.to_image(format="png")
                encoded_img = base64.b64encode(img_bytes).decode()

                data_summary = {
                    'revenue': total_revenue,
                    'cost': total_cost,
                    'profit': total_profit,
                    'margin': round(profit_margin, 2),
                    'data': df.to_dict(orient='records'),
                    'plot_url': f"data:image/png;base64,{encoded_img}"
        }

            except Exception as e:
                return render_template('index.html', summary=None, error=f"Error processing file: {str(e)}")
    return render_template('index.html', summary=data_summary, error=None)

if __name__ == '__main__':
    app.run(debug=True)

