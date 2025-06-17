from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
import re

from tinymce.widgets import TinyMCE

from apps.articles.models.article import Article
from apps.articles.models.category import Category
from apps.articles.models.tag import Tag
from apps.articles.models.comment import Comment

User = get_user_model()


class ArticleForm(forms.ModelForm):
    """Formulário para criação e edição de artigos"""
    
    class Meta:
        model = Article
        fields = [
            'title', 'excerpt', 'content', 'featured_image', 'featured_image_alt',
            'category', 'tags', 'status', 'is_featured', 'allow_comments',
            'meta_title', 'meta_description', 'meta_keywords'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Digite o título do artigo...',
                'maxlength': 200
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escreva um resumo atrativo do artigo...',
                'rows': 3,
                'maxlength': 500
            }),
            'content': TinyMCE(attrs={
                'class': 'form-control',
                'placeholder': 'Escreva o conteúdo completo do artigo...',
            }, mce_attrs={'config': 'advanced'}),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'featured_image_alt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Texto alternativo para a imagem...',
                'maxlength': 200
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_comments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Título para SEO (máx. 60 caracteres)',
                'maxlength': 60
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Descrição para SEO (máx. 160 caracteres)',
                'rows': 3,
                'maxlength': 160
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Palavras-chave separadas por vírgula',
                'maxlength': 200
            }),
        }
        
        labels = {
            'title': 'Título',
            'excerpt': 'Resumo',
            'content': 'Conteúdo',
            'featured_image': 'Imagem Destacada',
            'featured_image_alt': 'Texto Alternativo',
            'category': 'Categoria',
            'tags': 'Tags',
            'status': 'Status',
            'is_featured': 'Artigo em destaque',
            'allow_comments': 'Permitir comentários',
            'meta_title': 'Meta Título',
            'meta_description': 'Meta Descrição',
            'meta_keywords': 'Palavras-chave',
        }
        
        help_texts = {
            'title': 'Título principal do artigo (máximo 200 caracteres)',
            'excerpt': 'Resumo que aparecerá na listagem de artigos (máximo 500 caracteres)',
            'content': 'Conteúdo completo do artigo (pode usar HTML)',
            'featured_image': 'Imagem que aparecerá no topo do artigo e na listagem',
            'featured_image_alt': 'Texto alternativo para acessibilidade',
            'category': 'Categoria principal do artigo',
            'tags': 'Segure Ctrl/Cmd para selecionar múltiplas tags',
            'status': 'Status de publicação do artigo',
            'is_featured': 'Marque para destacar o artigo na página inicial',
            'allow_comments': 'Permitir que usuários comentem no artigo',
            'meta_title': 'Título para mecanismos de busca (máximo 60 caracteres)',
            'meta_description': 'Descrição para mecanismos de busca (máximo 160 caracteres)',
            'meta_keywords': 'Palavras-chave para SEO, separadas por vírgula',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset para categoria
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Selecione uma categoria"
        
        # Configurar queryset para tags
        self.fields['tags'].queryset = Tag.objects.all()
        
        # Tornar campos obrigatórios
        self.fields['title'].required = True
        self.fields['excerpt'].required = True
        self.fields['content'].required = True
        
        # Configurar valores padrão
        if not self.instance.pk:  # Novo artigo
            self.fields['status'].initial = 'draft'
            self.fields['allow_comments'].initial = True

    def clean_title(self):
        """Validação personalizada para o título"""
        title = self.cleaned_data.get('title')
        if title:
            # Verificar se já existe um artigo com o mesmo título (exceto o atual)
            existing = Article.objects.filter(title__iexact=title)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError('Já existe um artigo com este título.')
        
        return title

    def clean_excerpt(self):
        """Validação personalizada para o resumo"""
        excerpt = self.cleaned_data.get('excerpt')
        if excerpt and len(excerpt) < 50:
            raise ValidationError('O resumo deve ter pelo menos 50 caracteres.')
        return excerpt

    def clean_content(self):
        """Validação personalizada para o conteúdo"""
        content = self.cleaned_data.get('content')
        if content and len(content) < 100:
            raise ValidationError('O conteúdo deve ter pelo menos 100 caracteres.')
        return content

    def clean_meta_title(self):
        """Validação para meta título"""
        meta_title = self.cleaned_data.get('meta_title')
        if meta_title and len(meta_title) > 60:
            raise ValidationError('O meta título não pode ter mais de 60 caracteres.')
        return meta_title

    def clean_meta_description(self):
        """Validação para meta descrição"""
        meta_description = self.cleaned_data.get('meta_description')
        if meta_description and len(meta_description) > 160:
            raise ValidationError('A meta descrição não pode ter mais de 160 caracteres.')
        return meta_description

    def clean_featured_image(self):
        """Validação para imagem destacada"""
        image = self.cleaned_data.get('featured_image')
        if image:
            # Verificar tamanho do arquivo (máximo 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('A imagem não pode ser maior que 5MB.')
            
            # Verificar tipo de arquivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise ValidationError('Tipo de arquivo não permitido. Use JPEG, PNG, GIF ou WebP.')
        
        return image

    def save(self, commit=True):
        """Sobrescrever save para adicionar lógica personalizada"""
        article = super().save(commit=False)
        
        # Se não há meta_title, usar o título
        if not article.meta_title:
            article.meta_title = article.title[:60]
        
        # Se não há meta_description, usar o excerpt
        if not article.meta_description:
            article.meta_description = article.excerpt[:160]
        
        if commit:
            article.save()
            self.save_m2m()  # Salvar tags
        
        return article


class CommentForm(forms.ModelForm):
    """Formulário para comentários de artigos"""

    # Campo honeypot para detectar spam
    website_url = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='Website URL (deixe em branco)'
    )

    class Meta:
        model = Comment
        fields = ['name', 'email', 'website', 'content']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu nome *',
                'maxlength': 100,
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu email *',
                'required': True
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Seu website (opcional)'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escreva seu comentário... *',
                'rows': 4,
                'required': True
            }),
        }

        labels = {
            'name': 'Nome',
            'email': 'Email',
            'website': 'Website',
            'content': 'Comentário',
        }

        help_texts = {
            'name': 'Como você gostaria de ser identificado',
            'email': 'Seu email não será publicado',
            'website': 'URL do seu site ou blog (opcional)',
            'content': 'Compartilhe sua opinião, dúvida ou sugestão',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.article = kwargs.pop('article', None)
        self.parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)

        # Se usuário está logado, preencher campos automaticamente
        if self.user and self.user.is_authenticated:
            self.fields['name'].initial = self.user.get_full_name() or self.user.username
            self.fields['email'].initial = self.user.email
            # Tornar campos readonly para usuários logados
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['name'].help_text = 'Logado como: ' + (self.user.get_full_name() or self.user.username)
            self.fields['email'].help_text = 'Email da conta: ' + self.user.email

    def clean_website_url(self):
        """Honeypot para detectar spam"""
        website_url = self.cleaned_data.get('website_url')
        if website_url:
            raise ValidationError('Spam detectado.')
        return website_url

    def clean_name(self):
        """Validação do nome"""
        name = self.cleaned_data.get('name')
        if name:
            # Remover tags HTML
            name = strip_tags(name).strip()

            # Verificar se não é muito curto
            if len(name) < 2:
                raise ValidationError('O nome deve ter pelo menos 2 caracteres.')

            # Verificar se não contém apenas números
            if name.isdigit():
                raise ValidationError('O nome não pode conter apenas números.')

            # Verificar caracteres suspeitos
            if re.search(r'[<>{}[\]\\]', name):
                raise ValidationError('O nome contém caracteres não permitidos.')

        return name

    def clean_email(self):
        """Validação do email"""
        email = self.cleaned_data.get('email')
        if email:
            # Verificar domínios suspeitos
            suspicious_domains = [
                'tempmail.org', '10minutemail.com', 'guerrillamail.com',
                'mailinator.com', 'throwaway.email'
            ]
            domain = email.split('@')[1].lower() if '@' in email else ''
            if domain in suspicious_domains:
                raise ValidationError('Email temporário não é permitido.')

        return email

    def clean_content(self):
        """Validação do conteúdo"""
        content = self.cleaned_data.get('content')
        if content:
            # Remover tags HTML perigosas
            content = strip_tags(content).strip()

            # Verificar tamanho mínimo
            if len(content) < 10:
                raise ValidationError('O comentário deve ter pelo menos 10 caracteres.')

            # Verificar tamanho máximo
            if len(content) > 2000:
                raise ValidationError('O comentário não pode ter mais de 2000 caracteres.')

            # Verificar spam patterns
            spam_patterns = [
                r'http[s]?://[^\s]+\.[^\s]+',  # URLs
                r'\b(viagra|casino|poker|loan|credit)\b',  # Palavras spam
                r'[A-Z]{8,}',  # Muito texto em maiúscula
                r'(.)\1{6,}',  # Caracteres repetidos
            ]

            for pattern in spam_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    raise ValidationError('Conteúdo suspeito detectado.')

        return content

    def save(self, commit=True):
        """Salvar comentário com dados adicionais"""
        comment = super().save(commit=False)

        # Definir artigo e usuário
        if self.article:
            comment.article = self.article
        if self.user and self.user.is_authenticated:
            comment.user = self.user
        if self.parent:
            comment.parent = self.parent

        # Comentários de usuários verificados são aprovados automaticamente
        if self.user and self.user.is_authenticated and getattr(self.user, 'is_verified', False):
            comment.is_approved = True
            from django.utils import timezone
            comment.approved_at = timezone.now()

        if commit:
            comment.save()

        return comment


class ReplyForm(CommentForm):
    """Formulário para respostas a comentários"""

    class Meta(CommentForm.Meta):
        fields = ['name', 'email', 'content']  # Remover website das respostas

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Seu nome *',
                'maxlength': 100,
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Seu email *',
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Escreva sua resposta... *',
                'rows': 3,
                'required': True
            }),
        }


class CommentModerationForm(forms.ModelForm):
    """Formulário para moderação de comentários (admin)"""

    class Meta:
        model = Comment
        fields = ['is_approved', 'is_spam']

        widgets = {
            'is_approved': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_spam': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

        labels = {
            'is_approved': 'Aprovado',
            'is_spam': 'Spam',
        }

    def save(self, commit=True):
        """Salvar com lógica de moderação"""
        comment = super().save(commit=False)

        # Se aprovado, definir data de aprovação
        if comment.is_approved and not comment.approved_at:
            from django.utils import timezone
            comment.approved_at = timezone.now()

        # Se marcado como spam, desaprovar
        if comment.is_spam:
            comment.is_approved = False
            comment.approved_at = None

        if commit:
            comment.save()

        return comment
