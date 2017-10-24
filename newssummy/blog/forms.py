from django import forms
from .models import BlogArticles


class AddBlogForm(forms.ModelForm):
    blog_title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title', 'autofocus':''}))
    blog_description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}))
    blog_text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Text'}))

    class Meta:
        model = BlogArticles
        fields = ["blog_title", "blog_description", "blog_text", "blog_image"]
        widgets = {
            'blog_image': forms.FileInput(),
        }
