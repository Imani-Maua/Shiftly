-- This file creates all the tables in the schema

CREATE TABLE talents(
    id SERIAL PRIMARY KEY,
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    email VARCHAR(100),
    tal_role VARCHAR(50) NOT NULL,
    contract_type VARCHAR(50) DEFAULT 'full-time',
    is_active BOOLEAN DEFAULT TRUE,
    hours INTEGER DEFAULT 40,
    start_date DATE,
    end_date DATE
);

CREATE TABLE talent_constraints(
    id SERIAL PRIMARY KEY,
    talent_id INTEGER REFERENCES talents(id),
    type VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE
);


CREATE TABLE constraint_days(
    id SERIAL PRIMARY KEY,
    constraint_id INTEGER REFERENCES talent_constraints(id),
    day VARCHAR(50),
    shifts VARCHAR(50)
);

CREATE TABLE requests(
    id SERIAL PRIMARY KEY,
    talent_id INTEGER REFERENCES talents(id),
    req_date DATE NOT NULL,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users(
    id INTEGER,
    username VARCHAR(20),
    user_role VARCHAR(20),
    email VARCHAR(100),
    hashed_password VARCHAR(128),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)

CREATE OR REPLACE FUNCTION update_updated_at() 
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
BEFORE UPDATE ON requests
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TABLE scheduled_shifts(
    id SERIAL PRIMARY KEY,
    talent_id INTEGER REFERENCES talents(id),
    date_of DATE,
    start_time TIME,
    end_time TIME,
    shift_hours NUMERIC(3,1)
);

CREATE TABLE shift_periods(
    id SERIAL PRIMARY KEY,
    staffing VARCHAR(50),
    shift_name VARCHAR(50),
    start_time TIME,
    end_time TIME
);

CREATE TABLE shift_templates(
    id SERIAL PRIMARY KEY,
    period_id INTEGER REFERENCES shift_periods(id),
    role VARCHAR(50), 
    role_count INTEGER
);

CREATE TABLE events(
    id SERIAL PRIMARY KEY,
    shift_id INTEGER REFERENCES scheduled_shifts(id),
    event_name VARCHAR(50),
    event_date DATE,
    is_mandatory BOOLEAN,
    start_time TIME,
    end_time TIME,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)

CREATE OR REPLACE FUNCTION update_updated_at() 
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
BEFORE UPDATE ON events
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();


-- talent_data
create or replace view talent_data as
select t.id as talent_id,
t.firstname ||' '|| t.lastname as talent_name,
t.tal_role as tal_role,
t.hours as hours,
tc.type as constraint_type, 
tc.is_active as constraint_status,
cd.day as available_day,
cd.shifts as available_shifts
from talents t
left join talent_constraints tc on t.id=tc.talent_id

-- shift_data

CREATE OR REPLACE VIEW shift_data AS
 SELECT DISTINCT sp.id AS period_id,
    sp.staffing,
    sp.shift_name,
    sp.start_time,
    sp.end_time,
    st.role AS role_name,
    st.role_count
FROM shift_periods sp
JOIN shift_templates st ON sp.id = st.period_id;

