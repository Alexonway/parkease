# ParkEase — Smart Classic E-Parking Platform

> *"ParkEase — Parking, made simple. Find a space. Book ahead. Arrive relaxed."*

A full-stack, responsive E-Parking web application built with **Python 3**, **Django**, **Tailwind CSS**, and **Leaflet.js**. Features real-time slot availability, multi-floor interactive bay selector, idempotent server-calculated checkout, digital QR parking passes, gate barrier check-in portal, driver dashboard, and operator admin console.

---

## 🌟 Key Features

### 1. Classic & Attractive Design (Modern Minimal)
- **Classic luxury palette**: Off-white and cream surfaces (`#fcfdfd`, `#f8faf9`), deep forest green typography (`#062d22`, `#064e3b`), emerald green primary actions (`#059669`, `#10b981`), and mint highlights (`#d1fae5`).
- **Typography pairing**: Editorial classic serif headings (`Cinzel`) with modern, high-legibility interface body font (`Plus Jakarta Sans`).
- **High-resolution imagery**: Curated architecture and mobility photography for premium parking garages, EV hubs, and executive facilities.

### 2. Smart Parking Search & Interactive Map
- **Split Map / List View**: Switch between interactive Leaflet OpenStreetMap pins and card grid.
- **Filters**: Filter by city (New York, Chicago, San Francisco, Dallas, Los Angeles), EV charging availability, and vehicle type.
- **Sorting**: Sort by featured rating, price (low-to-high, high-to-low), and distance.

### 3. Multi-Floor Interactive Bay Selector
- **Floor Switcher**: Toggle between Ground Level (P1), Upper Level (P2), and Sky Terrace (P3).
- **Slot States**: Available (Emerald green), Occupied (Muted slate), Reserved, and Active Selected Bay.
- **Attributes**: Dedicated icons and indicators for EV Supercharging bays (⚡) and Accessible / Handicap bays (♿).

### 4. Idempotent Checkout & Pricing Engine
- **Server-Side Pricing**: Base rate × duration + reservation fee ($1.50) + municipal tax (8%).
- **Concurrency Protection**: Database transaction locking (`select_for_update()`) prevents race conditions or dual bookings on the same bay.
- **Loyalty Redemption**: Redeem 100 loyalty points for an instant $5 discount.
- **Test Payment Mode**: Simulated card and digital wallet gateway with instant verification.

### 5. Scannable Digital QR Parking Pass
- **Real QR Generation**: Cryptographically generated base64 PNG QR code embedding secure verification link (`/verify-ticket/<reference_code>/`).
- **Print / PDF Optimized**: Dedicated `@media print` CSS layout for one-click clean ticket printing.
- **Gate Attendant Portal**: Optical scanner view showing real-time pass validity with one-click barrier gate entry and exit checkouts.

### 6. Driver Dashboard & Operator Admin Console
- **Driver Dashboard**: Active bookings, cancellation with automatic slot release and refunds, completed history, favorite garages, and loyalty points ledger.
- **Admin Console**: Live network occupancy KPI, total revenue collected, multi-facility manager, real-time booking feed, and inquiry manager.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- `pip`

### 1. Installation
Clone or navigate to the project root:
```powershell
cd C:\Users\Admin\.gemini\antigravity\scratch\parkease
```

Install required packages:
```powershell
pip install django qrcode pillow
```

### 2. Database Setup & Seed Data
Initialize the database and load realistic facilities, floors, parking slots, and demo accounts:
```powershell
python manage.py makemigrations parking_app
python manage.py migrate
python manage.py seed_data
```

### 3. Run the Development Server
```powershell
python manage.py runserver 127.0.0.1:8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

---

## 👥 Demo Accounts (Pre-configured)

Use the one-click demo login buttons on the sign-in page or credentials below:

| Role | Username | Email | Password | Pre-configured Data |
| :--- | :--- | :--- | :--- | :--- |
| **Driver / Customer** | `alex_driver` | `alex@example.com` | `Password123!` | Active booking `PK-892401`, BMW i4, 450 loyalty points |
| **Administrator** | `admin` | `admin@parkease.com` | `Admin123!` | Executive operations console & gate barrier controller |

---

## 🧪 Automated Test Suite

Run the automated test suite:
```powershell
python manage.py test
```
All 7 unit and integration tests verify:
- Pricing engine calculations
- Real QR code generation
- Public route availability
- End-to-end booking flow and bay reservation locking
- Booking cancellation and automatic refund
- Staff gate barrier check-in and checkout operations
- Contact and concierge message storage

---

## 📁 Project Architecture

```
parkease/
├── config/
│   ├── settings.py         # Configurable brand settings, apps, templates, static
│   ├── urls.py             # Root URL routing
│   └── wsgi.py
├── parking_app/
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py # Seed realistic facilities, multi-floor slots & users
│   ├── models.py           # Facilities, Floors, Slots, Bookings, Payments, Rewards
│   ├── views.py            # Public, Booking, Verification, Dashboard & Admin views
│   ├── forms.py            # Registration, Contact, Review, and Admin forms
│   ├── urls.py             # RESTful routing for ParkEase
│   ├── utils.py            # QR code generation & pricing calculations
│   ├── tests.py            # Comprehensive unit and integration test suite
│   └── context_processors.py # Brand variables exposed to all templates
├── templates/
│   ├── base.html           # Classic luxury layout, Tailwind CDN, Leaflet, Navigation
│   ├── home.html           # Hero, quick search widget, featured facilities, stats
│   ├── facilities.html     # Find parking with Leaflet map / list split view
│   ├── facility_detail.html # Interactive multi-floor slot grid selector & reviews
│   ├── booking_checkout.html# 4-step progress checkout, server quote, test card gateway
│   ├── booking_confirmation.html # Digital QR ticket, print layout, cancellation
│   ├── verify_ticket.html  # Gate attendant scanner & live barrier check-in tool
│   ├── dashboard.html      # Driver dashboard, active bookings, loyalty ledger
│   ├── admin_dashboard.html# Executive KPI console, facilities & bookings manager
│   ├── about.html          # Mission, transparent tariffs, security architecture
│   ├── contact.html        # Concierge contact desk and inquiry form
│   ├── login.html          # Authentication with 1-click demo logins
│   └── register.html       # Driver registration with 100-point welcome bonus
├── .env.example            # Environment variables placeholder
├── .gitignore
├── manage.py
└── README.md
```
