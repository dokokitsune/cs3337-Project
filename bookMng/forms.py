from django import forms
from django.forms import ModelForm
from .models import Book
from .models import Comment


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'web', 'price', 'picture', 'genres']
        widgets = {
            'genres': forms.CheckboxSelectMultiple(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

