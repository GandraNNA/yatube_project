from django import forms

from .models import Group, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            'image'
        )

    text = forms.Textarea()
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False
    )
