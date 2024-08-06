from django.shortcuts import redirect, render
from django.contrib.auth import logout

#def logout_view(request):
#    logout(request)
#    return redirect('index')

#def timeout_view(request):
#    return render(request, 'timeout.html')



def index(request):
    return render(request, 'pages/index.html')



#def error404(request):
#    return render(request, 'varios/error404.html')

#def error500(request):
#    return render(request, 'varios/error500.html')

