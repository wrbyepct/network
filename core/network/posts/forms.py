"""Post forms."""

from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """Form for create/edit form."""

    class Meta:
        model = Post
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "row": "4",
                    "placeholder": "What's on your mind?",
                }
            )
        }
