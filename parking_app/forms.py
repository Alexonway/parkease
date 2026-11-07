from django import forms
from django.contrib.auth.models import User
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


class FacilityAdminForm(forms.ModelForm):
    amenities_text = forms.CharField(
        required=False,
        help_text="Comma-separated amenities (e.g. Covered, EV Charging, 24/7 Security, CCTV, Valet)",
        widget=forms.TextInput(attrs={'class': 'form-input'})
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
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-input'}),
            'tagline': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.0001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.0001'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.25'}),
            'daily_rate': forms.NumberInput(attrs={'class': 'form-input', 'step': '1.00'}),
            'image_url': forms.URLInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'ev_charger_types': forms.TextInput(attrs={'class': 'form-input'}),
            'cancellation_hours_before': forms.NumberInput(attrs={'class': 'form-input'}),
        }
