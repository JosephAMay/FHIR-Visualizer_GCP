CREATE DATABASE IF NOT EXISTS visualization;
USE visualization;

CREATE TABLE  IF NOT EXISTS worker(
    UserID INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    FirstName VARCHAR(30) NOT NULL,
    LastName VARCHAR(30) NOT NULL,
    Username VARCHAR(30) NOT NULL,
    Password VARCHAR(30) NOT NULL, 
    EmailAddress VARCHAR(40) NOT NULL,
    ProviderID INT,
    IsAdmin BOOLEAN DEFAULT 0
);



CREATE TABLE  IF NOT EXISTS user(
    UserID INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    FirstName VARCHAR(30) NOT NULL,
    LastName VARCHAR(30) NOT NULL,
    Username VARCHAR(30) NOT NULL,
    Password VARCHAR(30) NOT NULL, 
    EmailAddress VARCHAR(40) NOT NULL
);
    
INSERT INTO worker (FirstName, LastName, Username, Password, EmailAddress, ProviderID, IsAdmin) VALUES 
( "joseph", "may","joseph.may", "password", "joseph.may@example.com", NULL, 1 ),
("Taylor", "Hartman","taylor.hartman", "password", "taylor.hartman@example.com", NULL,1),
("John", "Smith","john.smith", "password", "john.smith@example.com",105, 0 ),
( "Jane", "Doe","jane.doe", "password", "jane.doe@example.com", 106, 0);

INSERT INTO user (FirstName, LastName, Username, Password, EmailAddress) VALUES 
( "User1", "Lname1","user1.lname", "password", "user1.lnamey@example.com"),
("User2", "Lname2","user2.lname", "password", "user2.lname@example.com"),
("User3", "Lname3","user3.lname", "password", "user3.lname@example.com"),
( "User4", "Lname4","user4.lname", "password", "user4.lname@example.com");