\c postgres;
DROP database codestreak;
CREATE database codestreak;

\c codestreak;

CREATE TABLE student(
	usn varchar(50) PRIMARY KEY,
	name varchar(50),
	rating float,
	best float,
	email varchar(50),
    password varchar(50),
    semester integer,
    section varchar(1)
);

CREATE TABLE professor(
    p_id varchar(50) PRIMARY KEY,
    name varchar(50),
    password varchar(50),
    email varchar(50)
);

CREATE TABLE question(
  q_id varchar(50) PRIMARY KEY,
  p_id varchar(50) REFERENCES professor(p_id),
  name varchar(50),
  create_time timestamp DEFAULT NOW(),
  problem varchar(10000),
  difficulty varchar(50),
  editorial varchar(10000),
  time_limit float, -- time in seconds
  memory_limit float, -- memory in kb
  test_cases json,
  score int DEFAULT 0,
  languages varchar(50) ARRAY[50],
  tags varchar(50) ARRAY[50]
);

CREATE TABLE contest(
   c_id varchar(50) PRIMARY KEY,
   p_id varchar(50) REFERENCES professor(p_id),
   name varchar(50),
   start_time timestamp,
   end_time timestamp,
   questions varchar(50) ARRAY[50], -- contains q_ids
   semester integer,
   section varchar(1),
   plagiarism json DEFAULT NULL,
   location varchar(50) DEFAULT NULL
);

CREATE TABLE submission(
  s_id varchar(50) PRIMARY KEY,
  usn varchar(50) REFERENCES student(usn),
  q_id varchar(50) REFERENCES question(q_id),
  c_id varchar(50) REFERENCES contest(c_id),
  score int DEFAULT 0,
  is_evaluated bool DEFAULT false,
  plagiarism float DEFAULT 0,
  submit_time timestamp DEFAULT NOW(),
  code varchar(10000),
  language varchar(50),
  test_case_status json,
  status varchar(50)
);
