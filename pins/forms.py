from django import forms
from .models import Comment, Category


class CommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control",
        "style": "border-radius: 20px; display: inline; width: 90%; float: right;",
        "placeholder": "Add Comment ..",
        "rows": "1"
    }))

    # body = forms.CharField()

    class Meta:
        model = Comment
        fields = ['body']


class CategoryForm(forms.ModelForm):
    topic = forms.CharField()

    class Meta:
        model = Category
        fields = ['topic']
