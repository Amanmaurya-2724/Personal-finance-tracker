# 💰 Personal Finance Tracker  

A **Streamlit + MySQL-based web app** to manage, track, and visualize your personal finances.  
This project helps you **add transactions, set budgets, generate reports, and analyze income vs. expenses** with interactive dashboards.  

---

## 🚀 Features  
- 📊 **Dashboard** – Visualize total income, expenses, and net cash flow  
- 📝 **Add Transactions** – Record income/expense with category & description  
- 📂 **View Transactions** – Filter by date/type & export to CSV  
- 💡 **Budget Management** – Set monthly budgets and compare with actual spending  
- 📈 **Reports** – Monthly trends, category breakdowns, and detailed summaries  

---

## 🛠️ Tech Stack  
- **Frontend/UI:** [Streamlit](https://streamlit.io/)  
- **Database:** MySQL  
- **Visualization:** Plotly  
- **Config & Security:** dotenv for environment variables  

---

## 📂 Project Structure  
finance-tracker/
├── app.py # Main Streamlit app
├── database.py # Database connection & queries
├── requirements.txt # Project dependencies
├── .env # Environment variables (DB credentials)
└── README.md # Project documentation

yaml
Copy code

---

## ⚙️ Setup Instructions  

### 1. Clone the repository  
```bash
git clone https://github.com/Amanmaurya-2724/Personal-finance-tracker.git
cd Personal-finance-tracker
2. Install dependencies
bash
Copy code
pip install -r requirements.txt
3. Set up environment variables
Create a .env file in the root directory:

ini
Copy code
DB_HOST=localhost
DB_NAME=finance_tracker
DB_USER=root
DB_PASSWORD=yourpassword
4. Run the app
bash
Copy code
streamlit run app.py
