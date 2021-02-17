from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


from .models import Profile
from .forms import LoginForm, UserRegistrationForm, \
                    UserEditForm, ProfileEditForm


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated '\
                                        'successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})


class RegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'account/register.html'
    redirect_name = 'account/register_done.html'

    def get(self, request, *args, **kwargs):
        user_form = self.form_class()
        return render(request, self.template_name, {'user_form': user_form})

    def post(self, request, *args, **kwargs):
        user_form = self.form_class(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(request, self.redirect_name, {'new_user': new_user})


@method_decorator(login_required, name='dispatch')
class EditView(View):
    user_form = UserEditForm
    profile_form = ProfileEditForm
    template_name = 'account/edit.html'

    def get(self, request, *args, **kwargs):
        user_form = self.user_form(instance=request.user)
        profile_form = self.profile_form(instance=request.user.profile)
        return render(request, self.template_name, {'user_form': user_form,
                                                    'profile_form': profile_form})

    def post(self, request, *args, **kwargs):
        user_form = self.user_form(instance=request.user,
                                   data=request.POST)
        profile_form = self.profile_form(instance=request.user.profile,
                                         data=request.POST,
                                         files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
        return render(request, self.template_name, {'user_form': user_form,
                                                    'profile_form': profile_form})

