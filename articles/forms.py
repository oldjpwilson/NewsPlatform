from django import forms
from tinymce import TinyMCE
from .models import Article


class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False


class ArticleModelForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 40, 'rows': 3}), help_text='This is a summary of the article and helps with SEO. This should be filled in')

    thumbnail = forms.ImageField(
        help_text='This image will display at the top of page and also in WhatsApp share links'
    )

    class Meta:
        model = Article
        fields = ('title',
                  'description',
                  'thumbnail',
                  'media_type',
                  'categories',
                  'urgency',
                  'duration',
                  'content',
                  'draft')


class ArticleFilterForm(forms.Form):
    latest = forms.BooleanField(required=False)
    view_count = forms.BooleanField(required=False)
    rating = forms.BooleanField(required=False)


class ContactForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'placeholder': 'Your email'}))
    name = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={'placeholder': 'Your name'}))
    message = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'What\'s on your mind'}))
