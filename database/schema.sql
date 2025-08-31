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




