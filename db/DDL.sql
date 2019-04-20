DROP database stock;
CREATE database stock;
USE stock;


CREATE TABLE company (
	`SYMBOL` VARCHAR(10) PRIMARY KEY,
	`NAME` VARCHAR(50) NOT NULL,
	`BSE_CODE` bigint NOT NULL
);

CREATE TABLE stock (
	`COMPANY_SYMBOL` VARCHAR(10) NOT NULL,
	`DATE` DATE NOT NULL,
	`OPEN` DOUBLE NOT NULL,
	`CLOSE` DOUBLE NOT NULL,
	`HIGH` DOUBLE NOT NULL,
	`LOW` DOUBLE NOT NULL,
	`VOLUME` BIGINT(10) NOT NULL,
	PRIMARY KEY (`COMPANY_SYMBOL`, `DATE`),
	FOREIGN KEY (`COMPANY_SYMBOL`) REFERENCES company (`SYMBOL`) ON DELETE CASCADE
);

CREATE TABLE prediction (
	`COMPANY_SYMBOL` VARCHAR(10) NOT NULL,
	`CLASSIFIER` VARCHAR(10) NOT NULL,
	`TRADING_WINDOW` INT NOT NULL,
	`FORWARD_DAY` INT NOT NULL,
	`LABEL` INT NOT NULL,
	`PROBABILITY` DOUBLE NOT NULL,
	PRIMARY KEY (`COMPANY_SYMBOL`, `CLASSIFIER`, `TRADING_WINDOW`,`FORWARD_DAY`),
	FOREIGN KEY (`COMPANY_SYMBOL`) REFERENCES company (`SYMBOL`) ON DELETE CASCADE
);

CREATE TABLE features (
	`COMPANY_SYMBOL` VARCHAR(10) NOT NULL,
	`DATE` DATE NOT NULL,
	`TRADING_WINDOW` INT NOT NULL,
	`RSI` DOUBLE NOT NULL,
	`K` DOUBLE NOT NULL,
	`R` DOUBLE NOT NULL,
	`SL` DOUBLE NOT NULL,
	`PROC` DOUBLE NOT NULL,
	`OBV` DOUBLE NOT NULL,
	`LABEL` DOUBLE NOT NULL,
	`EMA_12_C` DOUBLE NOT NULL,
	`EMA_26_C` DOUBLE NOT NULL,
	`EMA_9_MACD` DOUBLE NOT NULL,
	PRIMARY KEY (`COMPANY_SYMBOL`, `DATE`, `TRADING_WINDOW`),
	FOREIGN KEY (`COMPANY_SYMBOL`) REFERENCES company (`SYMBOL`) ON DELETE CASCADE
);

-- TRIGGER AND PROCEDURE ON INSERTION OF NEW COMPANY
delimiter //
CREATE PROCEDURE onNewCompany(IN symbol varchar(10))
BEGIN
	DECLARE x INT;
	DECLARE y INT;
	SET x = 0;
	WHILE x < 90 DO
		INSERT INTO stock VALUES (symbol, DATE_ADD("1900-01-01", INTERVAL x DAY), 0, 0, 0, 0, 0);
		SET x = x + 1;
	END WHILE;
	SET y = 0;
	WHILE y < 90 DO
		INSERT INTO features VALUES (symbol, DATE_ADD("1900-01-01", INTERVAL y DAY), 3, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0);
		INSERT INTO features VALUES (symbol, DATE_ADD("1900-01-01", INTERVAL y DAY), 5, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0);
		INSERT INTO features VALUES (symbol, DATE_ADD("1900-01-01", INTERVAL y DAY), 15, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0);
		INSERT INTO features VALUES (symbol, DATE_ADD("1900-01-01", INTERVAL y DAY), 30, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0);
		INSERT INTO features VALUES (symbol, DATE_ADD("1900-01-01", INTERVAL y DAY), 60, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0);
		INSERT INTO features VALUES (symbol, DATE_ADD("1900-01-01", INTERVAL y DAY), 90, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0);
		SET y = y + 1;
	END WHILE;
    
	INSERT INTO prediction VALUES (symbol, "RF", 3, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "RF", 3, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "RF", 3, 5, 0 ,0);
    
    INSERT INTO prediction VALUES (symbol, "RF", 5, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "RF", 5, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "RF", 5, 5, 0 ,0);
    
    INSERT INTO prediction VALUES (symbol, "RF", 15, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "RF", 15, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "RF", 15, 5, 0 ,0);
    
    INSERT INTO prediction VALUES (symbol, "RF", 30, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "RF", 30, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "RF", 30, 5, 0 ,0);

	INSERT INTO prediction VALUES (symbol, "RF", 60, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "RF", 60, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "RF", 60, 5, 0 ,0);

	INSERT INTO prediction VALUES (symbol, "RF", 90, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "RF", 90, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "RF", 90, 5, 0 ,0);

	INSERT INTO prediction VALUES (symbol, "GBDT", 3, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "GBDT", 3, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "GBDT", 3, 5, 0 ,0);
    
    INSERT INTO prediction VALUES (symbol, "GBDT", 5, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "GBDT", 5, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "GBDT", 5, 5, 0 ,0);
    
    INSERT INTO prediction VALUES (symbol, "GBDT", 15, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "GBDT", 15, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "GBDT", 15, 5, 0 ,0);
    
    INSERT INTO prediction VALUES (symbol, "GBDT", 30, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "GBDT", 30, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "GBDT", 30, 5, 0 ,0);

	INSERT INTO prediction VALUES (symbol, "GBDT", 60, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "GBDT", 60, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "GBDT", 60, 5, 0 ,0);

	INSERT INTO prediction VALUES (symbol, "GBDT", 90, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "GBDT", 90, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "GBDT", 90, 5, 0 ,0);


	INSERT INTO prediction VALUES (symbol, "HYBRID", 3, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "HYBRID", 3, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "HYBRID", 3, 5, 0 ,0);
    
    INSERT INTO prediction VALUES (symbol, "HYBRID", 5, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "HYBRID", 5, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "HYBRID", 5, 5, 0 ,0);
    
    INSERT INTO prediction VALUES (symbol, "HYBRID", 15, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "HYBRID", 15, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "HYBRID", 15, 5, 0 ,0);
    
    INSERT INTO prediction VALUES (symbol, "HYBRID", 30, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "HYBRID", 30, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "HYBRID", 30, 5, 0 ,0);

	INSERT INTO prediction VALUES (symbol, "HYBRID", 60, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "HYBRID", 60, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "HYBRID", 60, 5, 0 ,0);

	INSERT INTO prediction VALUES (symbol, "HYBRID", 90, 1, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "HYBRID", 90, 3, 0 ,0);
    INSERT INTO prediction VALUES (symbol, "HYBRID", 90, 5, 0 ,0);
END//

CREATE TRIGGER onNewCompanyTrigger
AFTER INSERT ON company
FOR EACH ROW
BEGIN
	call onNewCompany(NEW.`SYMBOL`);
END//
delimiter ;
