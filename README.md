# Shiftly

Shiftly is a **shift scheduling MVP** designed to allocate employees (who Shiftly refers to as talents) to shifts efficiently while respecting availability and constraints. The project separates responsibilities clearly, applies abstraction for flexibility, and uses adapters for data transformation.

> ⚠️ **Note:** This is an MVP. Future enhancements may include maximum hours validation, consecutive-day checks, night-to-morning shift restrictions, and employee request handling.

---

## Features

- Fetch talent and shift data from a PostgreSQL database.
- Filter talents based on availability and constraints.
- Convert raw data into **Pandas DataFrames** for easy manipulation.
- Apply **eligibility rules** to determine which talents can work which shifts.
- Allocate shifts using a **rule-based system**.
- Output scheduled assignments.

> ⚠️ **Note:** Future enhancements will include:

- Maximum hours validation.
- Consecutive-day checks.
- Night-to-morning shift restrictions.
- Employee request handling.

---
