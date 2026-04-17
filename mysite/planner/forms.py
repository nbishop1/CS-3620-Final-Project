from django import forms
from django.contrib.auth.models import User

from .models import Note, UserProfile


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )


class SignUpForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    theme = forms.ChoiceField(choices=UserProfile.THEME_CHOICES)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match.')

        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        UserProfile.objects.create(user=user, theme=self.cleaned_data['theme'])
        return user


class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    theme = forms.ChoiceField(choices=UserProfile.THEME_CHOICES)
    profile_picture = forms.ImageField(required=False)
    remove_profile_picture = forms.BooleanField(required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields['theme'].initial = profile.theme

    def save(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.user)

        self.user.first_name = self.cleaned_data['first_name']
        self.user.last_name = self.cleaned_data['last_name']
        self.user.save(update_fields=['first_name', 'last_name'])

        profile.theme = self.cleaned_data['theme']
        if self.cleaned_data['remove_profile_picture']:
            profile.profile_picture = None
        elif self.cleaned_data.get('profile_picture'):
            profile.profile_picture = self.cleaned_data['profile_picture']
        profile.save()

        return self.user


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'rows': 16,
                    'placeholder': 'Write your journal entry here...',
                }
            ),
        }

    def clean_content(self):
        content = self.cleaned_data['content'].strip()
        word_count = len(content.split())

        if word_count > 1000:
            raise forms.ValidationError('Notes are limited to 1,000 words.')

        return content
