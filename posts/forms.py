from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text')
        labels = {
            "group": ("Выберете группу"),
            "text": ("Текст"),
        }
        help_texts = {
            "group": ("Выберете группу из списка доступных."),
            "text": ("Введите текст Вашего поста."),
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if len(data) < 10:
            raise forms.ValidationError("Слишком короткий текст!")
        return data
