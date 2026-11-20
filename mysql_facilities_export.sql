-- ====================================================================
-- PARKEASE MYSQL FACILITY EXPORT & SYNC SCRIPT
-- Generated automatically from ParkEase Admin Portal
-- Compatible with MySQL 8.0+
-- Database: ParkEaseDB
-- ====================================================================
USE ParkEaseDB;

INSERT INTO ParkingFacilities (
    id, name, slug, category, tagline, address, city, state, postal_code,
    latitude, longitude, hourly_rate, daily_rate, currency, image_url,
    description, is_24_7, is_active, is_featured, rating, review_count,
    amenities_json, ev_charging_available, ev_charger_types, cancellation_hours_before
) VALUES (
    1, 'Test Indian MLCP Hub', 'test-indian-mlcp', 'Parking Deck', 'Premium parking in New Delhi (Delhi)',
    '100 Barakhamba Road', 'New Delhi (Delhi)', 'Delhi NCR', '110001',
    40.712800, -74.006000, 50.00, 300.00, '₹',
    '', 'Secure multi-level parking facility in New Delhi (Delhi) with 24/7 security and fast EV charging.', 1,
    1, 0, 4.80, 24,
    '[]', 1,
    'Type 2 & CCS2 Fast Charge', 2
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    tagline = VALUES(tagline),
    address = VALUES(address),
    city = VALUES(city),
    latitude = VALUES(latitude),
    longitude = VALUES(longitude),
    hourly_rate = VALUES(hourly_rate),
    daily_rate = VALUES(daily_rate),
    image_url = VALUES(image_url),
    description = VALUES(description),
    is_active = VALUES(is_active),
    amenities_json = VALUES(amenities_json);

INSERT INTO ParkingFacilities (
    id, name, slug, category, tagline, address, city, state, postal_code,
    latitude, longitude, hourly_rate, daily_rate, currency, image_url,
    description, is_24_7, is_active, is_featured, rating, review_count,
    amenities_json, ev_charging_available, ev_charger_types, cancellation_hours_before
) VALUES (
    2, 'Aerocity Worldmark SkyDeck Parking (Renovated & Expanded)', 'aerocity-worldmark-skydeck', 'Parking Deck', 'Upgraded 24/7 luxury parking with premium EV lounge',
    'Asset Area 8, Hospitality District, Aerocity', 'New Delhi (Delhi)', 'Delhi NCR', '110037',
    28.551000, 77.121000, 90.00, 500.00, '₹',
    'https://images.unsplash.com/photo-1506521781263-d8422e82f27a', 'Newly renovated luxury multi-level parking deck with biometric barriers and VIP valet services.', 1,
    1, 1, 4.80, 24,
    '["Covered Parking", "24/7 CCTV", "VIP Valet", "Fast EV Charging", "Car Spa"]', 1,
    'CCS2 120kW Supercharger', 2
)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    tagline = VALUES(tagline),
    address = VALUES(address),
    city = VALUES(city),
    latitude = VALUES(latitude),
    longitude = VALUES(longitude),
    hourly_rate = VALUES(hourly_rate),
    daily_rate = VALUES(daily_rate),
    image_url = VALUES(image_url),
    description = VALUES(description),
    is_active = VALUES(is_active),
    amenities_json = VALUES(amenities_json);
