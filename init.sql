CREATE DATABASE IF NOT EXISTS evoting;
USE evoting;

CREATE TABLE IF NOT EXISTS voter (
    voter_id int(11) NOT NULL AUTO_INCREMENT,
    name varchar(50) NOT NULL,
    username varchar(50) NOT NULL,
    password varchar(255) NOT NULL,
    has_voted boolean DEFAULT FALSE,
    assembly varchar(50) DEFAULT NULL,
    PRIMARY KEY (voter_id)
) AUTO_INCREMENT=1 DEFAULT CHARSET='utf8';

CREATE TABLE IF NOT EXISTS candidate (
	candidate_id INT(11) auto_increment,
	name VARCHAR(50) NOT NULL,
    number_of_votes INT default 0,
    party VARCHAR(25),
    criminal_records boolean default false,
    assembly VARCHAR(50) NOT NULL,
    age INT,
    PRIMARY KEY (candidate_id)
)AUTO_INCREMENT=1 DEFAULT CHARSET='utf8';

CREATE TABLE IF NOT EXISTS vote (
	vote_number INT auto_increment,
	candidate_id INT NOT NULL,
    voter_id INT default 0,
    time_stamp timestamp default current_timestamp(),
    PRIMARY KEY (vote_number)
)AUTO_INCREMENT=1 DEFAULT CHARSET='utf8';

CREATE TABLE IF NOT EXISTS results (
	result_id INT AUTO_INCREMENT,
	admin_id INT,
	candidate_id INT NOT NULL,
    candidate_name VARCHAR(50),
    number_of_votes INT default 0,
    party VARCHAR(50),
    assembly VARCHAR(50),
    PRIMARY KEY (result_id),
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id),
    FOREIGN KEY (candidate_id) REFERENCES candidate(candidate_id)
)DEFAULT CHARSET='utf8';

CREATE TABLE IF NOT EXISTS admin (
	admin_id INT primary key,
    name VARCHAR(50) not null,
    username VARCHAR(50) not null,
    password VARCHAR(255) not null,
    assembly VARCHAR(50)
)DEFAULT CHARSET='utf8';

CREATE TABLE IF NOT EXISTS votes_for(
	voter_id INT NOT NULL,
    voter_name VARCHAR(50) not null,
    candidate_id INT not null,
    candidate_name VARCHAR(50) not null,
    foreign key (voter_id) references voter(voter_id),
    foreign key (candidate_id) references candidate(candidate_id)
)DEFAULT CHARSET='utf8';