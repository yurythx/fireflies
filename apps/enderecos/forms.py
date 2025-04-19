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

        # Evita KeyError: garante que os campos existem antes de configurar
        if 'estado' in self.fields:
            self.fields['estado'].queryset = Estado.objects.all()

        if 'cidade' in self.fields:
            self.fields['cidade'].queryset = Cidade.objects.none()

            # Se já há um estado selecionado (via POST ou ao editar)
            if 'estado' in self.data:
                try:
                    estado_id = int(self.data.get('estado'))
                    self.fields['cidade'].queryset = Cidade.objects.filter(estado_id=estado_id).order_by('nome')
                except (ValueError, TypeError):
                    pass
            elif self.instance.pk and hasattr(self.instance, 'estado') and self.instance.estado:
                self.fields['cidade'].queryset = self.instance.estado.cidades.all()

        # Layout com Crispy Forms
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                *(  # Usando * para desempacotar apenas campos válidos
                    [
                        Field('estado', id='id_estado', wrapper_class='col-md-6')
                        if 'estado' in self.fields else None,
                        Field('cidade', id='id_cidade', wrapper_class='col-md-6')
                        if 'cidade' in self.fields else None,
                        Field('rua', wrapper_class='col-md-8')
                        if 'rua' in self.fields else None,
                        Field('numero', wrapper_class='col-md-4')
                        if 'numero' in self.fields else None,
                        Field('complemento', wrapper_class='col-md-6')
                        if 'complemento' in self.fields else None,
                        Field('bairro', wrapper_class='col-md-6')
                        if 'bairro' in self.fields else None,
                        Field('cep', wrapper_class='col-md-6')
                        if 'cep' in self.fields else None,
                    ]
                ),
                css_class='row g-3'
            )
        )