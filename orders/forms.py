from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Address

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=20, required=False)
    street = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    zip_code = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user_profile = UserProfile.objects.create(user=user, phone_number=self.cleaned_data['phone_number'])
            if self.cleaned_data['street']:
                address = Address.objects.create(
                    user_profile=user_profile,
                    street=self.cleaned_data['street'],
                    city=self.cleaned_data['city'],
                    state=self.cleaned_data['state'],
                    zip_code=self.cleaned_data['zip_code']
                )
                user_profile.addresses.add(address)
            user_profile.save()
        return user
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number']

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'zip_code']
