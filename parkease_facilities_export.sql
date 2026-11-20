-- ====================================================================
-- PARKEASE SQL SERVER FACILITY EXPORT & SYNC SCRIPT
-- Generated automatically from ParkEase Admin Portal
-- Compatible with Microsoft SQL Server 2025 / Azure Data Studio
-- Database: ParkEaseDB
-- ====================================================================
USE [ParkEaseDB];
GO

SET IDENTITY_INSERT ParkingFacilities ON;
GO

-- Facility: Test Indian MLCP Hub (ID: 1)
IF NOT EXISTS (SELECT 1 FROM ParkingFacilities WHERE slug = N'test-indian-mlcp')
BEGIN
    INSERT INTO ParkingFacilities (
        id, name, slug, category, tagline, address, city, state, postal_code,
        latitude, longitude, hourly_rate, daily_rate, currency, image_url,
        description, is_24_7, is_active, is_featured, rating, review_count,
        amenities_json, ev_charging_available, ev_charger_types, cancellation_hours_before
    ) VALUES (
        1, N'Test Indian MLCP Hub', N'test-indian-mlcp', N'Parking Deck', N'Premium parking in New Delhi (Delhi)',
        N'100 Barakhamba Road', N'New Delhi (Delhi)', N'Delhi NCR', N'110001',
        40.712800, -74.006000, 50.00, 300.00, N'₹',
        N'', N'Secure multi-level parking facility in New Delhi (Delhi) with 24/7 security and fast EV charging.', 1,
        1, 0, 4.80, 24,
        N'[]', 1,
        N'Type 2 & CCS2 Fast Charge', 2
    );
END
ELSE
BEGIN
    UPDATE ParkingFacilities SET
        name = N'Test Indian MLCP Hub',
        tagline = N'Premium parking in New Delhi (Delhi)',
        address = N'100 Barakhamba Road',
        city = N'New Delhi (Delhi)',
        postal_code = N'110001',
        latitude = 40.712800,
        longitude = -74.006000,
        hourly_rate = 50.00,
        daily_rate = 300.00,
        image_url = N'',
        description = N'Secure multi-level parking facility in New Delhi (Delhi) with 24/7 security and fast EV charging.',
        is_24_7 = 1,
        is_active = 1,
        is_featured = 0,
        amenities_json = N'[]',
        ev_charging_available = 1,
        ev_charger_types = N'Type 2 & CCS2 Fast Charge'
    WHERE slug = N'test-indian-mlcp';
END
GO

-- Facility: Aerocity Worldmark SkyDeck Parking (Renovated & Expanded) (ID: 2)
IF NOT EXISTS (SELECT 1 FROM ParkingFacilities WHERE slug = N'aerocity-worldmark-skydeck')
BEGIN
    INSERT INTO ParkingFacilities (
        id, name, slug, category, tagline, address, city, state, postal_code,
        latitude, longitude, hourly_rate, daily_rate, currency, image_url,
        description, is_24_7, is_active, is_featured, rating, review_count,
        amenities_json, ev_charging_available, ev_charger_types, cancellation_hours_before
    ) VALUES (
        2, N'Aerocity Worldmark SkyDeck Parking (Renovated & Expanded)', N'aerocity-worldmark-skydeck', N'Parking Deck', N'Upgraded 24/7 luxury parking with premium EV lounge',
        N'Asset Area 8, Hospitality District, Aerocity', N'New Delhi (Delhi)', N'Delhi NCR', N'110037',
        28.551000, 77.121000, 90.00, 500.00, N'₹',
        N'https://images.unsplash.com/photo-1506521781263-d8422e82f27a', N'Newly renovated luxury multi-level parking deck with biometric barriers and VIP valet services.', 1,
        1, 1, 4.80, 24,
        N'["Covered Parking", "24/7 CCTV", "VIP Valet", "Fast EV Charging", "Car Spa"]', 1,
        N'CCS2 120kW Supercharger', 2
    );
END
ELSE
BEGIN
    UPDATE ParkingFacilities SET
        name = N'Aerocity Worldmark SkyDeck Parking (Renovated & Expanded)',
        tagline = N'Upgraded 24/7 luxury parking with premium EV lounge',
        address = N'Asset Area 8, Hospitality District, Aerocity',
        city = N'New Delhi (Delhi)',
        postal_code = N'110037',
        latitude = 28.551000,
        longitude = 77.121000,
        hourly_rate = 90.00,
        daily_rate = 500.00,
        image_url = N'https://images.unsplash.com/photo-1506521781263-d8422e82f27a',
        description = N'Newly renovated luxury multi-level parking deck with biometric barriers and VIP valet services.',
        is_24_7 = 1,
        is_active = 1,
        is_featured = 1,
        amenities_json = N'["Covered Parking", "24/7 CCTV", "VIP Valet", "Fast EV Charging", "Car Spa"]',
        ev_charging_available = 1,
        ev_charger_types = N'CCS2 120kW Supercharger'
    WHERE slug = N'aerocity-worldmark-skydeck';
END
GO

SET IDENTITY_INSERT ParkingFacilities OFF;
GO
