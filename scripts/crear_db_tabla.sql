create table Pictures.pictures (id VARCHAR(36) PRIMARY KEY, 
                                path VARCHAR(256) NOT NULL,
                                date VARCHAR(25) NOT NULL,
                                size INT
                                );
create table Pictures.tags (tag VARCHAR(32), 
                            picture_id VARCHAR(36), 
                            confidence INT NOT NULL,
                            date VARCHAR(25) NOT NULL,
                            PRIMARY KEY (tag, picture_id),
                            FOREIGN KEY (picture_id) REFERENCES Pictures.pictures(id)
                            );
