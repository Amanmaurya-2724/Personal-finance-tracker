import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from database import Database

# Initialize database
db = Database()
db.initialize_database()

# Page configuration
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="main-header">💰 Personal Finance Tracker</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Add Transaction", "View Transactions", "Budget Management", "Reports"])

# Utility functions
def get_categories(type_filter=None):
    if type_filter:
        query = "SELECT name FROM categories WHERE type = %s ORDER BY name"
        result = db.execute_query(query, (type_filter,), fetch=True)
        return [cat['name'] for cat in result] if result else []
    else:
        query = "SELECT name, type FROM categories ORDER BY type, name"
        result = db.execute_query(query, fetch=True)
        return result if result else []

def add_transaction(amount, category, type, description, date):
    query = """
        INSERT INTO transactions (amount, category, type, description, date)
        VALUES (%s, %s, %s, %s, %s)
    """
    return db.execute_query(query, (amount, category, type, description, date))

def get_transactions(start_date=None, end_date=None):
    query = "SELECT * FROM transactions"
    params = []
    
    if start_date and end_date:
        query += " WHERE date BETWEEN %s AND %s"
        params.extend([start_date, end_date])
    elif start_date:
        query += " WHERE date >= %s"
        params.append(start_date)
    elif end_date:
        query += " WHERE date <= %s"
        params.append(end_date)
    
    query += " ORDER BY date DESC"
    return db.execute_query(query, params, fetch=True)

def get_transactions_summary(start_date=None, end_date=None):
    query = """
        SELECT 
            type,
            category,
            SUM(amount) as total_amount,
            COUNT(*) as transaction_count
        FROM transactions
    """
    params = []
    
    if start_date and end_date:
        query += " WHERE date BETWEEN %s AND %s"
        params.extend([start_date, end_date])
    elif start_date:
        query += " WHERE date >= %s"
        params.append(start_date)
    elif end_date:
        query += " WHERE date <= %s"
        params.append(end_date)
    
    query += " GROUP BY type, category ORDER BY type, total_amount DESC"
    return db.execute_query(query, params, fetch=True)

def set_budget(category, amount, month):
    # Check if budget already exists for this category and month
    check_query = "SELECT id FROM budgets WHERE category = %s AND month = %s"
    existing = db.execute_query(check_query, (category, month), fetch=True)
    
    if existing:
        # Update existing budget
        query = "UPDATE budgets SET amount = %s WHERE category = %s AND month = %s"
        return db.execute_query(query, (amount, category, month))
    else:
        # Insert new budget
        query = "INSERT INTO budgets (category, amount, month) VALUES (%s, %s, %s)"
        return db.execute_query(query, (category, amount, month))

def get_budgets(month=None):
    query = "SELECT * FROM budgets"
    params = []
    
    if month:
        query += " WHERE month = %s"
        params.append(month)
    
    query += " ORDER BY category"
    return db.execute_query(query, params, fetch=True)

def get_budget_vs_actual(month):
    query = """
        SELECT 
            b.category,
            b.amount as budget_amount,
            COALESCE(SUM(CASE WHEN t.type = 'expense' THEN t.amount ELSE 0 END), 0) as actual_expenses
        FROM budgets b
        LEFT JOIN transactions t ON b.category = t.category 
            AND DATE_FORMAT(t.date, '%Y-%m') = %s
        WHERE b.month = %s
        GROUP BY b.category, b.amount
    """
    return db.execute_query(query, (month, month), fetch=True)

# Dashboard Page
if page == "Dashboard":
    st.header("Financial Dashboard")
    
    # Date filters
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today().replace(day=1))
    with col2:
        end_date = st.date_input("End Date", value=date.today())
    
    # Get transactions summary
    summary = get_transactions_summary(start_date, end_date)
    
    if summary:
        # Calculate totals
        total_income = sum(item['total_amount'] for item in summary if item['type'] == 'income')
        total_expenses = sum(item['total_amount'] for item in summary if item['type'] == 'expense')
        net_flow = total_income - total_expenses
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Income", f"${total_income:,.2f}")
        with col2:
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
        with col3:
            st.metric("Net Cash Flow", f"${net_flow:,.2f}", delta_color="inverse" if net_flow < 0 else "normal")
        
        # Income vs Expenses chart
        st.subheader("Income vs Expenses")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Income', 'Expenses'],
            y=[total_income, total_expenses],
            marker_color=['green', 'red']
        ))
        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Amount ($)",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Expense breakdown
        expense_data = [item for item in summary if item['type'] == 'expense']
        if expense_data:
            st.subheader("Expense Breakdown")
            fig = px.pie(
                expense_data, 
                values='total_amount', 
                names='category',
                title="Expenses by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Income breakdown
        income_data = [item for item in summary if item['type'] == 'income']
        if income_data:
            st.subheader("Income Breakdown")
            fig = px.pie(
                income_data, 
                values='total_amount', 
                names='category',
                title="Income by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No transactions found for the selected period.")

# Add Transaction Page
elif page == "Add Transaction":
    st.header("Add New Transaction")
    
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_type = st.radio("Type", ["income", "expense"])
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
            transaction_date = st.date_input("Date", value=date.today())
        
        with col2:
            categories = get_categories(transaction_type)
            category = st.selectbox("Category", categories)
            description = st.text_input("Description")
        
        submitted = st.form_submit_button("Add Transaction")
        
        if submitted:
            if amount > 0:
                result = add_transaction(amount, category, transaction_type, description, transaction_date)
                if result:
                    st.success("Transaction added successfully!")
                else:
                    st.error("Error adding transaction. Please try again.")
            else:
                st.error("Amount must be greater than 0.")

# View Transactions Page
elif page == "View Transactions":
    st.header("View Transactions")
    
    # Date filters
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", key="view_start")
    with col2:
        end_date = st.date_input("End Date", key="view_end")
    
    # Type filter
    type_filter = st.selectbox("Filter by Type", ["All", "income", "expense"])
    
    # Get transactions
    transactions = get_transactions(start_date, end_date)
    
    if transactions:
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(transactions)
        
        # Apply type filter
        if type_filter != "All":
            df = df[df['type'] == type_filter]
        
        # Format date and amount
        df['date'] = pd.to_datetime(df['date']).dt.date
        df['amount'] = df['amount'].apply(lambda x: f"${x:,.2f}")
        
        # Display transactions
        st.dataframe(
            df[['date', 'type', 'category', 'amount', 'description']],
            use_container_width=True,
            hide_index=True
        )
        
        # Export option
        if st.button("Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"transactions_{date.today()}.csv",
                mime="text/csv"
            )
    else:
        st.info("No transactions found for the selected period.")

# Budget Management Page
elif page == "Budget Management":
    st.header("Budget Management")
    
    tab1, tab2 = st.tabs(["Set Budget", "View Budgets"])
    
    with tab1:
        st.subheader("Set Monthly Budget")
        
        # Get current month and year
        current_month = date.today().strftime("%Y-%m")
        
        with st.form("budget_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                month = st.text_input("Month (YYYY-MM)", value=current_month)
            
            with col2:
                expense_categories = get_categories("expense")
                category = st.selectbox("Category", expense_categories)
            
            with col3:
                amount = st.number_input("Budget Amount ($)", min_value=0.01, step=0.01, format="%.2f")
            
            submitted = st.form_submit_button("Set Budget")
            
            if submitted:
                if amount > 0:
                    result = set_budget(category, amount, month)
                    if result:
                        st.success("Budget set successfully!")
                    else:
                        st.error("Error setting budget. Please try again.")
                else:
                    st.error("Amount must be greater than 0.")
    
    with tab2:
        st.subheader("View Budgets")
        
        # Month selection
        selected_month = st.text_input("View Month (YYYY-MM)", value=current_month)
        
        # Get budgets for selected month
        budgets = get_budgets(selected_month)
        
        if budgets:
            # Display budgets
            st.write(f"Budgets for {selected_month}")
            for budget in budgets:
                st.write(f"- {budget['category']}: ${budget['amount']:,.2f}")
            
            # Budget vs Actual comparison
            st.subheader("Budget vs Actual")
            comparison = get_budget_vs_actual(selected_month)
            
            if comparison:
                comp_df = pd.DataFrame(comparison)
                comp_df['difference'] = comp_df['budget_amount'] - comp_df['actual_expenses']
                comp_df['status'] = comp_df['difference'].apply(
                    lambda x: 'Under Budget' if x >= 0 else 'Over Budget'
                )
                
                # Display comparison
                for _, row in comp_df.iterrows():
                    status_color = "green" if row['difference'] >= 0 else "red"
                    st.write(
                        f"- {row['category']}: "
                        f"Budget: ${row['budget_amount']:,.2f}, "
                        f"Actual: ${row['actual_expenses']:,.2f}, "
                        f"Difference: <span style='color:{status_color}'>${row['difference']:,.2f}</span>",
                        unsafe_allow_html=True
                    )
                
                # Create bar chart
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=comp_df['category'],
                    y=comp_df['budget_amount'],
                    name='Budget',
                    marker_color='blue'
                ))
                fig.add_trace(go.Bar(
                    x=comp_df['category'],
                    y=comp_df['actual_expenses'],
                    name='Actual',
                    marker_color='orange'
                ))
                fig.update_layout(
                    xaxis_title="Category",
                    yaxis_title="Amount ($)",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No budgets set for {selected_month}.")

# Reports Page
elif page == "Reports":
    st.header("Financial Reports")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today().replace(day=1), key="report_start")
    with col2:
        end_date = st.date_input("End Date", value=date.today(), key="report_end")
    
    # Get transaction summary
    summary = get_transactions_summary(start_date, end_date)
    
    if summary:
        # Convert to DataFrame
        df = pd.DataFrame(summary)
        
        # Monthly trend chart
        st.subheader("Monthly Trends")
        
        # Get monthly data
        monthly_query = """
            SELECT 
                DATE_FORMAT(date, '%Y-%m') as month,
                type,
                SUM(amount) as total_amount
            FROM transactions
            WHERE date BETWEEN %s AND %s
            GROUP BY month, type
            ORDER BY month
        """
        monthly_data = db.execute_query(monthly_query, (start_date, end_date), fetch=True)
        
        if monthly_data:
            monthly_df = pd.DataFrame(monthly_data)
            
            # Pivot the data
            pivot_df = monthly_df.pivot(index='month', columns='type', values='total_amount').fillna(0)
            
            # Create line chart
            fig = go.Figure()
            if 'income' in pivot_df.columns:
                fig.add_trace(go.Scatter(
                    x=pivot_df.index,
                    y=pivot_df['income'],
                    mode='lines+markers',
                    name='Income'
                ))
            if 'expense' in pivot_df.columns:
                fig.add_trace(go.Scatter(
                    x=pivot_df.index,
                    y=pivot_df['expense'],
                    mode='lines+markers',
                    name='Expenses'
                ))
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Amount ($)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Category breakdown
        st.subheader("Category Breakdown")
        
        # Create treemap
        fig = px.treemap(
            df, 
            path=['type', 'category'], 
            values='total_amount',
            color='type',
            color_discrete_map={'income':'green', 'expense':'red'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed summary table
        st.subheader("Detailed Summary")
        st.dataframe(
            df[['type', 'category', 'total_amount', 'transaction_count']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No transactions found for the selected period.")