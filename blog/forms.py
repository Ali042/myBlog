from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "image"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "", "placeholder": "Title"}),
            "content": forms.Textarea(attrs={"rows": 8, "placeholder": "What’s on your mind?"}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        from .models import Profile
        model = Profile
        fields = ["display_name", "bio", "website", "avatar"]
        widgets = {
            "display_name": forms.TextInput(attrs={"placeholder": "Display name"}),
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "About you"}),
            "website": forms.URLInput(attrs={"placeholder": "https://example.com"}),
        }

class CommentForm(forms.Form):
    content = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Write a comment..."}),
    )
