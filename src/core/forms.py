from django.contrib.auth import authenticate
from django import forms
from .models import User, Channel, Profile


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('Incorrect username/password')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect username/password')
        return super(LoginForm, self).clean(*args, **kwargs)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', 'subscriptions', 'payment_details')


class ChannelCreateForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ('name',
                  'description',
                  'profile_image',
                  'background_image',
                  'categories',
                  'payment_details')
