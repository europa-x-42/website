CREATE TABLE Users (username TEXT,email TEXT,password TEXT,isAdmin BOOLEAN);
INSERT INTO Users (username,email,password,isAdmin) VALUES ('admin','europax@yopmail.com','92b5fe2e600aa6a33b0cd0deeb07e1b34bcf9c997e9a2443769ffa8e1fb878e2',False);
--Default admin password: 'password'. Should be changed in production database
CREATE TABLE Catalog (itemID INTEGER,name TEXT,description TEXT,price FLOAT,imageURL TEXT);
