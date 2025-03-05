-- Drop existing tables if they exist
DROP TABLE IF EXISTS borrowed_chemicals;
DROP TABLE IF EXISTS indent;

-- Create table for borrowed chemicals
CREATE TABLE borrowed_chemicals (
    id SERIAL PRIMARY KEY,  -- Auto-incrementing ID
    borrower_name VARCHAR(255) NOT NULL,  -- Name of the borrower
    lab VARCHAR(255) NOT NULL,  -- Laboratory where borrowed
    division VARCHAR(7) NOT NULL,  -- Division of the borrower
    phone_number CHAR(10) NOT NULL,  -- Phone number of the borrower
    chemical_name VARCHAR(255) DEFAULT NULL,  -- Name of the chemical borrowed
    bottle_quantity VARCHAR(10) DEFAULT NULL,  -- Quantity of bottles borrowed
    date_borrowed DATE NOT NULL,  -- Date when borrowed
    status TEXT CHECK (status IN ('Borrowed', 'Returned')) DEFAULT 'Borrowed',  -- Status of the borrowing (Borrowed or Returned)
    date_returned TIMESTAMP DEFAULT NULL,  -- Timestamp when returned
    CONSTRAINT borrowed_chemicals_chk_1 CHECK (phone_number ~ '^[0-9]{10}$')  -- Validate phone number format
);

-- Create table for indents
CREATE TABLE indent (
    id SERIAL PRIMARY KEY,  -- Auto-incrementing ID
    date DATE NOT NULL,  -- Date of the indent
    chemical_name VARCHAR(255) NOT NULL,  -- Name of the chemical indented
    cas_no VARCHAR(100) NOT NULL,  -- CAS number of the chemical
    company VARCHAR(255) NOT NULL,  -- Company involved in the indent
    quantity VARCHAR(10) NOT NULL,  -- Quantity of the chemical indented
    bottle_quantity VARCHAR(10) DEFAULT NULL,  -- Quantity of bottles indented
    status TEXT CHECK (status IN ('Pending', 'Approved', 'Rejected')) DEFAULT 'Pending'  -- Status of the indent (Pending, Approved, or Rejected)
);
