from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages, auth
from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Profile, Followers


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'That username is taken')
            return redirect('register')
        else:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'That email is being used')
                return redirect('register')
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in!!')
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('pin-home')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login')
    else:
        return render(request, 'users/login.html')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            logout(request)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {
        'form': form
    })


@login_required
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)


def follow_user(request, **kwargs):
    other_user = User.objects.get(username=kwargs.get('username'))
    print(other_user)
    session_user = request.user.username
    print(session_user)
    get_user = User.objects.get(username=session_user)
    check_follower = Followers.objects.filter(user=get_user.id).exists()
    print(check_follower)
    is_followed = False

    # re = Followers.objects.get(user__username='realkush')
    # for i in Followers.objects.filter():
    #     print(i.another_user.filter(username=re.user.username))

    if check_follower:
        # if other_user.name != session_user:   # user cannot follow himself.
        check_follower = Followers.objects.get(user=get_user.id)
        if check_follower.another_user.filter(username=other_user).exists():
            add_usr = Followers.objects.get(user=get_user)
            add_usr.another_user.remove(other_user)
            is_followed = False
            messages.success(request, f'User Unfollowed!')
            return render(request, 'pins/home.html')
        else:
            add_usr = Followers.objects.get(user=get_user)
            add_usr.another_user.add(other_user)
            is_followed = True
            messages.success(request, f'User Followed!')
            return render(request, 'pins/home.html')

    else:
        save_user = Followers(user=get_user)
        print(save_user)
        save_user.save()
        check_follower = Followers.objects.get(user=get_user.id)
        print(f"Check_Followers in else clause --> {check_follower}")
        is_followed = False
        if check_follower.another_user.filter(username=other_user).exists():
            add_usr = Followers.objects.get(user=get_user)
            add_usr.another_user.remove(other_user)
            is_followed = False
            messages.success(request, f'User Unfollowed!')
            return render(request, 'pins/home.html')
        else:
            add_usr = Followers.objects.get(user=get_user)
            add_usr.another_user.add(other_user)
            is_followed = True
            messages.success(request, f'User Followed!')
            return render(request, 'pins/home.html')



