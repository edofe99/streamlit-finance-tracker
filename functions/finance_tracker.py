import streamlit as st
from functions.tracker_functions import edit_expense, plotDataFrame,sum_dashboard
from datetime import datetime, timedelta
import plotly.express as px



def expense_earning_chart():
    col1, col2 = st.columns(2)

    category_sum = (
        st.session_state.data.groupby("Category")["Amount"].sum().reset_index()
    )

    # Split the data into spending (negative) and entries (positive)
    spending = category_sum[category_sum["Amount"] < 0]
    entries = category_sum[category_sum["Amount"] > 0]

    # Convert amounts to positive for pie chart display purposes
    spending["Amount"] = spending["Amount"].abs()

    def chart(title, data):
        fig = px.bar(
            data,
            x="Category",
            y="Amount",
        )

        fig.update_traces(texttemplate="%{y:.2f}$", textposition="outside")
        fig.update_layout(
            xaxis_title=None,  # Remove x-axis label
            yaxis_title=None,  # Remove y-axis label
            xaxis=dict(
                showticklabels=True,  # Hide x-axis tick labels
                showgrid=False,  # Hide x-axis grid lines
            ),
            yaxis=dict(
                showticklabels=False,  # Hide y-axis tick labels
                showgrid=False,  # Hide y-axis grid lines
            ),
            title=dict(text="", x=0.5, xanchor="center"),  # Remove the chart title
            # dict(
            # x=0.5,  # Center the title
            # xanchor='center')
            margin=dict(
                l=20,  # Left margin
                r=20,  # Right margin
                t=0,  # Top margin
                b=0,  # Bottom margin
            ),
        )
        return fig

    with col1.container(border=True):
        st.markdown(f'#### :red[Expenses: {spending['Amount'].sum():.2f}$]')
        st.plotly_chart(chart("Expenses", spending))
    with col2.container(border=True):
        st.markdown(f'#### :green[Entries: {entries['Amount'].sum():.2f}$]')
        st.plotly_chart(chart("Entries", entries))


def main_dashboard():
    # sum_dashboard()

    tab1, tab2 = st.tabs(["🏠 Dashboard", "💰 Expenses List"])

    
    with tab1:
        sum_dashboard()

        expense_earning_chart()

    with tab2:

        st.markdown('### Expenses from')        
        
        df = st.session_state.data
        df = df.sort_values(by='Date', ascending=True)
        df_toplot = df.tail(10)

        today = datetime.now()
        
        if not hasattr(st.session_state, 'custom_range'):
            st.session_state.custom_range = False

        this_week, this_month, this_year, custom_range, edit_col= st.columns(5)
        if this_week.button('This week'):
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            df_toplot = df[(df['Date'] >= start_of_week) & (df['Date'] <= end_of_week)]
            st.session_state.custom_range = False

        if this_month.button('This month'):
            start_of_month = today.replace(day=1)
            next_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1)
            end_of_month = next_month - timedelta(days=1)

            df_toplot = df[(df['Date'] >= start_of_month) & (df['Date'] <= end_of_month)]
            st.session_state.custom_range = False

        if this_year.button('This year'):
            # Get the start and end of the current year
            start_of_year = today.replace(month=1, day=1)
            end_of_year = today.replace(month=12, day=31)

            df_toplot = df[(df['Date'] >= start_of_year) & (df['Date'] <= end_of_year)]
            st.session_state.custom_range = False

        if custom_range.button('Custom range') or st.session_state.custom_range:
            st.session_state.custom_range = True
            col_start,col_end = st.columns(2)
            date_start = col_start.date_input(
                "Select start date",
                value=df['Date'].min(),
                min_value=df['Date'].min(),
                max_value=df['Date'].max(),
                format="YYYY-MM-DD",
                )
            date_end = col_end.date_input(
                "Select end date",
                value=df['Date'].max(),
                min_value=df['Date'].min(),
                max_value=df['Date'].max(),
                format="YYYY-MM-DD",
                )
            date_start = datetime.combine(date_start, datetime.min.time())
            date_end = datetime.combine(date_end, datetime.min.time())
            if date_start and date_end:
                df_toplot = df[(df['Date'] >= date_start) & (df['Date'] <= date_end)]
            

        if edit_col.button('✏️ Edit data'):
            edit_expense()

        if not df_toplot.empty:
            plotDataFrame(df_toplot)
        else:
            st.warning('No data for selected time range')


    css = """
    <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size:1.2rem;
        }
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)
