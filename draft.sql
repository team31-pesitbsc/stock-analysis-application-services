DROP TABLE IF EXISTS features;
DROP TABLE IF EXISTS prediction;
DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS company;

CREATE TABLE company (
	Company_symbol VARCHAR(10) PRIMARY KEY,
	Company_name VARCHAR(50) NOT NULL
);

CREATE TABLE stock (
	Stock_symbol VARCHAR(10) NOT NULL,
	Stock_date DATE NOT NULL,
	Stock_open DOUBLE NOT NULL,
	Stock_close DOUBLE NOT NULL,
	Stock_high DOUBLE NOT NULL,
	Stock_low DOUBLE NOT NULL,
	Stock_volume BIGINT(10) NOT NULL,
	PRIMARY KEY (Stock_symbol, Stock_date),
	FOREIGN KEY (Stock_symbol) REFERENCES company (Company_symbol) ON DELETE CASCADE
);

CREATE TABLE prediction (
	Prediction_symbol VARCHAR(10) NOT NULL,
	Classifier VARCHAR(10) NOT NULL,
	Trading_window INT NOT NULL,
	Prediction_label_1 INT NOT NULL,
	Prediction_accuracy_1 DOUBLE NOT NULL,
	Prediction_label_3 INT NOT NULL,
	Prediction_accuracy_3 DOUBLE NOT NULL,
	Prediction_label_5 INT NOT NULL,
	Prediction_accuracy_5 DOUBLE NOT NULL,
	PRIMARY KEY (Prediction_symbol, Trading_window),
	FOREIGN KEY (Prediction_symbol) REFERENCES stock (Stock_symbol) ON DELETE CASCADE
);

CREATE TABLE features (
	Feature_symbol VARCHAR(10) NOT NULL,
	Feature_date DATE NOT NULL,
	Trading_window INT NOT NULL,
	Feature_RSI DOUBLE NOT NULL,
	Feature_K DOUBLE NOT NULL,
	Feature_R DOUBLE NOT NULL,
	Feature_SL DOUBLE NOT NULL,
	Feature_PROC DOUBLE NOT NULL,
	Feature_OBV DOUBLE NOT NULL,
	Feature_label DOUBLE NOT NULL,
	Feature_ema_12_c DOUBLE NOT NULL,
	Feature_ema_26_c DOUBLE NOT NULL,
	Feature_ema_9_macd DOUBLE NOT NULL,
	PRIMARY KEY (Feature_symbol, Feature_date, Trading_window),
	FOREIGN KEY (Feature_symbol) REFERENCES company (Company_symbol) ON DELETE CASCADE
);

-- TRIGGER AND PROCEDURE ON INSERTION OF NEW COMPANY
delimiter //
DROP PROCEDURE IF EXISTS onNewCompany//
CREATE PROCEDURE onNewCompany(IN symbol varchar(10))
BEGIN
	DECLARE x INT;
	DECLARE y INT;
	DECLARE Stock_date DATE;
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
	INSERT INTO prediction VALUES (symbol, "RF", 3, 0, 0, 0, 0, 0, 0);
	INSERT INTO prediction VALUES (symbol, "GBDT", 3, 0, 0, 0, 0, 0, 0);
	INSERT INTO prediction VALUES (symbol, "RF", 5, 0, 0, 0, 0, 0, 0);
	INSERT INTO prediction VALUES (symbol, "GBDT", 5, 0, 0, 0, 0, 0, 0);
	INSERT INTO prediction VALUES (symbol, "RF", 15, 0, 0, 0, 0, 0, 0);
	INSERT INTO prediction VALUES (symbol, "GBDT", 15, 0, 0, 0, 0, 0, 0);
	INSERT INTO prediction VALUES (symbol, "RF", 30, 0, 0, 0, 0, 0, 0);
	INSERT INTO prediction VALUES (symbol, "GBDT", 30, 0, 0, 0, 0, 0, 0);
	INSERT INTO prediction VALUES (symbol, "RF", 60, 0, 0, 0, 0, 0, 0);
	INSERT INTO prediction VALUES (symbol, "GBDT", 60, 0, 0, 0, 0, 0, 0);
	INSERT INTO prediction VALUES (symbol, "RF", 90, 0, 0, 0, 0, 0, 0);
	INSERT INTO prediction VALUES (symbol, "GBDT", 90, 0, 0, 0, 0, 0, 0);

END//

DROP trigger IF EXISTS onNewCompanyTrigger//
CREATE TRIGGER onNewCompanyTrigger
AFTER INSERT ON company
FOR EACH ROW
BEGIN
	call onNewCompany(NEW.Company_symbol);
END//
delimiter ;

INSERT into company values ("RCOM", "Reliance communications LTD"),("TATAMOTORS", "Tata Motors"),("WIPRO", "Wipro"),("INFY", "Infosys ltd");

select Stock_close, Feature_ema_12_c, Feature_ema_26_c from features JOIN stock on Feature_symbol = Stock_symbol and Feature_date = Stock_date where Feature_symbol = "INFY" and Trading_window=5;