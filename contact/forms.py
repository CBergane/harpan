from django import forms
from .models import ContactSubmission


class ContactForm(forms.ModelForm):
    """Kontaktformulär"""
    
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'phone', 'org_number', 'subject', 'message', 'gdpr_consent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ditt namn'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'din@email.se'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '070-123 45 67'
            }),
            'org_number': forms.TextInput(attrs={
                'placeholder': "5590xxxx-xxxx",
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Vad gäller din förfrågan?'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Berätta mer om hur vi kan hjälpa dig...',
                'rows': 5
            }),
            'gdpr_consent': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            })
        }
        labels = {
            'name': 'Namn *',
            'email': 'E-post *',
            'phone': 'Telefon',
            'org_number': 'Organisationsnummer (valfritt)',
            'subject': 'Ämne',
            'message': 'Meddelande *',
            'gdpr_consent': ''
        }
    
    def clean_gdpr_consent(self):
        consent = self.cleaned_data.get('gdpr_consent')
        if not consent:
            raise forms.ValidationError('Du måste godkänna behandling av personuppgifter')
        return consent
