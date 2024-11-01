from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from .forms import TranscendenceUserCreationForm, TranscendenceUserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import TranscendenceUser

# Create your views here.
class SignUpView(generic.CreateView):
    form_class = TranscendenceUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


@login_required
def profile(request, username=None):
    if username and username != request.user.username:
        user = get_object_or_404(TranscendenceUser, username=username)
        editable = False
        form = None
    else:
        #if no username provided or matches logged in user
        user = request.user
        editable = True
        if request.method == 'POST':
            form = TranscendenceUserChangeForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('profile')
        else:
            form = TranscendenceUserChangeForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'user': user, 'form': form, 'editable': editable})
