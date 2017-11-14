from django import forms


class UserSummaryForm(forms.Form):
    sentences_number = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of sentences (default is 3)', 'autofocus':''}))
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your text', 'autofocus':''}))
