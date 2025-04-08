from django import forms
from tinymce.widgets import TinyMCE

from .models import Article
from .models import Comment
import re


# Personalizando o widget TinyMCE para não incluir o atributo 'required'
class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False  # Impede a inclusão do atributo 'required' no campo

class ArticleForm(forms.ModelForm):
    # Usando o TinyMCEWidget para o campo 'content'
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'cols': 30, 'rows': 10, 'class': 'form-control', 'id': 'mytextarea'}
        )
    )

    class Meta:
        model = Article
        fields = ['title', 'excerpt', 'imagem_article', 'content', 'cover', 'category', 'tags', 'is_published', 'created_by']

    # Validação para o título do artigo
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError("O título não pode estar vazio.")
        return title

    # Validação para o resumo (excerpt) do artigo
    def clean_excerpt(self):
        excerpt = self.cleaned_data.get('excerpt')
        if len(excerpt) > 255:
            raise forms.ValidationError("O resumo não pode ter mais de 255 caracteres.")
        return excerpt

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author_name', 'text']


