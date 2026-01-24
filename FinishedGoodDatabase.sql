
-- Table to store finished goods information
CREATE TABLE tblFinishedGoods(
    FinishedGoodID UUID PRIMARY KEY DEFAULT uuidv7(),
    FinishedGoodName VARCHAR(150) NOT NULL
);

-- Table to store available finished good inventory
--FinishedGoodID referenced from tblFinishedGoods, If item deleted from tblFinishedGoods, it will also be deleted from this table
CREATE TABLE tblProductionInventory(
    FinishedGoodID UUID PRIMARY KEY REFERENCES tblFinishedGoods(FinishedGoodID) ON DELETE CASCADE,
    AvailableParts INT NOT NULL
);

--Table to store Production data, to view parts produced by order, this will take infeed data from sensor 
CREATE TABLE tblProductionData(
    OrderNumber UUID PRIMARY KEY DEFAULT uuidv7(),
    SensorID UUID NOT NULL,
    FinishedGoodID UUID NOT NULL,
    PartsProduced INT NOT NULL,
    ProductionOrderStartTime TIMESTAMP NOT NULL,
    ProductionOrderStartDate DATE NOT NULL,
    ProductionOrderEndTime TIMESTAMP NOT NULL,
    ProductionOrderEndDate DATE NOT NULL,

    --implementing constraints for foreign key variables
    CONSTRAINT FKFinishedGoodID FOREIGN KEY (FinishedGoodID) REFERENCES tblFinishedGoods(FinishedGoodID) ON DELETE CASCADE
);
