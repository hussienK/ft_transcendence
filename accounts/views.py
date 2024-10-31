from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import TranscendenceUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

# Create your views here.
class SignUpView(generic.CreateView):
    form_class = TranscendenceUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

@login_required
def profile(request):
    if request.method == 'POST':
        form = TranscendenceUserCreationForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        
    else:
        form = TranscendenceUserCreationForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})
