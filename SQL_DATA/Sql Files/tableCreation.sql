-- =========================
--  PRODUCTS
-- =========================
CREATE TABLE Products (
    index SERIAL PRIMARY KEY,
    productName VARCHAR(255) UNIQUE NOT NULL
);

-- =========================
--  CUSTOMERS
-- =========================
CREATE TABLE Customers (
    customerIndex SERIAL PRIMARY KEY,
    customerName VARCHAR(255) UNIQUE NOT NULL
);

-- =========================
--  STATE REGIONS
-- =========================
CREATE TABLE stateRegions (
    stateCode VARCHAR(10) PRIMARY KEY,
    state VARCHAR(255),
    region VARCHAR(255)
);

-- =========================
--  REGIONS
-- =========================
CREATE TABLE Regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    county VARCHAR(255),
    stateCode VARCHAR(10) NOT NULL,
    state VARCHAR(255),
    type VARCHAR(100),
    latitude DECIMAL(10,5),
    longitude DECIMAL(10,5),
    areaCode INT,
    population INT,
    households INT,
    medianIncome INT,
    landArea INT,
    waterArea INT,
    timeZone VARCHAR(50),
	CONSTRAINT fk_regions_stateCode
        FOREIGN KEY (stateCode)
        REFERENCES stateRegions(stateCode)
);

-- =========================
--  BUDGET
-- =========================
CREATE TABLE Budget (
    productName VARCHAR(255) PRIMARY KEY,
    budget DECIMAL(11,3),

    CONSTRAINT fk_budget_productName
        FOREIGN KEY (productName)
        REFERENCES Products(productName)
);

-- =========================
--  SALES ORDER
-- =========================
CREATE TABLE SalesOrder (
    orderNumber VARCHAR(100) PRIMARY KEY,
    orderDate DATE,

    customerNameIndex INT NOT NULL,
    channel VARCHAR(100),
    currencyCode VARCHAR(10),
    warehouseCode VARCHAR(50),

    deliveryRegionIndex INT NOT NULL,
    productDescriptionIndex INT NOT NULL,

    orderQuantity INT,
    unitPrice DECIMAL(6,2),
    lineTotal DECIMAL(7,2),
    totalUnitCost DECIMAL(7,3),

    CONSTRAINT fk_sales_customer
        FOREIGN KEY (customerNameIndex)
        REFERENCES Customers(customerIndex),

    CONSTRAINT fk_sales_product
        FOREIGN KEY (productDescriptionIndex)
        REFERENCES Products(index),

    CONSTRAINT fk_sales_region
        FOREIGN KEY (deliveryRegionIndex)
        REFERENCES Regions(id)
);
