from django.contrib.auth import authenticate
from django import forms
from .models import User, Channel


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


class ChannelCreateForm(forms.ModelForm):
    background_image = forms.ImageField(
        help_text='Ideal size is 2560 pixels wide by x 1440 pixels tall.')

    class Meta:
        model = Channel
        fields = (
            'name',
            'description',
            'profile_image',
            'background_image',
            'categories'
        )


class ChannelUpdateForm(forms.ModelForm):
    background_image = forms.ImageField(
        help_text='Ideal size is 2560 pixels wide by 1440 pixels tall.')

    class Meta:
        model = Channel
        fields = (
            'description',
            'profile_image',
            'background_image',
            'categories'
        )
