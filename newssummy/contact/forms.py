from django import forms


class SentUsMailForm(forms.Form):
    subject = forms.CharField(max_length=120, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Subject'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-Mail'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Message'}))
