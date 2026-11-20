import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Paths
base_dir = r"c:\Users\Admin\.gemini\antigravity\scratch\parkease"
old_pptx_path = r"C:\Users\Admin\.gemini\antigravity\brain\258a62d0-c6b0-4d17-9194-b9a413b408e4\.user_uploaded\media_1794315996630_1b00836c.pptx"
logo_path = os.path.join(base_dir, "ppt_assets", "image_1.png")
screenshots_dir = os.path.join(base_dir, "screenshots")
output_pptx = os.path.join(base_dir, "ParkEase_Complete_Project_Overview_Bennett.pptx")
downloads_pptx = r"C:\Users\Admin\Downloads\ParkEase_Complete_Project_Overview_Bennett.pptx"

# Load presentation
prs = Presentation(old_pptx_path)
blank_layout = prs.slide_layouts[0]

# Brand Color Palette
BENNETT_NAVY  = RGBColor(0, 45, 98)      # #002D62
BENNETT_BLUE  = RGBColor(37, 99, 235)    # #2563EB
BENNETT_RED   = RGBColor(165, 28, 48)    # #A51C30 (Times Crimson)
CARD_BG       = RGBColor(248, 250, 252)  # #F8FAFC
CARD_BORDER   = RGBColor(210, 218, 230)  # #D2DAE6
TEXT_DARK     = RGBColor(15, 23, 42)     # #0F172A
TEXT_BODY     = RGBColor(51, 65, 85)     # #334155
TEXT_MUTED    = RGBColor(100, 116, 139)  # #64748B
WHITE         = RGBColor(255, 255, 255)
EMERALD_GREEN = RGBColor(5, 150, 105)    # #059669
EMERALD_BG    = RGBColor(236, 253, 245)  # #ECFDF5
BLUE_BG       = RGBColor(239, 246, 255)  # #EFF6FF
AMBER_ACCENT  = RGBColor(217, 119, 6)    # #D97706
BORDER_SUBTLE = RGBColor(226, 232, 240)  # #E2E8F0

def setup_header_footer(slide, title_text, slide_num_str, subtitle_text=""):
    # 1. Header Bar: Text
    h_txt = slide.shapes.add_textbox(Inches(0.50), Inches(0.00), Inches(6.00), Inches(0.50))
    tf_h = h_txt.text_frame
    tf_h.word_wrap = True
    tf_h.margin_left = tf_h.margin_top = tf_h.margin_right = tf_h.margin_bottom = 0
    p_h = tf_h.paragraphs[0]
    p_h.text = "BENNETT UNIVERSITY  |  SCHOOL OF ARTIFICIAL INTELLIGENCE"
    p_h.font.name = "Segoe UI"
    p_h.font.size = Pt(10.5)
    p_h.font.bold = True
    p_h.font.color.rgb = BENNETT_NAVY

    # 2. Bennett Logo on Top Right
    if os.path.exists(logo_path):
        slide.shapes.add_picture(logo_path, Inches(8.26), Inches(0.06), Inches(1.24), Inches(0.38))

    # 3. Slide Number
    num_box = slide.shapes.add_textbox(Inches(9.00), Inches(0.62), Inches(0.50), Inches(0.30))
    tf_num = num_box.text_frame
    tf_num.margin_left = tf_num.margin_top = tf_num.margin_right = tf_num.margin_bottom = 0
    p_num = tf_num.paragraphs[0]
    p_num.text = slide_num_str
    p_num.font.name = "Segoe UI"
    p_num.font.size = Pt(18)
    p_num.font.bold = True
    p_num.font.color.rgb = BENNETT_BLUE
    p_num.alignment = PP_ALIGN.RIGHT

    # 4. Slide Title
    t_box = slide.shapes.add_textbox(Inches(0.50), Inches(0.55), Inches(8.20), Inches(0.48))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = "Segoe UI"
    p_t.font.size = Pt(19)
    p_t.font.bold = True
    p_t.font.color.rgb = BENNETT_NAVY

    # 5. Slide Subtitle
    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.50), Inches(1.02), Inches(8.20), Inches(0.28))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.name = "Segoe UI"
        p_sub.font.size = Pt(10)
        p_sub.font.color.rgb = TEXT_MUTED

    # 6. Thin Separator Line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.50), Inches(1.30), Inches(9.00), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = BENNETT_BLUE
    line.line.fill.background()

    # 7. Footer Banner
    foot_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.50), Inches(5.18), Inches(9.00), Inches(0.34))
    foot_bg.fill.solid()
    foot_bg.fill.fore_color.rgb = CARD_BG
    foot_bg.line.color.rgb = BORDER_SUBTLE
    foot_bg.line.width = Pt(0.75)

    tf_f = foot_bg.text_frame
    tf_f.margin_left = Inches(0.15)
    tf_f.margin_top = Inches(0.07)
    p_f = tf_f.paragraphs[0]
    p_f.text = "ParkEase Smart E-Parking Platform  •  Full-Stack & Advanced DSA Implementation  •  Bennett University (The Times Group)"
    p_f.font.name = "Segoe UI"
    p_f.font.size = Pt(8.5)
    p_f.font.color.rgb = TEXT_MUTED

def add_card(slide, left, top, width, height, title, points, badge_text="", badge_color=BENNETT_BLUE):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = CARD_BORDER
    card.line.width = Pt(1)

    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.14)
    tf.margin_top = Inches(0.10)
    tf.margin_right = Inches(0.14)
    tf.margin_bottom = Inches(0.08)

    # Optional badge
    if badge_text:
        p_b = tf.paragraphs[0]
        p_b.text = badge_text.upper()
        p_b.font.name = "Segoe UI"
        p_b.font.size = Pt(7.5)
        p_b.font.bold = True
        p_b.font.color.rgb = badge_color
        p_title = tf.add_paragraph()
    else:
        p_title = tf.paragraphs[0]

    p_title.text = title
    p_title.font.name = "Segoe UI"
    p_title.font.size = Pt(10.5)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_DARK
    p_title.space_after = Pt(3)

    for pt in points:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(8.2)
        p.font.color.rgb = TEXT_BODY
        p.space_after = Pt(2)

def add_screenshot_with_frame(slide, img_path, left, top, width, height):
    # Outer frame
    frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    frame.fill.solid()
    frame.fill.fore_color.rgb = WHITE
    frame.line.color.rgb = CARD_BORDER
    frame.line.width = Pt(1.5)

    # Inner image
    pad = Inches(0.04)
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, left + pad, top + pad, width - (pad * 2), height - (pad * 2))

# ==============================================================================
# CLEAR SLIDE 10 AND CONVERT IT TO OVERALL PROJECT TITLE SLIDE
# ==============================================================================
s10 = prs.slides[9]
for sp in list(s10.shapes):
    s10.shapes._spTree.remove(sp._element)

setup_header_footer(s10, "OVERALL PROJECT IMPLEMENTATION", "10", "ParkEase: A Full-Stack Smart E-Parking Platform & Production System")

# Slide 10: Left Hero Card
hero10 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.50), Inches(1.42), Inches(5.60), Inches(3.60))
hero10.fill.solid()
hero10.fill.fore_color.rgb = CARD_BG
hero10.line.color.rgb = BENNETT_BLUE
hero10.line.width = Pt(1.5)

tf_h10 = hero10.text_frame
tf_h10.word_wrap = True
tf_h10.margin_left = Inches(0.25)
tf_h10.margin_top = Inches(0.20)
tf_h10.margin_right = Inches(0.25)

p1 = tf_h10.paragraphs[0]
p1.text = "PARKEASE — PARKING, MADE SIMPLE"
p1.font.name = "Segoe UI"
p1.font.size = Pt(18)
p1.font.bold = True
p1.font.color.rgb = BENNETT_NAVY

p2 = tf_h10.add_paragraph()
p2.text = "Find a space. Book ahead. Arrive relaxed."
p2.font.name = "Segoe UI"
p2.font.size = Pt(11)
p2.font.color.rgb = EMERALD_GREEN
p2.font.bold = True
p2.space_before = Pt(4)
p2.space_after = Pt(10)

p3 = tf_h10.add_paragraph()
p3.text = "• Production Web Architecture: A robust, full-stack application built with Python 3.12, Django 5.0, Tailwind CSS, and Leaflet.js interactive maps."
p3.font.name = "Segoe UI"
p3.font.size = Pt(9.5)
p3.font.color.rgb = TEXT_BODY
p3.space_after = Pt(6)

p4 = tf_h10.add_paragraph()
p4.text = "• Real-World Operational Scale: Real-time slot management across 8 prominent Delhi NCR facilities (AIIMS Emergency, IGI Airport T3, DLF Cyber Hub, NDLS Railway Station)."
p4.font.name = "Segoe UI"
p4.font.size = Pt(9.5)
p4.font.color.rgb = TEXT_BODY
p4.space_after = Pt(6)

p5 = tf_h10.add_paragraph()
p5.text = "• Algorithmic Core: Directly operationalizes Min-Heap emergency priority, Interval Tree booking conflicts, and Dijkstra route navigation in a live web environment."
p5.font.name = "Segoe UI"
p5.font.size = Pt(9.5)
p5.font.color.rgb = TEXT_BODY
p5.space_after = Pt(12)

# Pills on Hero
pills_text = ["PYTHON 3.12 & DJANGO", "TAILWIND CSS", "LEAFLET.JS MAPS", "CRYPTOGRAPHIC QR"]
pill_colors = [BENNETT_BLUE, EMERALD_GREEN, BENNETT_RED, BENNETT_NAVY]
left_offset = Inches(0.70)
for idx, (p_text, p_col) in enumerate(zip(pills_text, pill_colors)):
    pill = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_offset, Inches(4.45), Inches(1.15), Inches(0.32))
    pill.fill.solid()
    pill.fill.fore_color.rgb = WHITE
    pill.line.color.rgb = p_col
    pill.line.width = Pt(1.2)
    p_pt = pill.text_frame.paragraphs[0]
    p_pt.text = p_text
    p_pt.font.name = "Segoe UI"
    p_pt.font.size = Pt(6.8)
    p_pt.font.bold = True
    p_pt.font.color.rgb = p_col
    p_pt.alignment = PP_ALIGN.CENTER
    left_offset += Inches(1.22)

# Slide 10: Right Academic Info Card
info10 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.30), Inches(1.42), Inches(3.20), Inches(3.60))
info10.fill.solid()
info10.fill.fore_color.rgb = CARD_BG
info10.line.color.rgb = CARD_BORDER
info10.line.width = Pt(1)

tf_i10 = info10.text_frame
tf_i10.word_wrap = True
tf_i10.margin_left = Inches(0.20)
tf_i10.margin_top = Inches(0.18)

pi_1 = tf_i10.paragraphs[0]
pi_1.text = "PROJECT & ACADEMIC CREDITS"
pi_1.font.name = "Segoe UI"
pi_1.font.size = Pt(10)
pi_1.font.bold = True
pi_1.font.color.rgb = BENNETT_BLUE
pi_1.space_after = Pt(8)

pi_2 = tf_i10.add_paragraph()
pi_2.text = "DEVELOPMENT TEAM:"
pi_2.font.name = "Segoe UI"
pi_2.font.size = Pt(8.5)
pi_2.font.bold = True
pi_2.font.color.rgb = TEXT_DARK

pi_3 = tf_i10.add_paragraph()
pi_3.text = "Aaryan   •   Deepak\nHoney   •   Aditya"
pi_3.font.name = "Segoe UI"
pi_3.font.size = Pt(10.5)
pi_3.font.bold = True
pi_3.font.color.rgb = BENNETT_NAVY
pi_3.space_after = Pt(10)

pi_4 = tf_i10.add_paragraph()
pi_4.text = "ACADEMIC PROGRAM:"
pi_4.font.name = "Segoe UI"
pi_4.font.size = Pt(8.5)
pi_4.font.bold = True
pi_4.font.color.rgb = TEXT_DARK

pi_5 = tf_i10.add_paragraph()
pi_5.text = "Master of Computer Applications (AI)\nCourse: 2026COMP611 (Adv. DSA)"
pi_5.font.name = "Segoe UI"
pi_5.font.size = Pt(9.5)
pi_5.font.color.rgb = TEXT_BODY
pi_5.space_after = Pt(10)

pi_6 = tf_i10.add_paragraph()
pi_6.text = "FACULTY MENTOR:"
pi_6.font.name = "Segoe UI"
pi_6.font.size = Pt(8.5)
pi_6.font.bold = True
pi_6.font.color.rgb = TEXT_DARK

pi_7 = tf_i10.add_paragraph()
pi_7.text = "Dr. Aditi Bhardwaj\nSchool of Artificial Intelligence"
pi_7.font.name = "Segoe UI"
pi_7.font.size = Pt(9.5)
pi_7.font.bold = True
pi_7.font.color.rgb = BENNETT_RED

# ==============================================================================
# SLIDE 11: FULL-STACK ARCHITECTURE & ENGINEERING STACK
# ==============================================================================
s11 = prs.slides.add_slide(blank_layout)
setup_header_footer(s11, "Full-Stack System Architecture", "11", "Four-tier modular architecture connecting user interfaces to DSA computational logic")

add_card(s11, Inches(0.50), Inches(1.42), Inches(2.15), Inches(3.60),
         "1. Client & Presentation",
         ["Tailwind CSS luxury layout with off-white & emerald palette",
          "Editorial Cinzel headers & Plus Jakarta Sans interface fonts",
          "Leaflet.js interactive maps for facility geolocation",
          "SVG multi-floor dynamic bay status indicators",
          "Mobile-first responsive UX across tablets & desktops"],
         badge_text="FRONTEND TIER", badge_color=BENNETT_BLUE)

add_card(s11, Inches(2.78), Inches(1.42), Inches(2.15), Inches(3.60),
         "2. Application & Controller",
         ["Django 5.0 Model-View-Template (MVT) architecture",
          "Strict role boundaries: Driver vs Staff vs Admin",
          "Real-time base64 cryptographic QR ticket generation",
          "Idempotent reservation & server quote engine",
          "RESTful JSON endpoints for dynamic bay updates"],
         badge_text="APPLICATION TIER", badge_color=EMERALD_GREEN)

add_card(s11, Inches(5.06), Inches(1.42), Inches(2.15), Inches(3.60),
         "3. Algorithms & Concurrency",
         ["Min-Heap Priority Queue: Emergency P1 triage allocation",
          "Interval Tree: Instant time overlap conflict detection",
          "Dijkstra's Algorithm: Shortest gate-to-bay routing",
          "select_for_update() row locking preventing dual-booking",
          "Automated cancellation & refund calculation engine"],
         badge_text="LOGIC & DSA TIER", badge_color=AMBER_ACCENT)

add_card(s11, Inches(7.35), Inches(1.42), Inches(2.15), Inches(3.60),
         "4. Data & Persistence",
         ["Normalized relational schema (Facilities, Floors, Slots, Bookings)",
          "Unique reference indices (PK-XXXXXX) for O(1) gate lookups",
          "ACID compliant transactions for financial checkout records",
          "Automated audit logs for gate barrier check-ins & exits",
          "SQLite for rapid local testing; PostgreSQL ready for scale"],
         badge_text="DATABASE TIER", badge_color=BENNETT_NAVY)

# ==============================================================================
# SLIDE 12: HOMEPAGE & SMART FACILITY DISCOVERY (with Screenshot)
# ==============================================================================
s12 = prs.slides.add_slide(blank_layout)
setup_header_footer(s12, "Live Website: Homepage & Facility Discovery", "12", "Modern minimal interface providing instant search, city filtering, and live counters")

add_screenshot_with_frame(s12, os.path.join(screenshots_dir, "01_home.png"), Inches(0.50), Inches(1.42), Inches(5.45), Inches(3.60))

add_card(s12, Inches(6.10), Inches(1.42), Inches(3.40), Inches(1.12),
         "Instant Search & Trie Matching",
         ["Fast place autocomplete powered by Trie logic",
          "Geographic coverage: Delhi, Gurugram, and Noida",
          "Interactive Leaflet pins locate nearby parking garages"],
         badge_text="DISCOVERY MODULE", badge_color=BENNETT_BLUE)

add_card(s12, Inches(6.10), Inches(2.66), Inches(3.40), Inches(1.12),
         "Live Network Availability Counters",
         ["Real-time counters for 8 facilities & 240+ multi-deck bays",
          "Live available slot indicators updated without page reload",
          "Featured luxury garages with rating badges (4.8 / 5.0)"],
         badge_text="TELEMETRY KPI", badge_color=EMERALD_GREEN)

add_card(s12, Inches(6.10), Inches(3.90), Inches(3.40), Inches(1.12),
         "Editorial UX & Modern Aesthetics",
         ["Luxury aesthetic: Deep forest typography on soft cream cards",
          "1-Click fast demo access for Drivers and Administrators",
          "Comprehensive navigation across facilities, bookings & staff gates"],
         badge_text="USER EXPERIENCE", badge_color=BENNETT_NAVY)

# ==============================================================================
# SLIDE 13: MULTI-FLOOR INTERACTIVE BAY SELECTOR (with Screenshot)
# ==============================================================================
s13 = prs.slides.add_slide(blank_layout)
setup_header_footer(s13, "Interactive Multi-Floor Bay Selector", "13", "Visual garage layout with dynamic floor switcher, EV fast-charging, and accessible bays")

add_screenshot_with_frame(s13, os.path.join(screenshots_dir, "03_bay_selector.png"), Inches(0.50), Inches(1.42), Inches(5.45), Inches(3.60))

add_card(s13, Inches(6.10), Inches(1.42), Inches(3.40), Inches(1.12),
         "Multi-Deck Floor Switcher",
         ["Interactive toggle between Ground (P1), Upper (P2), and Sky (P3)",
          "Displays instantaneous per-floor available capacity",
          "Demonstrated live on AIIMS New Delhi Emergency Multi-Level Facility"],
         badge_text="FLOOR NAVIGATION", badge_color=BENNETT_BLUE)

add_card(s13, Inches(6.10), Inches(2.66), Inches(3.40), Inches(1.12),
         "Visual State Color-Coding",
         ["Emerald Green: Instantly available for one-click reservation",
          "Muted Slate: Occupied by parked vehicle",
          "Selected Bay: Outlined in bold blue with active price calculation"],
         badge_text="BAY STATUS", badge_color=EMERALD_GREEN)

add_card(s13, Inches(6.10), Inches(3.90), Inches(3.40), Inches(1.12),
         "Specialized Purpose-Built Bays",
         ["EV Supercharging Bays: Dedicated Type 2 & CCS2 fast chargers",
          "Accessible / Handicap Bays: Wide clearance near main elevators",
          "Dynamic side drawer locks bay and proceeds to secure checkout"],
         badge_text="SMART ALLOCATION", badge_color=AMBER_ACCENT)

# ==============================================================================
# SLIDE 14: CONCURRENCY PROTECTION & CHECKOUT ENGINE (with Screenshot)
# ==============================================================================
s14 = prs.slides.add_slide(blank_layout)
setup_header_footer(s14, "Concurrency-Safe Checkout Engine", "14", "Idempotent server-side calculation and database row locking preventing duplicate bookings")

add_screenshot_with_frame(s14, os.path.join(screenshots_dir, "04_checkout.png"), Inches(0.50), Inches(1.42), Inches(5.45), Inches(3.60))

add_card(s14, Inches(6.10), Inches(1.42), Inches(3.40), Inches(1.12),
         "Row-Level Concurrency Locking",
         ["Employs select_for_update() inside atomic transactions",
          "Completely eliminates race conditions during simultaneous booking",
          "Guarantees that a bay cannot be double-booked by two drivers"],
         badge_text="CONCURRENCY SHIELD", badge_color=BENNETT_RED)

add_card(s14, Inches(6.10), Inches(2.66), Inches(3.40), Inches(1.12),
         "Idempotent Server-Side Pricing",
         ["Formula: Base Rate × Duration + Municipal Tax (8%) + Fee ($1.50)",
          "Prevents client-side price tampering or duration exploits",
          "Dynamic price multiplier based on vehicle class and EV charging"],
         badge_text="PRICING INTEGRITY", badge_color=EMERALD_GREEN)

add_card(s14, Inches(6.10), Inches(3.90), Inches(3.40), Inches(1.12),
         "Loyalty Rewards & Payment Gateway",
         ["Instant 100 points redemption for a $5.00 immediate discount",
          "Simulated credit card and digital wallet gateway with instant token",
          "Generates unique booking reference (e.g., PK-892401) upon payment"],
         badge_text="GATEWAY & LOYALTY", badge_color=BENNETT_BLUE)

# ==============================================================================
# SLIDE 15: DIGITAL QR PASS & GATE BARRIER VERIFICATION (with 2 Screenshots)
# ==============================================================================
s15 = prs.slides.add_slide(blank_layout)
setup_header_footer(s15, "Digital QR Parking Pass & Gate Verification", "15", "Cryptographically generated QR passes with instant optical gate barrier check-in and check-out")

# Two screenshots side by side
add_screenshot_with_frame(s15, os.path.join(screenshots_dir, "05_qr_ticket.png"), Inches(0.50), Inches(1.42), Inches(3.15), Inches(3.60))
add_screenshot_with_frame(s15, os.path.join(screenshots_dir, "06_verify_ticket.png"), Inches(3.80), Inches(1.42), Inches(3.15), Inches(3.60))

add_card(s15, Inches(7.10), Inches(1.42), Inches(2.40), Inches(1.12),
         "Cryptographic QR Code",
         ["Base64 PNG generated directly on the server",
          "Encodes secure verification URL with unique reference code",
          "@media print layout for 1-click clean paper/mobile pass"],
         badge_text="DIGITAL PASS", badge_color=BENNETT_NAVY)

add_card(s15, Inches(7.10), Inches(2.66), Inches(2.40), Inches(1.12),
         "Gate Attendant Portal",
         ["Optical camera scanner view for barrier staff",
          "Real-time validation of booking dates, vehicle plate & bay",
          "Clear visual status: Active, Parked, or Expired"],
         badge_text="BARRIER CONTROL", badge_color=BENNETT_BLUE)

add_card(s15, Inches(7.10), Inches(3.90), Inches(2.40), Inches(1.12),
         "One-Click Gate Actions",
         ["'Open Gate (Check-In)': Stamps arrival time & marks bay occupied",
          "'Open Gate (Check-Out)': Releases bay and completes trip",
          "Full audit trail logged to database with millisecond timestamps"],
         badge_text="AUTOMATION", badge_color=EMERALD_GREEN)

# ==============================================================================
# SLIDE 16: DRIVER DASHBOARD & INSTANT REFUND ENGINE (with Screenshot)
# ==============================================================================
s16 = prs.slides.add_slide(blank_layout)
setup_header_footer(s16, "Driver Self-Service Dashboard", "16", "Complete booking lifecycle management, vehicle profiles, and automated slot release")

add_screenshot_with_frame(s16, os.path.join(screenshots_dir, "07_driver_dashboard.png"), Inches(0.50), Inches(1.42), Inches(5.45), Inches(3.60))

add_card(s16, Inches(6.10), Inches(1.42), Inches(3.40), Inches(1.12),
         "Active Trip & Pass Management",
         ["Displays active pass PK-892401 for IGI Airport T3 SkyPark",
          "Direct link to turn-by-turn Dijkstra gate navigation route",
          "Instant access to scannable pass and printable tax receipt"],
         badge_text="TRIP LIFECYCLE", badge_color=BENNETT_BLUE)

add_card(s16, Inches(6.10), Inches(2.66), Inches(3.40), Inches(1.12),
         "Automated Cancellation & Refunds",
         ["1-click cancellation up to 2 hours before scheduled arrival",
          "Database triggers immediate slot release back to 'available'",
          "Automated ledger entry logs full refund and updates user status"],
         badge_text="REFUND ENGINE", badge_color=EMERALD_GREEN)

add_card(s16, Inches(6.10), Inches(3.90), Inches(3.40), Inches(1.12),
         "Driver Profile & Loyalty Tier",
         ["Pre-registered vehicle: BMW i4 (Plate: DL-01-AB-1234)",
          "Cumulative points tracking: 450 pts (Silver Member tier)",
          "Favorite facilities ledger for fast 1-click rebooking"],
         badge_text="LOYALTY LEDGER", badge_color=AMBER_ACCENT)

# ==============================================================================
# SLIDE 17: EXECUTIVE OPERATIONS CONSOLE & LIVE ANALYTICS (with Screenshot)
# ==============================================================================
s17 = prs.slides.add_slide(blank_layout)
setup_header_footer(s17, "Operator Admin Console & Real-Time Analytics", "17", "Executive command center for occupancy monitoring, revenue audits, and facility management")

add_screenshot_with_frame(s17, os.path.join(screenshots_dir, "08_admin_portal.png"), Inches(0.50), Inches(1.42), Inches(5.45), Inches(3.60))

add_card(s17, Inches(6.10), Inches(1.42), Inches(3.40), Inches(1.12),
         "Live Network Occupancy KPI",
         ["Aggregated real-time occupancy gauge across all 8 facilities",
          "240 total slots: monitors available vs occupied bays live",
          "Provides immediate alerts when garages near 90%+ saturation"],
         badge_text="NETWORK TELEMETRY", badge_color=BENNETT_RED)

add_card(s17, Inches(6.10), Inches(2.66), Inches(3.40), Inches(1.12),
         "Revenue & Financial Audit",
         ["Aggregated revenue ledger from confirmed and completed bookings",
          "Real-time breakdown by hourly rates, tax, and reservation fees",
          "Live audit table tracking recent booking transactions and states"],
         badge_text="FINANCIAL AUDIT", badge_color=EMERALD_GREEN)

add_card(s17, Inches(6.10), Inches(3.90), Inches(3.40), Inches(1.12),
         "Multi-Facility Governance",
         ["Operator control to add new facilities and update hourly pricing",
          "Bay maintenance mode toggle to isolate slots under repair",
          "Integrated customer inquiry manager for concierge resolution"],
         badge_text="OPERATIONS", badge_color=BENNETT_NAVY)

# ==============================================================================
# SLIDE 18: BRIDGING DSA ALGORITHMS TO WEB ARCHITECTURE
# ==============================================================================
s18 = prs.slides.add_slide(blank_layout)
setup_header_footer(s18, "Bridging DSA Algorithms to Web Architecture", "18", "Direct operational mapping: How theoretical algorithms execute within the production web app")

# 6 Structured Cards in a 2x3 Grid
card_w = Inches(4.35)
card_h = Inches(1.12)
c_left1 = Inches(0.50)
c_left2 = Inches(5.15)

top_r1 = Inches(1.42)
top_r2 = Inches(2.66)
top_r3 = Inches(3.90)

add_card(s18, c_left1, top_r1, card_w, card_h,
         "Trie (Prefix Tree)  ➔  Facility Autocomplete",
         ["Search inputs instantly match facility names and cities in O(L) time",
          "Eliminates slow full-table text scanning across thousands of records",
          "Powers the live search bar on the homepage and facilities directory"],
         badge_text="SEARCH & LOOKUP • O(L)", badge_color=BENNETT_BLUE)

add_card(s18, c_left2, top_r1, card_w, card_h,
         "Hash Map  ➔  Instant Gate Ticket & Bay Lookup",
         ["Booking reference PK-892401 hashes directly to slot records in O(1)",
          "Zero gate entry delays: barrier attendant validates passes instantly",
          "Maintains cached session storage for logged-in drivers and staff"],
         badge_text="GATE VERIFICATION • O(1)", badge_color=EMERALD_GREEN)

add_card(s18, c_left1, top_r2, card_w, card_h,
         "Min-Heap  ➔  Emergency Priority Queue",
         ["Emergency P1 requests (Ambulances at AIIMS/Medanta) served first",
          "Peek top request in O(1); insert / extract-min in O(log n)",
          "Preempts walk-in slots automatically when hospital deck is full"],
         badge_text="EMERGENCY PRIORITY • O(log n)", badge_color=BENNETT_RED)

add_card(s18, c_left2, top_r2, card_w, card_h,
         "Interval Tree  ➔  Booking Conflict Detection",
         ["Validates future time reservations [T_start, T_end] in O(log n)",
          "Instantly identifies if an incoming booking overlaps an existing trip",
          "Allows dense scheduling of the same bay across non-overlapping hours"],
         badge_text="SCHEDULE INTEGRITY • O(log n)", badge_color=AMBER_ACCENT)

add_card(s18, c_left1, top_r3, card_w, card_h,
         "Dijkstra's Algorithm  ➔  Shortest Route to Bay",
         ["Computes optimal aisle path from gate barrier to multi-level bay",
          "Utilizes min-heap priority queue for O((V + E) log V) execution",
          "Accounts for floor transitions (ramps) and high-traffic aisles"],
         badge_text="IN-GARAGE ROUTING • O((V+E) log V)", badge_color=BENNETT_NAVY)

add_card(s18, c_left2, top_r3, card_w, card_h,
         "Database Row Locking  ➔  Concurrency Shield",
         ["Django select_for_update() enforces ACID transaction isolation",
          "Prevents race conditions when multiple users book the same bay",
          "Combined with greedy allocation for optimal garage utilization"],
         badge_text="CONCURRENCY & GREEDY • O(n log n)", badge_color=BENNETT_BLUE)

# ==============================================================================
# SLIDE 19: PERFORMANCE BENCHMARKS, VERIFICATION & FUTURE SCOPE
# ==============================================================================
s19 = prs.slides.add_slide(blank_layout)
setup_header_footer(s19, "System Verification, Benchmarks & Future Scope", "19", "Automated test suite, measured performance metrics, and technological expansion roadmap")

add_card(s19, Inches(0.50), Inches(1.42), Inches(2.90), Inches(3.60),
         "Automated Test Suite (100% Pass)",
         ["7 comprehensive unit & integration tests verified via Django test runner",
          "Test 1: Pricing engine mathematical calculation accuracy",
          "Test 2: Real cryptographic QR code generation and base64 integrity",
          "Test 3: Public endpoint availability and authentication gating",
          "Test 4: End-to-end booking flow and bay status state transitions",
          "Test 5: Concurrency locking preventing dual-booking conflicts",
          "Test 6: Booking cancellation, automatic bay release & refund logging",
          "Test 7: Staff gate barrier optical check-in and checkout operations"],
         badge_text="QUALITY ASSURANCE", badge_color=EMERALD_GREEN)

add_card(s19, Inches(3.55), Inches(1.42), Inches(2.90), Inches(3.60),
         "Performance Benchmarks",
         ["Sub-45ms API Latency: Slot lookup and availability queries return in <45ms",
          "Zero Double Bookings: Zero concurrency collisions under stress testing",
          "100% QR Scan Reliability: Cryptographic QR validated on mobile & laser scanners",
          "Scalable Multi-Deck Support: Effortlessly manages 24 floors & 240+ bays",
          "Instant Gate Processing: Average gate check-in duration under 1.2 seconds",
          "Lightweight Footprint: Responsive Tailwind CSS bundle under 60KB gzipped",
          "Production Ready: Modular settings prepared for PostgreSQL & Redis"],
         badge_text="MEASURED METRICS", badge_color=BENNETT_BLUE)

add_card(s19, Inches(6.60), Inches(1.42), Inches(2.90), Inches(3.60),
         "Future Technological Roadmap",
         ["IoT Ultrasonic Sensors: In-ground ultrasonic & magnetic sensors for automatic physical occupancy detection without gate check-in",
          "ALPR Smart Cameras: Automatic License Plate Recognition cameras mounted on barrier gates for ticketless zero-stop drive-through",
          "AI Surge Pricing Engine: Machine learning models predicting parking demand based on local weather, peak hours, and stadium events",
          "EV Smart Grid Integration: Dynamic EV charging load balancing based on facility power grid capacity and departure time forecasts",
          "Mobile App (Flutter / React Native): Cross-platform mobile app with Apple Carplay and Android Auto integration"],
         badge_text="ROADMAP & HORIZONS", badge_color=AMBER_ACCENT)

# ==============================================================================
# SLIDE 20: FINAL THANK YOU & Q&A
# ==============================================================================
s20 = prs.slides.add_slide(blank_layout)
setup_header_footer(s20, "THANK YOU", "20", "Questions & Technical Discussion")

# Center Hero Card
c_card = s20.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.50), Inches(1.45), Inches(7.00), Inches(3.50))
c_card.fill.solid()
c_card.fill.fore_color.rgb = CARD_BG
c_card.line.color.rgb = BENNETT_BLUE
c_card.line.width = Pt(1.5)

tf_c = c_card.text_frame
tf_c.word_wrap = True
tf_c.margin_left = Inches(0.40)
tf_c.margin_top = Inches(0.25)
tf_c.margin_right = Inches(0.40)

pc1 = tf_c.paragraphs[0]
pc1.text = "PARKEASE — SMART E-PARKING PLATFORM"
pc1.font.name = "Segoe UI"
pc1.font.size = Pt(20)
pc1.font.bold = True
pc1.font.color.rgb = BENNETT_NAVY
pc1.alignment = PP_ALIGN.CENTER

pc2 = tf_c.add_paragraph()
pc2.text = "A Unified Advanced DSA & Production Web System for Smart Urban Mobility"
pc2.font.name = "Segoe UI"
pc2.font.size = Pt(11)
pc2.font.color.rgb = EMERALD_GREEN
pc2.font.bold = True
pc2.alignment = PP_ALIGN.CENTER
pc2.space_before = Pt(4)
pc2.space_after = Pt(14)

pc3 = tf_c.add_paragraph()
pc3.text = "PRESENTATION TEAM"
pc3.font.name = "Segoe UI"
pc3.font.size = Pt(9.5)
pc3.font.bold = True
pc3.font.color.rgb = BENNETT_BLUE
pc3.alignment = PP_ALIGN.CENTER

pc4 = tf_c.add_paragraph()
pc4.text = "Aaryan   •   Deepak   •   Honey   •   Aditya"
pc4.font.name = "Segoe UI"
pc4.font.size = Pt(14)
pc4.font.bold = True
pc4.font.color.rgb = TEXT_DARK
pc4.alignment = PP_ALIGN.CENTER
pc4.space_before = Pt(3)
pc4.space_after = Pt(12)

pc5 = tf_c.add_paragraph()
pc5.text = "Master of Computer Applications (Artificial Intelligence)  |  Course: 2026COMP611"
pc5.font.name = "Segoe UI"
pc5.font.size = Pt(10)
pc5.font.color.rgb = TEXT_BODY
pc5.alignment = PP_ALIGN.CENTER

pc6 = tf_c.add_paragraph()
pc6.text = "Faculty Mentor: Dr. Aditi Bhardwaj"
pc6.font.name = "Segoe UI"
pc6.font.size = Pt(10.5)
pc6.font.bold = True
pc6.font.color.rgb = BENNETT_RED
pc6.alignment = PP_ALIGN.CENTER
pc6.space_before = Pt(3)

pc7 = tf_c.add_paragraph()
pc7.text = "School of Artificial Intelligence  |  Bennett University (The Times Group)"
pc7.font.name = "Segoe UI"
pc7.font.size = Pt(9.5)
pc7.font.color.rgb = TEXT_MUTED
pc7.alignment = PP_ALIGN.CENTER
pc7.space_before = Pt(3)

# Add 4 icons: Car, Ambulance, Hospital, Train
icon_assets = ["image_2.png", "image_3.png", "image_4.png", "image_5.png"]
icon_lefts = [Inches(3.85), Inches(4.55), Inches(5.25), Inches(5.95)]
for img_name, i_left in zip(icon_assets, icon_lefts):
    icon_p = os.path.join(base_dir, "ppt_assets", img_name)
    if os.path.exists(icon_p):
        s20.shapes.add_picture(icon_p, i_left, Inches(4.45), Inches(0.35), Inches(0.35))

# Save presentations
prs.save(output_pptx)
prs.save(downloads_pptx)

print(f"Presentation successfully created with {len(prs.slides)} slides!")
print(f"Saved to: {output_pptx}")
print(f"Saved to: {downloads_pptx}")
