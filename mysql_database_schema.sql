-- ====================================================================
-- PARKEASE DATABASE SCHEMA (MYSQL VERSION)
-- Target RDBMS: MySQL 8.0+ / MariaDB / phpMyAdmin / MySQL Workbench
-- Database: parkease_db
-- ====================================================================

CREATE DATABASE IF NOT EXISTS parkease_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE parkease_db;

-- 1. DROP TABLES (Reverse Dependency Order)
DROP TABLE IF EXISTS contact_messages;
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS rewards;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS parking_slots;
DROP TABLE IF EXISTS parking_floors;
DROP TABLE IF EXISTS parking_facilities;
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS users;

-- 2. CREATE TABLES

-- Table 1: Users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Table 2: User Profiles
CREATE TABLE user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    phone VARCHAR(25) NULL,
    vehicle_plate VARCHAR(30) NULL,
    vehicle_model VARCHAR(100) NULL,
    vehicle_type VARCHAR(30) NOT NULL DEFAULT 'sedan',
    loyalty_points INT NOT NULL DEFAULT 100,
    role ENUM('customer', 'staff', 'admin') NOT NULL DEFAULT 'customer',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table 3: Parking Facilities
CREATE TABLE parking_facilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL DEFAULT 'Mall',
    tagline VARCHAR(300) NULL,
    address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Delhi NCR',
    postal_code VARCHAR(20) NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    hourly_rate DECIMAL(10,2) NOT NULL DEFAULT 40.00,
    daily_rate DECIMAL(10,2) NOT NULL DEFAULT 250.00,
    currency VARCHAR(10) NOT NULL DEFAULT '₹',
    image_url VARCHAR(1000) NULL,
    description TEXT NULL,
    is_24_7 BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_featured BOOLEAN NOT NULL DEFAULT FALSE,
    rating DECIMAL(3,2) NOT NULL DEFAULT 4.80,
    review_count INT NOT NULL DEFAULT 0,
    ev_charging_available BOOLEAN NOT NULL DEFAULT TRUE,
    ev_charger_types VARCHAR(200) NULL,
    cancellation_hours_before INT NOT NULL DEFAULT 2,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_city (city),
    INDEX idx_category (category)
) ENGINE=InnoDB;

-- Table 4: Parking Floors
CREATE TABLE parking_floors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facility_id INT NOT NULL,
    floor_name VARCHAR(100) NOT NULL,
    floor_number INT NOT NULL,
    FOREIGN KEY (facility_id) REFERENCES parking_facilities(id) ON DELETE CASCADE,
    UNIQUE KEY uq_facility_floor (facility_id, floor_number)
) ENGINE=InnoDB;

-- Table 5: Parking Slots
CREATE TABLE parking_slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facility_id INT NOT NULL,
    floor_id INT NULL,
    slot_number VARCHAR(20) NOT NULL,
    vehicle_type VARCHAR(30) NOT NULL DEFAULT 'sedan',
    has_ev_charger BOOLEAN NOT NULL DEFAULT FALSE,
    is_handicap BOOLEAN NOT NULL DEFAULT FALSE,
    status ENUM('available', 'occupied', 'reserved', 'maintenance') NOT NULL DEFAULT 'available',
    price_multiplier DECIMAL(4,2) NOT NULL DEFAULT 1.00,
    FOREIGN KEY (facility_id) REFERENCES parking_facilities(id) ON DELETE CASCADE,
    FOREIGN KEY (floor_id) REFERENCES parking_floors(id) ON DELETE SET NULL,
    UNIQUE KEY uq_facility_slot (facility_id, slot_number),
    INDEX idx_status (status),
    INDEX idx_vehicle_type (vehicle_type)
) ENGINE=InnoDB;

-- Table 6: Bookings
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reference_code VARCHAR(30) NOT NULL UNIQUE,
    user_id INT NULL,
    guest_name VARCHAR(150) NOT NULL,
    guest_email VARCHAR(254) NOT NULL,
    guest_phone VARCHAR(30) NOT NULL,
    facility_id INT NOT NULL,
    floor_id INT NULL,
    slot_id INT NOT NULL,
    vehicle_plate VARCHAR(30) NOT NULL,
    vehicle_type VARCHAR(30) NOT NULL DEFAULT 'sedan',
    vehicle_model VARCHAR(100) NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    duration_hours DECIMAL(5,2) NOT NULL,
    hourly_rate DECIMAL(10,2) NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    service_fee DECIMAL(10,2) NOT NULL DEFAULT 15.00,
    tax_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total_price DECIMAL(10,2) NOT NULL,
    status ENUM('confirmed', 'checked_in', 'completed', 'cancelled') NOT NULL DEFAULT 'confirmed',
    qr_data TEXT NULL,
    cancellation_reason TEXT NULL,
    cancelled_at DATETIME NULL,
    checked_in_at DATETIME NULL,
    checked_out_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (facility_id) REFERENCES parking_facilities(id) ON DELETE RESTRICT,
    FOREIGN KEY (slot_id) REFERENCES parking_slots(id) ON DELETE RESTRICT,
    INDEX idx_timing (slot_id, start_time, end_time),
    INDEX idx_reference (reference_code)
) ENGINE=InnoDB;

-- Table 7: Payments
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE,
    transaction_id VARCHAR(100) NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    payment_method VARCHAR(50) NOT NULL DEFAULT 'UPI / NetBanking',
    status ENUM('successful', 'pending', 'failed', 'refunded') NOT NULL DEFAULT 'successful',
    provider VARCHAR(100) NOT NULL DEFAULT 'ParkEase India Pay',
    paid_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table 8: Reviews
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facility_id INT NOT NULL,
    user_id INT NOT NULL,
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (facility_id) REFERENCES parking_facilities(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table 9: Rewards
CREATE TABLE rewards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    points INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    description VARCHAR(300) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table 10: Favorites
CREATE TABLE favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    facility_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (facility_id) REFERENCES parking_facilities(id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_facility (user_id, facility_id)
) ENGINE=InnoDB;

-- Table 11: Contact Messages
CREATE TABLE contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    phone VARCHAR(30) NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
