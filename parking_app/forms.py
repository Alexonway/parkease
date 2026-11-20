from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal
from .models import UserProfile, ContactMessage, ParkingFacility, ParkingSlot, Review

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Create secure password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm password'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+1 (555) 000-0000'}))
    vehicle_plate = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. ABC-1234'}))
    vehicle_model = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Tesla Model 3 / BMW 3 Series'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Choose username'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'name@example.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Full Name', 'required': 'true'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your.email@example.com', 'required': 'true'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number (Optional)'}),
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Subject / Inquiry topic', 'required': 'true'}),
            'message': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'How can our parking concierge team assist you?', 'required': 'true'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(5, '5 Stars - Exceptional'), (4, '4 Stars - Very Good'), (3, '3 Stars - Average'), (2, '2 Stars - Needs Improvement'), (1, '1 Star - Poor')], attrs={'class': 'form-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Share your parking experience...', 'required': 'true'}),
        }


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class FacilityAdminForm(forms.ModelForm):
    slug = forms.CharField(
        required=False,
        label="URL Identifier (Slug)",
        help_text="Optional — any text you enter with spaces will automatically be converted to a clean URL slug",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Optional — auto-generated from name'})
    )
    image_file = forms.FileField(
        required=False,
        label="Upload Main Place Image",
        help_text="Upload a photo from your computer (JPG, PNG, WebP)",
        widget=forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'})
    )
    gallery_files = forms.FileField(
        required=False,
        label="Upload Additional Place Photos (Gallery)",
        help_text="You can select multiple photo files to show more angles of this facility",
        widget=MultipleFileInput(attrs={'class': 'form-input', 'accept': 'image/*'})
    )
    gallery_urls = forms.CharField(
        required=False,
        label="Additional Image URLs",
        help_text="Paste web image links (comma or newline separated)",
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'https://example.com/photo1.jpg, https://example.com/photo2.jpg'})
    )
    amenities_text = forms.CharField(
        required=False,
        label="Amenities & Features",
        help_text="Comma-separated amenities (e.g. Covered, EV Charging, 24/7 Security, CCTV, Valet, Car Wash)",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Covered Parking, 24/7 CCTV, Fast EV Charging, Valet'})
    )
    floors_count = forms.IntegerField(
        required=False,
        initial=2,
        min_value=1,
        max_value=10,
        label="Initial Decks / Floors to Provision",
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )
    slots_per_floor = forms.IntegerField(
        required=False,
        initial=8,
        min_value=1,
        max_value=50,
        label="Slots per Deck",
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = ParkingFacility
        fields = [
            'name', 'slug', 'tagline', 'address', 'city', 'postal_code',
            'latitude', 'longitude', 'hourly_rate', 'daily_rate',
            'image_url', 'description', 'is_24_7', 'is_active', 'is_featured',
            'ev_charging_available', 'ev_charger_types', 'cancellation_hours_before'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. CyberHub Smart Tower Parking'}),
            'slug': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. cyberhub-smart-tower'}),
            'tagline': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Executive multi-level deck in Gurugram'}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street / Sector / Complex Address'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Gurugram (Haryana) or Noida (UP)'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 122002'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.000001', 'placeholder': '28.4900'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.000001', 'placeholder': '77.0900'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-input', 'step': '1.00', 'placeholder': '50'}),
            'daily_rate': forms.NumberInput(attrs={'class': 'form-input', 'step': '5.00', 'placeholder': '300'}),
            'image_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://images.unsplash.com/...'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describe security, accessibility, entry gates...'}),
            'ev_charger_types': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Type 2 & CCS2 Fast Charge'}),
            'cancellation_hours_before': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make non-essential fields completely optional with smart defaults
        self.fields['slug'].required = False
        self.fields['tagline'].required = False
        self.fields['postal_code'].required = False
        self.fields['image_url'].required = False
        self.fields['description'].required = False
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['latitude'].initial = 28.5355
        self.fields['longitude'].initial = 77.2410
        self.fields['hourly_rate'].required = False
        self.fields['hourly_rate'].initial = 50.00
        self.fields['daily_rate'].required = False
        self.fields['daily_rate'].initial = 300.00
        self.fields['cancellation_hours_before'].required = False
        self.fields['cancellation_hours_before'].initial = 2
        self.fields['ev_charger_types'].required = False
        self.fields['ev_charger_types'].initial = "Type 2 & CCS2 Fast Charge"

        if self.instance and self.instance.pk:
            if self.instance.amenities:
                self.fields['amenities_text'].initial = ', '.join(self.instance.amenities)
            if self.instance.gallery_images:
                self.fields['gallery_urls'].initial = '\n'.join(self.instance.gallery_images)

    def clean_slug(self):
        slug = (self.cleaned_data.get('slug') or '').strip()
        if slug:
            return slugify(slug)
        return ''

    def clean(self):
        cleaned_data = super().clean()
        name = (cleaned_data.get('name') or '').strip()
        slug = (cleaned_data.get('slug') or '').strip()

        # 1. Automatic Slug Generation if empty or invalid
        if not slug and name:
            slug = slugify(name)
        elif slug:
            slug = slugify(slug)

        if not slug:
            slug = f"facility-{timezone.now().strftime('%y%m%d%H%M%S')}"

        # 2. Slug Deduplication
        base_slug = slug
        counter = 1
        query = ParkingFacility.objects.filter(slug=slug)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        while query.exists():
            counter += 1
            slug = f"{base_slug}-{counter}"
            query = ParkingFacility.objects.filter(slug=slug)
            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.pk)

        cleaned_data['slug'] = slug

        # 3. Intelligent default values for all optional fields
        city = (cleaned_data.get('city') or '').strip() or 'Delhi NCR'
        if not cleaned_data.get('tagline'):
            cleaned_data['tagline'] = f"Secure & convenient parking in {city}"
        if not cleaned_data.get('description'):
            cleaned_data['description'] = f"Modern multi-level parking facility in {city} with 24/7 CCTV surveillance, automated barrier entry, and high-speed EV charging bays."
        if not cleaned_data.get('postal_code'):
            cleaned_data['postal_code'] = "110001"
        if not cleaned_data.get('hourly_rate'):
            cleaned_data['hourly_rate'] = Decimal("50.00")
        if not cleaned_data.get('daily_rate'):
            cleaned_data['daily_rate'] = Decimal("300.00")
        if not cleaned_data.get('latitude'):
            cleaned_data['latitude'] = 28.5355
        if not cleaned_data.get('longitude'):
            cleaned_data['longitude'] = 77.2410
        if not cleaned_data.get('cancellation_hours_before'):
            cleaned_data['cancellation_hours_before'] = 2
        if not cleaned_data.get('ev_charger_types'):
            cleaned_data['ev_charger_types'] = "Type 2 & CCS2 Fast Charge"

        return cleaned_data
