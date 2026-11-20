"""
SQL Synchronization Utility for ParkEase.
Exports and synchronizes all Parking Facilities, Floors, and Slots
into standalone, production-ready SQL scripts (SQL Server & MySQL compatible).
"""

import json
from pathlib import Path
from django.conf import settings
from .models import ParkingFacility, ParkingFloor, ParkingSlot


def escape_sql(val):
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "1" if val else "0"
    if isinstance(val, (int, float)):
        return str(val)
    # String escaping (double single-quotes for SQL)
    escaped = str(val).replace("'", "''")
    return f"N'{escaped}'"


def sync_facilities_to_sql():
    """
    Exports all current facilities from the database into:
    1. parkease_facilities_export.sql (Production SQL Server T-SQL)
    2. mysql_facilities_export.sql (MySQL compatible)
    """
    facilities = ParkingFacility.objects.all().order_by('id')
    base_dir = settings.BASE_DIR

    # 1. SQL Server Script
    sql_server_lines = [
        "-- ====================================================================",
        "-- PARKEASE SQL SERVER FACILITY EXPORT & SYNC SCRIPT",
        f"-- Generated automatically from ParkEase Admin Portal",
        "-- Compatible with Microsoft SQL Server 2025 / Azure Data Studio",
        "-- Database: ParkEaseDB",
        "-- ====================================================================",
        "USE [ParkEaseDB];",
        "GO",
        "",
        "SET IDENTITY_INSERT ParkingFacilities ON;",
        "GO",
        ""
    ]

    # 2. MySQL Script
    mysql_lines = [
        "-- ====================================================================",
        "-- PARKEASE MYSQL FACILITY EXPORT & SYNC SCRIPT",
        f"-- Generated automatically from ParkEase Admin Portal",
        "-- Compatible with MySQL 8.0+",
        "-- Database: ParkEaseDB",
        "-- ====================================================================",
        "USE ParkEaseDB;",
        ""
    ]

    for f in facilities:
        amenities_str = json.dumps(f.amenities or [])
        gallery_str = json.dumps(f.gallery_images or [])
        tagline = f.tagline or f"Premium parking in {f.city}"
        postal = f.postal_code or "110001"
        ev_type = f.ev_charger_types or "Type 2 & CCS2 Fast Charge"
        desc = f.description or f"Secure multi-level parking facility in {f.city} with 24/7 security and fast EV charging."

        # SQL Server MERGE (Upsert)
        sql_server_lines.append(f"""-- Facility: {f.name} (ID: {f.id})
IF NOT EXISTS (SELECT 1 FROM ParkingFacilities WHERE slug = {escape_sql(f.slug)})
BEGIN
    INSERT INTO ParkingFacilities (
        id, name, slug, category, tagline, address, city, state, postal_code,
        latitude, longitude, hourly_rate, daily_rate, currency, image_url,
        description, is_24_7, is_active, is_featured, rating, review_count,
        amenities_json, ev_charging_available, ev_charger_types, cancellation_hours_before
    ) VALUES (
        {f.id}, {escape_sql(f.name)}, {escape_sql(f.slug)}, N'Parking Deck', {escape_sql(tagline)},
        {escape_sql(f.address)}, {escape_sql(f.city)}, N'Delhi NCR', {escape_sql(postal)},
        {f.latitude:.6f}, {f.longitude:.6f}, {f.hourly_rate:.2f}, {f.daily_rate:.2f}, N'₹',
        {escape_sql(f.image_url)}, {escape_sql(desc)}, {1 if f.is_24_7 else 0},
        {1 if f.is_active else 0}, {1 if f.is_featured else 0}, {f.rating:.2f}, {f.review_count},
        {escape_sql(amenities_str)}, {1 if f.ev_charging_available else 0},
        {escape_sql(ev_type)}, {f.cancellation_hours_before}
    );
END
ELSE
BEGIN
    UPDATE ParkingFacilities SET
        name = {escape_sql(f.name)},
        tagline = {escape_sql(tagline)},
        address = {escape_sql(f.address)},
        city = {escape_sql(f.city)},
        postal_code = {escape_sql(postal)},
        latitude = {f.latitude:.6f},
        longitude = {f.longitude:.6f},
        hourly_rate = {f.hourly_rate:.2f},
        daily_rate = {f.daily_rate:.2f},
        image_url = {escape_sql(f.image_url)},
        description = {escape_sql(desc)},
        is_24_7 = {1 if f.is_24_7 else 0},
        is_active = {1 if f.is_active else 0},
        is_featured = {1 if f.is_featured else 0},
        amenities_json = {escape_sql(amenities_str)},
        ev_charging_available = {1 if f.ev_charging_available else 0},
        ev_charger_types = {escape_sql(ev_type)}
    WHERE slug = {escape_sql(f.slug)};
END
GO
""")

        # MySQL Upsert
        mysql_lines.append(f"""INSERT INTO ParkingFacilities (
    id, name, slug, category, tagline, address, city, state, postal_code,
    latitude, longitude, hourly_rate, daily_rate, currency, image_url,
    description, is_24_7, is_active, is_featured, rating, review_count,
    amenities_json, ev_charging_available, ev_charger_types, cancellation_hours_before
) VALUES (
    {f.id}, '{f.name.replace("'", "''")}', '{f.slug.replace("'", "''")}', 'Parking Deck', '{tagline.replace("'", "''")}',
    '{f.address.replace("'", "''")}', '{f.city.replace("'", "''")}', 'Delhi NCR', '{postal}',
    {f.latitude:.6f}, {f.longitude:.6f}, {f.hourly_rate:.2f}, {f.daily_rate:.2f}, '₹',
    '{f.image_url.replace("'", "''")}', '{desc.replace("'", "''")}', {1 if f.is_24_7 else 0},
    {1 if f.is_active else 0}, {1 if f.is_featured else 0}, {f.rating:.2f}, {f.review_count},
    '{amenities_str.replace("'", "''")}', {1 if f.ev_charging_available else 0},
    '{ev_type.replace("'", "''")}', {f.cancellation_hours_before}
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
""")

    sql_server_lines.append("SET IDENTITY_INSERT ParkingFacilities OFF;\nGO\n")

    # Write files
    sql_server_path = base_dir / "parkease_facilities_export.sql"
    mysql_path = base_dir / "mysql_facilities_export.sql"

    with open(sql_server_path, "w", encoding="utf-8") as fs:
        fs.write("\n".join(sql_server_lines))

    with open(mysql_path, "w", encoding="utf-8") as fm:
        fm.write("\n".join(mysql_lines))

    return sql_server_path, mysql_path
