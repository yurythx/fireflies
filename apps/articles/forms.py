from django import forms
from tinymce.widgets import TinyMCE

from .models import Article
from .models import Comment


class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
         return False


class ArticleForm(forms.ModelForm):

      content = forms.CharField(
          widget=TinyMCEWidget(
              attrs={'required': False, 'cols': 30, 'rows': 10, 'class': 'form-control', 'id': 'mytextarea'}
          )
      )
      
     
      class Meta:
        model = Article
        fields = ['title', 'exerpt', 'imagem_article', 'content', 'cover', 'category', 'tags', 'is_published' , 'created_by']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author_name', 'author_email', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Escreva seu comentário...', 'rows': 5}),
        }
