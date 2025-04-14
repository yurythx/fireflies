from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from .models import Endereco, Estado, Cidade

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['estado', 'cidade', 'rua', 'numero', 'complemento', 'bairro', 'cep']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Estado e Cidade
        self.fields['estado'].queryset = Estado.objects.all()
        self.fields['cidade'].queryset = Cidade.objects.none()

        # Se já há um estado selecionado (via POST ou ao editar)
        if 'estado' in self.data:
            try:
                estado_id = int(self.data.get('estado'))
                self.fields['cidade'].queryset = Cidade.objects.filter(estado_id=estado_id).order_by('nome')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.estado:
            self.fields['cidade'].queryset = self.instance.estado.cidades.all()

        # Layout com Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Field('estado', id='id_estado', wrapper_class='col-md-6'),
                Field('cidade', id='id_cidade', wrapper_class='col-md-6'),
                Field('rua', wrapper_class='col-md-8'),
                Field('numero', wrapper_class='col-md-4'),
                Field('complemento', wrapper_class='col-md-6'),
                Field('bairro', wrapper_class='col-md-6'),
                Field('cep', wrapper_class='col-md-6'),
                css_class='row g-3'
            )
        )
