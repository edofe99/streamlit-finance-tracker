import streamlit as st
import pandas as pd
import time
from datetime import date
import plotly.express as px

@st.dialog("Add a new expense",width="large")
def add_expense():
    date = st.date_input("Date", value="today",format='YYYY-MM-DD')
    expense = st.text_input("Expense")
    amount = st.number_input("Amount $", step=0.01)
    choices = st.session_state.data['Account'].unique().tolist()
    choices.append('Other')
    account = st.selectbox("Account: ", choices,index=None,
                           placeholder='Please select account')
    if account == "Other": 
        account = st.text_input(label='Enter new account')
    category = st.text_input("Category")
    note = st.text_area("Note")

    if st.button("Submit"):
        new_data = pd.DataFrame(
            {
                "Date": [date],
                "Expense": [expense],
                "Amount": [amount],
                "Account": [account],
                "Category": [category],
                "Note": [note],
            }
        )

        new_data["Date"] = pd.to_datetime(new_data["Date"])
        st.session_state.data = pd.concat(
            [st.session_state.data, new_data], ignore_index=True
        )

        st.success("Expense added!")
        time.sleep(1)
        st.rerun()

@st.dialog("Field Editor",width="large")
def edit_expense():
    
    df = st.session_state.data
    new_data = pd.DataFrame()
    edit_box = st.container(border=True)
    
    with edit_box: 
        #st.markdown('### Select entry to edit')
        col1, col2 = st.columns(2)
        with col1:
            date = col1.date_input("Date", value="today", format='YYYY-MM-DD')
            filtered_df = df[df['Date'] == date.strftime('%Y-%m-%d')]
        with col2:
            check_expenses = 'No expenses for this date' if df[df['Date'] == date.strftime('%Y-%m-%d')].empty else 'Choose an option'
            expense = col2.selectbox(
                 label='Select field to edit',
                 index=None,
                 placeholder=check_expenses,
                 options= filtered_df['Expense'].drop_duplicates().tolist()
            )
        
        if not filtered_df.empty:#filtered_df.shape[0] == 1:
            with edit_box:
                plotDataFrame(filtered_df[['Date','Expense','Amount','Account','Category']]) 
                #st.markdown(table_styler(filtered_df[['Date','Expense','Amount','Account','Category']]),unsafe_allow_html=True)


        if expense:
            filtered_df = df[(df['Date'] == date.strftime('%Y-%m-%d')) & (df['Expense'] == expense)]
            filtered_amount = df[(df['Date'] == date.strftime('%Y-%m-%d')) & (df['Expense'] == expense)]['Amount']

            if filtered_df['Expense'].duplicated().any():
                st.write(f'There are duplicates for **{expense}**, select the amount you want to change:' )
                amount = st.selectbox("Select Amount",
                                        index=None,
                                        options=filtered_amount)    
            else:
                amount = filtered_amount.iloc[0]

            if amount:
                filtered_df = df[(df['Date'] == date.strftime('%Y-%m-%d')) & (df['Expense'] == expense) 
                                & (df['Amount'] == amount)]
                account = df[(df['Date'] == date.strftime('%Y-%m-%d')) & (df['Expense'] == expense) & 
                            (df['Amount'] == amount)]['Account'].iloc[0]

            if filtered_df.shape[0] == 1:
                st.markdown('### Edit field')
                e_col1, e_col2, e_col3 = st.columns(3)
                e_date = e_col1.date_input("Date", value=date, format='YYYY-MM-DD')
                e_expense = e_col2.text_input("Expense",value=expense)
                e_amount = e_col1.number_input("Amount $", step=0.01,
                                        value=amount)
                e_account = e_col2.text_input("Account",value=account)
                e_category = e_col3.text_input("Category",value=filtered_df['Category'].iloc[0])
                e_note = st.text_area("Note",value=filtered_df['Note'].fillna("").iloc[0],placeholder="Insert note")

                new_data = pd.DataFrame(
                    {
                        "Date": [e_date],
                        "Expense": [e_expense],
                        "Amount": [e_amount],
                        "Account": [e_account],
                        "Category": [e_category],
                        "Note": [e_note],
                    }
                )
                new_data['Date'] = pd.to_datetime(new_data['Date'], format='%Y-%m-%d')

    if len(new_data) == 1 and len(filtered_df) == 1 and not new_data.reset_index(drop=True).equals(filtered_df.reset_index(drop=True)):
        if st.button("Save"):
        #if new_data:
            # Update the matching row in df_first with the values from df_second
            
            st.session_state.data.loc[filtered_df.index[0], :] = new_data.iloc[0]

            st.success("Successfully modified entry.")
            time.sleep(1)
            st.rerun()
    else:
        if st.button("Save"):
            st.info('Please make a change before saving', icon="ℹ️")

def plotDataFrame(df):
        st.dataframe(
        df,
        hide_index=True,
        height=35 * len(df) + 19 * 2,
        use_container_width = True,
        column_config={
            "Date": st.column_config.DateColumn(
                default=date.today(), format="YYYY-MM-DD", width="small"
            ),
            "Expense": st.column_config.TextColumn(width="None"),
            "Amount": st.column_config.NumberColumn(
                "Amount",
                help="The value in $ of the expense",
                step=0.01,
                format="%.2f $",
                width="None",
            ),
            "Account": st.column_config.TextColumn(width="None"),
            "Category": st.column_config.TextColumn(width="small"),
            "Note": st.column_config.TextColumn(width="None"),
        },
    )


def sum_dashboard():
    total_col, add_col = st.columns(2)
    summed_expenses = (
        st.session_state.data.groupby("Account")["Amount"].sum().reset_index()
    )
    if add_col.button(":money_with_wings: Add expense"):
        add_expense()
    
    total_col.markdown(f"##### Toal:  :blue[{summed_expenses['Amount'].sum():.2f} $]")
    
    col_accounts, col_pie = st.columns(2)
    with st.container(border=False):
        if not st.session_state.data.empty:
            # st.markdown('#### :bank: Accounts')
            with col_accounts:
                plotDataFrame(summed_expenses)
            with col_pie:
                # Create a pie chart using Plotly
                positive_expenses = summed_expenses[summed_expenses['Amount']>0.1]
                fig = px.pie(
                    names=positive_expenses['Account'], 
                    values=positive_expenses['Amount'], 
                    hole=0.4  # If you want a donut chart
                )
                fig.update_traces(
                    textinfo='label+value',  # Show both account name and amount
                    hoverinfo='none',  # Disable tooltips
                    texttemplate='%{label}<br>%{value:.2f}$'
                )
                fig.update_layout(showlegend=False)
                fig.update_layout(
                    margin=dict(
                        l=0,  # Left margin
                        r=0,  # Right margin
                        t=0,  # Top margin
                        b=0,  # Bottom margin
                    ),
                )
                fig.update_layout(
                    autosize=True,
                    width=400,
                    height=250)
                # Display the plot
                st.plotly_chart(fig)

            # ------------------- Deprecated account list using widgets ------------------ #
            # num_accounts = summed_expenses["Account"].nunique()
            # list_accounts = st.columns(num_accounts)
            # total = 0
            # index = 0
            # for col in list_accounts:
            #     account = summed_expenses.iloc[index]["Account"]
            #     number = summed_expenses.iloc[index]["Amount"]
            #     total += number
            #     amount = f"{number:.2f} $"
            #     # color = "green" if summed_expenses.iloc[index]["Amount"] > 0 else "red"
            #     # col.write(f'**{account}:   :{color}[{amount}]**')
            #     col.metric(account, amount)  # ,'10%')
            #     index = index + 1
        else:
            st.warning("There is no existent data, please add some expenses first")