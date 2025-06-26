CREATE TABLE employees (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  department VARCHAR(100)
);

INSERT INTO employees (name, department) VALUES
('Alice', 'Engineering'),
('Bob', 'Marketing');
