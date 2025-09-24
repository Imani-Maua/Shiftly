# Shiftly

Shiftly is a shift scheduling MVP designed to allocate employees (called **talents**) to shifts efficiently while respecting their availability and constraints.  

The system separates responsibilities clearly, applies abstraction for flexibility, and uses adapters for transforming data between the database and the scheduler.  

> ⚠️ **Note:** This iteration of Shiftly is an MVP therefor not yet in production.
---

## ✨ Current Features  

- **Data integration**: Fetch talent and shift data from a PostgreSQL database and transform it into Pandas DataFrames for easy     manipulation.  
- **Role & availability matching**: Filter talents based on role requirements, availability windows, and allowed shift types.  
- **Constraint validation**: Apply rule-based validators to ensure compliance with scheduling rules, including:  
  - Maximum weekly working hours  
  - No more than one shift per day  
  - Minimum 11 hours rest between shifts  
  - Maximum six consecutive workdays  
- **Quota-aware allocation**: Assign up to the required number of talents per role/shift (e.g., 5 servers for one dinner shift).  
- **Prioritization**: Consider constrained talents first, then unconstrained, ensuring critical assignments are filled.  
- **Greedy, rule-based allocation**: For each shift, assign eligible talents until the role’s quota is met, ensuring all validators are satisfied.  
- **Output**: Return a list of valid shift–talent assignments.  

## 🚀 Future Enhancements  

- Employee request handling (preferences, time-off requests).  
- More advanced optimization for fairness and workload balance.  
- Integration of AI/ML models to predict staffing needs based on external factors (e.g., demand forecasts, seasonality).  

---

## 🛠️ Tech Stack

- **Backend Language**: Python 3.11+
- **Database**: PostgreSQL
- **Data Processing**: Pandas
- **Version Control**: Git

## Setup

Follow these instructions to get Shiftly running locally.

### 1. Clone the repository

```bash
git clone https://github.com/your-username/shiftly.git
cd shiftly
```

### 2. Create a virtual environment (optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the environment variables

Create a .env file in the root of the project

```bash
DB_HOST=your_database_host
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

### 5. Set up the database

- Connect to your postgreSQL database
- Run the schema file to create tables and views needed for shiftly

```bash
psql -U DB_USER -d DB_NAME -f schema.sql
```

- Seed the database with imaginary data

```bash
psql -U DB_USER -d DB_NAME -f seed.sql
```

### 6. Run the demo

```bash
python3 -m app.demo.demo
```