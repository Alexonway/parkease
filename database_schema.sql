-- ====================================================================
-- PARKEASE DATABASE SCHEMA & INITIAL DATA (SELF-CONTAINED)
-- Target RDBMS: Microsoft SQL Server / Azure Data Studio & MySQL
-- Database: ParkEaseDB
-- Note: Completely self-contained. All data is internally generated.
-- ====================================================================

USE ParkEaseDB;
GO

-- 1. DROP EXISTING TABLES IN REVERSE DEPENDENCY ORDER (FOR CLEAN RE-CREATION)
IF OBJECT_ID('ContactMessages', 'U') IS NOT NULL DROP TABLE ContactMessages;
IF OBJECT_ID('Favorites', 'U') IS NOT NULL DROP TABLE Favorites;
IF OBJECT_ID('Rewards', 'U') IS NOT NULL DROP TABLE Rewards;
IF OBJECT_ID('Reviews', 'U') IS NOT NULL DROP TABLE Reviews;
IF OBJECT_ID('Payments', 'U') IS NOT NULL DROP TABLE Payments;
IF OBJECT_ID('Bookings', 'U') IS NOT NULL DROP TABLE Bookings;
IF OBJECT_ID('ParkingSlots', 'U') IS NOT NULL DROP TABLE ParkingSlots;
IF OBJECT_ID('ParkingFloors', 'U') IS NOT NULL DROP TABLE ParkingFloors;
IF OBJECT_ID('ParkingFacilities', 'U') IS NOT NULL DROP TABLE ParkingFacilities;
IF OBJECT_ID('UserProfiles', 'U') IS NOT NULL DROP TABLE UserProfiles;
IF OBJECT_ID('Users', 'U') IS NOT NULL DROP TABLE Users;
GO

-- ====================================================================
-- 2. CREATE ENTITIES & TABLES WITH CONSTRAINTS AND INDEXES
-- ====================================================================

-- TABLE 1: Users (Core Authentication)
CREATE TABLE Users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(150) NOT NULL UNIQUE,
    email NVARCHAR(254) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    first_name NVARCHAR(150) NOT NULL,
    last_name NVARCHAR(150) NOT NULL,
    is_staff BIT NOT NULL DEFAULT 0,
    is_superuser BIT NOT NULL DEFAULT 0,
    is_active BIT NOT NULL DEFAULT 1,
    date_joined DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- TABLE 2: UserProfiles (Extended Driver / Staff Profile)
CREATE TABLE UserProfiles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    phone NVARCHAR(25) NULL,
    vehicle_plate NVARCHAR(30) NULL,
    vehicle_model NVARCHAR(100) NULL,
    vehicle_type NVARCHAR(30) NOT NULL DEFAULT 'sedan',
    loyalty_points INT NOT NULL DEFAULT 100,
    role NVARCHAR(20) NOT NULL DEFAULT 'customer',
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_UserProfiles_Users FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    CONSTRAINT CHK_UserProfiles_Role CHECK (role IN ('customer', 'staff', 'admin'))
);

-- TABLE 3: ParkingFacilities (Malls, Hospitals, Airports, Railway Stations)
CREATE TABLE ParkingFacilities (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(200) NOT NULL,
    slug NVARCHAR(200) NOT NULL UNIQUE,
    category NVARCHAR(50) NOT NULL DEFAULT 'Mall', -- 'Airport', 'Mall', 'Hospital', 'Railway', 'Corporate'
    tagline NVARCHAR(300) NULL,
    address NVARCHAR(500) NOT NULL,
    city NVARCHAR(100) NOT NULL,
    state NVARCHAR(100) NOT NULL DEFAULT 'Delhi NCR',
    postal_code NVARCHAR(20) NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    hourly_rate DECIMAL(10,2) NOT NULL DEFAULT 40.00,
    daily_rate DECIMAL(10,2) NOT NULL DEFAULT 250.00,
    currency NVARCHAR(10) NOT NULL DEFAULT '₹',
    image_url NVARCHAR(1000) NULL,
    description NVARCHAR(MAX) NULL,
    is_24_7 BIT NOT NULL DEFAULT 1,
    is_active BIT NOT NULL DEFAULT 1,
    is_featured BIT NOT NULL DEFAULT 0,
    rating DECIMAL(3,2) NOT NULL DEFAULT 4.80,
    review_count INT NOT NULL DEFAULT 0,
    amenities_json NVARCHAR(MAX) NULL,
    ev_charging_available BIT NOT NULL DEFAULT 1,
    ev_charger_types NVARCHAR(200) NULL,
    cancellation_hours_before INT NOT NULL DEFAULT 2,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- TABLE 4: ParkingFloors (Multi-Deck Structure: P1, P2, P3, etc.)
CREATE TABLE ParkingFloors (
    id INT IDENTITY(1,1) PRIMARY KEY,
    facility_id INT NOT NULL,
    floor_name NVARCHAR(100) NOT NULL,
    floor_number INT NOT NULL,
    CONSTRAINT FK_ParkingFloors_Facility FOREIGN KEY (facility_id) REFERENCES ParkingFacilities(id) ON DELETE CASCADE,
    CONSTRAINT UQ_Facility_Floor UNIQUE (facility_id, floor_number)
);

-- TABLE 5: ParkingSlots (Individual Parking Bays)
CREATE TABLE ParkingSlots (
    id INT IDENTITY(1,1) PRIMARY KEY,
    facility_id INT NOT NULL,
    floor_id INT NULL,
    slot_number NVARCHAR(20) NOT NULL,
    vehicle_type NVARCHAR(30) NOT NULL DEFAULT 'sedan', -- 'sedan', 'suv', 'ev', 'handicap', 'motorcycle'
    has_ev_charger BIT NOT NULL DEFAULT 0,
    is_handicap BIT NOT NULL DEFAULT 0,
    status NVARCHAR(20) NOT NULL DEFAULT 'available', -- 'available', 'occupied', 'reserved', 'maintenance'
    price_multiplier DECIMAL(4,2) NOT NULL DEFAULT 1.00,
    CONSTRAINT FK_ParkingSlots_Facility FOREIGN KEY (facility_id) REFERENCES ParkingFacilities(id) ON DELETE CASCADE,
    CONSTRAINT FK_ParkingSlots_Floor FOREIGN KEY (floor_id) REFERENCES ParkingFloors(id) ON DELETE NO ACTION,
    CONSTRAINT UQ_Facility_Slot UNIQUE (facility_id, slot_number),
    CONSTRAINT CHK_Slot_Status CHECK (status IN ('available', 'occupied', 'reserved', 'maintenance'))
);

-- TABLE 6: Bookings (Driver Reservations with Digital Ticket)
CREATE TABLE Bookings (
    id INT IDENTITY(1,1) PRIMARY KEY,
    reference_code NVARCHAR(30) NOT NULL UNIQUE,
    user_id INT NULL,
    guest_name NVARCHAR(150) NOT NULL,
    guest_email NVARCHAR(254) NOT NULL,
    guest_phone NVARCHAR(30) NOT NULL,
    facility_id INT NOT NULL,
    floor_id INT NULL,
    slot_id INT NOT NULL,
    vehicle_plate NVARCHAR(30) NOT NULL,
    vehicle_type NVARCHAR(30) NOT NULL DEFAULT 'sedan',
    vehicle_model NVARCHAR(100) NULL,
    start_time DATETIME2 NOT NULL,
    end_time DATETIME2 NOT NULL,
    duration_hours DECIMAL(5,2) NOT NULL,
    hourly_rate DECIMAL(10,2) NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    service_fee DECIMAL(10,2) NOT NULL DEFAULT 15.00,
    tax_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_price DECIMAL(10,2) NOT NULL,
    status NVARCHAR(30) NOT NULL DEFAULT 'confirmed', -- 'confirmed', 'checked_in', 'completed', 'cancelled'
    qr_data NVARCHAR(MAX) NULL,
    qr_image_base64 NVARCHAR(MAX) NULL,
    cancellation_reason NVARCHAR(MAX) NULL,
    cancelled_at DATETIME2 NULL,
    checked_in_at DATETIME2 NULL,
    checked_out_at DATETIME2 NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_Bookings_User FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE SET NULL,
    CONSTRAINT FK_Bookings_Facility FOREIGN KEY (facility_id) REFERENCES ParkingFacilities(id) ON DELETE NO ACTION,
    CONSTRAINT FK_Bookings_Slot FOREIGN KEY (slot_id) REFERENCES ParkingSlots(id) ON DELETE NO ACTION,
    CONSTRAINT CHK_Booking_Status CHECK (status IN ('confirmed', 'checked_in', 'completed', 'cancelled'))
);

-- TABLE 7: Payments (Idempotent Transaction Ledger)
CREATE TABLE Payments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE,
    transaction_id NVARCHAR(100) NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL,
    currency NVARCHAR(10) NOT NULL DEFAULT 'INR',
    payment_method NVARCHAR(50) NOT NULL DEFAULT 'UPI / NetBanking',
    status NVARCHAR(30) NOT NULL DEFAULT 'successful', -- 'successful', 'pending', 'failed', 'refunded'
    provider NVARCHAR(100) NOT NULL DEFAULT 'ParkEase Secure Pay',
    paid_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_Payments_Booking FOREIGN KEY (booking_id) REFERENCES Bookings(id) ON DELETE CASCADE,
    CONSTRAINT CHK_Payment_Status CHECK (status IN ('successful', 'pending', 'failed', 'refunded'))
);

-- TABLE 8: Reviews (Verified Driver Experience)
CREATE TABLE Reviews (
    id INT IDENTITY(1,1) PRIMARY KEY,
    facility_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL,
    comment NVARCHAR(MAX) NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_Reviews_Facility FOREIGN KEY (facility_id) REFERENCES ParkingFacilities(id) ON DELETE CASCADE,
    CONSTRAINT FK_Reviews_User FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    CONSTRAINT CHK_Rating_Range CHECK (rating >= 1 AND rating <= 5)
);

-- TABLE 9: Rewards (Loyalty Ledger)
CREATE TABLE Rewards (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    points INT NOT NULL,
    action NVARCHAR(100) NOT NULL,
    description NVARCHAR(300) NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_Rewards_User FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- TABLE 10: Favorites (Driver Saved Facilities)
CREATE TABLE Favorites (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    facility_id INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_Favorites_User FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    CONSTRAINT FK_Favorites_Facility FOREIGN KEY (facility_id) REFERENCES ParkingFacilities(id) ON DELETE NO ACTION,
    CONSTRAINT UQ_User_Favorite UNIQUE (user_id, facility_id)
);

-- TABLE 11: ContactMessages (Concierge Inquiries & Support)
CREATE TABLE ContactMessages (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(150) NOT NULL,
    email NVARCHAR(254) NOT NULL,
    phone NVARCHAR(30) NULL,
    subject NVARCHAR(200) NOT NULL,
    message NVARCHAR(MAX) NOT NULL,
    is_resolved BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
GO

-- ====================================================================
-- 3. PERFORMANCE INDEXES
-- ====================================================================
CREATE INDEX IX_Facilities_City ON ParkingFacilities(city);
CREATE INDEX IX_Facilities_Category ON ParkingFacilities(category);
CREATE INDEX IX_ParkingSlots_Status ON ParkingSlots(status);
CREATE INDEX IX_ParkingSlots_VehicleType ON ParkingSlots(vehicle_type);
CREATE INDEX IX_Bookings_Reference ON Bookings(reference_code);
CREATE INDEX IX_Bookings_Status ON Bookings(status);
CREATE INDEX IX_Bookings_Timing ON Bookings(slot_id, start_time, end_time);
CREATE INDEX IX_Payments_Transaction ON Payments(transaction_id);
GO

-- ====================================================================
-- 4. INSERT SELF-CONTAINED PROJECT SEED DATA (DELHI, UP, HARYANA)
-- ====================================================================

-- 4.1 USERS
INSERT INTO Users (username, email, password_hash, first_name, last_name, is_staff, is_superuser)
VALUES 
('admin', 'admin@parkease.in', 'pbkdf2_sha256$870000$AdminHash$Placeholder', 'Rajesh', 'Sharma', 1, 1),
('alex_driver', 'arjun.verma@example.in', 'pbkdf2_sha256$870000$DriverHash$Placeholder', 'Arjun', 'Verma', 0, 0);

-- 4.2 PROFILES
INSERT INTO UserProfiles (user_id, phone, vehicle_plate, vehicle_model, vehicle_type, loyalty_points, role)
VALUES 
(1, '+91 98110 23456', '', 'Security Fleet Mahindra Scorpio', 'suv', 1500, 'admin'),
(2, '+91 98765 43210', 'DL-01-CZ-7842', 'Tata Nexon EV Max', 'ev', 450, 'customer');

-- 4.3 FACILITIES (Airport, Malls, Hospitals, Railway, Corporate)
INSERT INTO ParkingFacilities 
(name, slug, category, tagline, address, city, state, postal_code, latitude, longitude, hourly_rate, daily_rate, currency, image_url, description, is_24_7, is_active, is_featured, rating, review_count, ev_charging_available, ev_charger_types)
VALUES
(
    'IGI Airport Terminal 3 SkyPark MLCP',
    'igi-airport-t3-skypark',
    'Airport',
    'World-class 24/7 multi-level terminal parking with direct skywalk to T3 departures.',
    'Terminal 3, Indira Gandhi International Airport, Palam',
    'New Delhi (Delhi)', 'Delhi', '110037',
    28.5562, 77.1000, 100.00, 600.00, N'₹',
    'https://images.unsplash.com/photo-1506521781263-d8422e82f27a?auto=format&fit=crop&w=1200&q=80',
    'Official multi-level automated facility for Delhi International Airport Terminal 3 with ANPR, flight status displays, and fast EV chargers.',
    1, 1, 1, 4.90, 428, 1, 'CCS2 & Bharat DC-001 (60 kW Fast Charge)'
),
(
    'DLF Mall of India Smart Multi-Deck Garage',
    'dlf-mall-of-india-noida',
    'Mall',
    'Indias largest mall parking deck with automated bay guidance and valet.',
    'Sector 18, Noida Express Highway, Gautam Buddha Nagar',
    'Noida (UP)', 'Uttar Pradesh', '201301',
    28.5677, 77.3211, 50.00, 280.00, N'₹',
    'https://images.unsplash.com/photo-1590674899484-d5640e854abe?auto=format&fit=crop&w=1200&q=80',
    'Massive 7-tier multi-level parking facility at Sector 18 Noida with Tata Power EV fast charging and direct mall escalators.',
    0, 1, 1, 4.80, 356, 1, 'Tata Power EZ Charge (CCS2 & Type 2)'
),
(
    'Select CITYWALK & DLF Avenue Underground Deck',
    'select-citywalk-saket',
    'Mall',
    'Luxury underground shopping and dining parking in South Delhi.',
    'A-3, District Centre, Saket, South Delhi',
    'South Delhi (Delhi)', 'Delhi', '110017',
    28.5284, 77.2185, 60.00, 350.00, N'₹',
    'https://images.unsplash.com/photo-1563720223185-11003d516935?auto=format&fit=crop&w=1200&q=80',
    'Underground climate-controlled executive parking serving the premier shopping district of South Delhi with optical QR barrier gates.',
    1, 1, 1, 4.90, 289, 1, 'Statiq & Kazam (CCS2 & AC Type 2)'
),
(
    'AIIMS New Delhi Emergency & OPD Multi-Level Facility',
    'aiims-new-delhi-parking',
    'Hospital',
    'Dedicated priority medical parking with stretcher-friendly elevator bays.',
    'Sri Aurobindo Marg, Ansari Nagar East, New Delhi',
    'New Delhi (Delhi)', 'Delhi', '110029',
    28.5672, 77.2100, 30.00, 180.00, N'₹',
    'https://images.unsplash.com/photo-1573348722427-f1d6819fdf98?auto=format&fit=crop&w=1200&q=80',
    'Designed specifically for patients, doctors, and emergency visitors with priority ambulance clearance corridors.',
    1, 1, 1, 4.70, 512, 0, 'None'
),
(
    'Medanta The Medicity Super-Specialty Hospital Deck',
    'medanta-the-medicity-gurugram',
    'Hospital',
    'Hassle-free sheltered hospital parking right by the main admission lobby.',
    'CH Bakhtawar Singh Road, Sector 38, Gurugram',
    'Gurugram (Haryana)', 'Haryana', '122001',
    28.4393, 77.0425, 40.00, 220.00, N'₹',
    'https://images.unsplash.com/photo-1545454675-3531b543be5d?auto=format&fit=crop&w=1200&q=80',
    'Multi-story modern car parking adjacent to Medanta hospital towers with patient buggy transfer shuttles.',
    1, 1, 0, 4.80, 195, 1, 'Jio-bp Pulse (CCS2 50kW)'
),
(
    'New Delhi Railway Station (NDLS) Ajmeri Gate Executive Parking',
    'ndls-ajmeri-gate-parking',
    'Railway',
    'Guaranteed rail commuter parking steps away from Platform 16 and Airport Express Metro.',
    'Bhavbhuti Marg, Ajmeri Gate Side, New Delhi Railway Station',
    'Central Delhi (Delhi)', 'Delhi', '110006',
    28.6415, 77.2210, 40.00, 240.00, N'₹',
    'https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd?auto=format&fit=crop&w=1200&q=80',
    'Direct foot-over-bridge access to all 16 platforms and the Orange Line Airport Express Metro with 24/7 guarded parking.',
    1, 1, 1, 4.60, 640, 1, 'EESL Multi-Standard Fast Charger'
),
(
    'DLF Cyber Hub & Cyber City Automated Executive Deck',
    'dlf-cyber-hub-gurugram',
    'Corporate',
    'Premium corporate hub and fine dining parking with 150kW hyper-chargers.',
    'DLF Cyber City, Phase 2, Sector 24, Gurugram',
    'Gurugram (Haryana)', 'Haryana', '122002',
    28.4950, 77.0895, 60.00, 380.00, N'₹',
    'https://images.unsplash.com/photo-1558441719-f90351336140?auto=format&fit=crop&w=1200&q=80',
    'Accommodates executive sedans and electric vehicles with dual-gun 150kW DC hyperchargers and Rapid Metro footbridge integration.',
    1, 1, 1, 4.90, 382, 1, 'Jio-bp & Fortum (150kW Dual Gun CCS2)'
),
(
    'Anand Vihar Mega Rail & ISBT Transit Terminal Deck',
    'anand-vihar-transit-terminal',
    'Railway',
    'Integrated eastern gateway parking linking Vande Bharat trains, Blue Line Metro & ISBT.',
    'Anand Vihar Railway Station Complex, Kaushambi Border',
    'East Delhi (Delhi)', 'Delhi', '110092',
    28.6502, 77.3155, 35.00, 200.00, N'₹',
    'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?auto=format&fit=crop&w=1200&q=80',
    'Multi-modal transit parking connecting East Delhi, Ghaziabad, and Noida commuters catching long-distance trains or buses.',
    1, 1, 0, 4.70, 275, 1, 'Tata Power EZ Charge (CCS2)'
);

-- 4.4 FLOORS FOR FACILITY 1 (IGI Airport T3)
INSERT INTO ParkingFloors (facility_id, floor_name, floor_number)
VALUES 
(1, 'Level P1 - Arrivals & EV Deck', 1),
(1, 'Level P2 - Executive Valet', 2),
(1, 'Level P3 - Long-Term Sky Deck', 3);

-- 4.5 SLOTS FOR FACILITY 1 FLOOR 1
INSERT INTO ParkingSlots (facility_id, floor_id, slot_number, vehicle_type, has_ev_charger, is_handicap, status, price_multiplier)
VALUES
(1, 1, 'A-01', 'handicap', 0, 1, 'available', 1.00),
(1, 1, 'A-02', 'handicap', 0, 1, 'available', 1.00),
(1, 1, 'A-03', 'ev', 1, 0, 'occupied', 1.20),
(1, 1, 'A-04', 'ev', 1, 0, 'available', 1.20),
(1, 1, 'A-05', 'ev', 1, 0, 'available', 1.20),
(1, 1, 'A-06', 'suv', 0, 0, 'available', 1.15),
(1, 1, 'A-07', 'suv', 0, 0, 'occupied', 1.15),
(1, 1, 'A-08', 'sedan', 0, 0, 'available', 1.00),
(1, 1, 'A-09', 'sedan', 0, 0, 'available', 1.00),
(1, 1, 'A-10', 'motorcycle', 0, 0, 'available', 0.70);

-- 4.6 SAMPLE VERIFIED BOOKING
INSERT INTO Bookings 
(reference_code, user_id, guest_name, guest_email, guest_phone, facility_id, floor_id, slot_id, vehicle_plate, vehicle_type, vehicle_model, start_time, end_time, duration_hours, hourly_rate, base_price, service_fee, tax_amount, discount_amount, total_price, status, qr_data)
VALUES
('PK-892401', 2, 'Arjun Verma', 'arjun.verma@example.in', '+91 98765 43210', 1, 1, 3, 'DL-01-CZ-7842', 'ev', 'Tata Nexon EV Max', DATEADD(hour, 1, GETDATE()), DATEADD(hour, 4, GETDATE()), 3.00, 120.00, 360.00, 15.00, 30.00, 50.00, 355.00, 'confirmed', 'http://127.0.0.1:8000/verify-ticket/PK-892401/');

-- 4.7 PAYMENT
INSERT INTO Payments 
(booking_id, transaction_id, amount, currency, payment_method, status, provider)
VALUES
(1, 'TXN_UPI_99481237IND', 355.00, 'INR', 'UPI (Google Pay / PhonePe)', 'successful', 'ParkEase India Pay');

-- 4.8 REVIEWS
INSERT INTO Reviews (facility_id, user_id, rating, comment)
VALUES
(1, 2, 5, N'The skywalk to Terminal 3 departures was seamless. The 60kW DC EV charger had my car fully charged upon return!'),
(2, 2, 5, N'Very spacious parking bays at DLF Mall of India. No waiting at the boom barrier thanks to the QR pass scanner.');

-- 4.9 REWARDS
INSERT INTO Rewards (user_id, points, action, description)
VALUES 
(2, 100, 'Welcome Bonus', 'New Member Welcome Bonus in ParkEase Club'),
(2, 50, 'Booking Reward', 'Bonus points for reserving bay at IGI Airport T3');

-- 4.10 FAVORITES
INSERT INTO Favorites (user_id, facility_id)
VALUES (2, 1);
GO

-- ====================================================================
-- VERIFY EXECUTION
-- ====================================================================
SELECT 'Users' AS TableName, COUNT(*) AS RecordCount FROM Users
UNION ALL
SELECT 'Facilities', COUNT(*) FROM ParkingFacilities
UNION ALL
SELECT 'Floors', COUNT(*) FROM ParkingFloors
UNION ALL
SELECT 'Slots', COUNT(*) FROM ParkingSlots
UNION ALL
SELECT 'Bookings', COUNT(*) FROM Bookings
UNION ALL
SELECT 'Payments', COUNT(*) FROM Payments
UNION ALL
SELECT 'Reviews', COUNT(*) FROM Reviews;
GO
