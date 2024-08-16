
from django import template
from django.contrib.auth.models import User
from django.views.generic import ListView, DeleteView, UpdateView, CreateView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse


@login_required(login_url="/login/")

def index_config(request):
    context = {'segment': 'index_config'}
    
    html_template = loader.get_template('config/index_config.html')
    return HttpResponse(html_template.render(context, request))
    
def lista_usuarios(request):
    context = {'segment': 'lista-usuarios'}    

    html_template = loader.get_template('config/lista-usuarios.html')
    return HttpResponse(html_template.render(context, request))


class ProfileListView(ListView):
    template_name = 'articles/profile.html'
    queryset = User.objects.get_queryset()
    #paginate_by = PER_PAGE
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = 'name -'
        return context

@login_required(login_url="/login/")

def pages_config(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index_config/'))
        context['segment'] = load_template

        html_template = loader.get_template('config/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('config/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('config/page-500.html')
        return HttpResponse(html_template.render(context, request))
