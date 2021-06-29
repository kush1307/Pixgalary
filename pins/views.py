from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Pins, Category, SavePin
from users.models import Profile, Followers
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def home(request):
    context = {
        'pins': Pins.objects.all()
    }
    return render(request, 'pins/home.html', context)


class PinCreateView(LoginRequiredMixin, CreateView):
    model = Pins
    fields = ['category', 'image', 'title', 'description']
    success_url = reverse_lazy('pin-home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


# class PinDetailView(DetailView):
#     model = Pins
#
#     def get_context_data(self, **kwargs):
#         # pin_id = get_object_or_404(Pins, pk=kwargs.get('pk'))
#         # pin_saved_by_user = self.request.user.username
#         # pin_data = Pins.objects.get(pk=pin_id.id)
#         # saved = False
#         # if SavePin.objects.filter(pin=pin_data, user=User.objects.get(username=pin_saved_by_user)).exists():
#         #     saved = True
#         data = super().get_context_data(**kwargs)
#         data['saved'] = 'saved'
#         return data

def pin_detail(request, **kwargs):
    # For save button functionality if already saved then unsave button will be render else save button.
    pin_id = get_object_or_404(Pins, pk=kwargs.get('pk'))
    print(pin_id)
    pin_owner = pin_id.user.username
    pin_saved_by_user = request.user.username
    print(pin_saved_by_user)
    pin_data = Pins.objects.get(pk=pin_id.id)
    print(pin_data)
    saved = False
    if SavePin.objects.filter(pin=pin_data, user=User.objects.get(username=pin_saved_by_user)).exists():
        saved = True

    # For follow functionality if already followed then unfollow button will be render.
    other_user = User.objects.get(username=pin_owner)
    session_user = request.user.username
    get_user = User.objects.get(username=session_user)
    check_follower = Followers.objects.filter(user=get_user.id).exists()

    is_followed = False
    if check_follower:
        check_follower = Followers.objects.get(user=get_user.id)
        print(f"@@@@   {check_follower.another_user.filter(username=other_user).exists()}")
        if check_follower.another_user.filter(username=other_user).exists():
            is_followed = True

    print(saved)
    print(is_followed)
    context = {"object": Pins.objects.get(pk=kwargs.get('pk')),
               'saved': saved, 'is_followed': is_followed}

    return render(request, 'pins/pins_detail.html', context)


class PinUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Pins
    fields = ['image', 'title', 'description']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        pin = self.get_object()
        if self.request.user == pin.user:
            return True
        return False


class PinDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Pins
    success_url = '/'

    def test_func(self):
        pin = self.get_object()
        if self.request.user == pin.user:
            return True
        return False


def SearchResultView(request):
    topic = request.GET.get('q')
    pi = Pins.objects.filter(category__topic__icontains=topic)

    return render(request, 'pins/search.html', {'topic': topic,
                                                'pins': pi})


class UserBoardView(ListView):
    model = Pins
    template_name = 'pins/pinboard.html'
    context_object_name = 'pins'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        new_var = User.objects.get(username=user).profile.image.url
        user_name = User.objects.get(username=user).username

        # For calculating number of followers and followings of a user.
        user_obj = User.objects.get( username=self.kwargs.get('username'))
        session_user = User.objects.get(username=self.request.user.username)
        session_following, create = Followers.objects.get_or_create(user=session_user)
        following, create = Followers.objects.get_or_create(user=session_user.id)
        check_user_followers = Followers.objects.filter(another_user=user_obj)

        print(new_var)
        data = super().get_context_data(**kwargs)
        data['url'] = new_var
        data['user_name'] = user_name
        data['pins'] = Pins.objects.filter(user=user)

        data['followers'] = check_user_followers
        data['following'] = following
        data['session_following'] = session_following

        return data


# TODO -get username who has clicked on the save button.
# TODO -get the pin id from the url and save that pin object and username to SavePin model.
def save_pin_view(request, **kwargs):
    if request.method == "GET":
        pin_id = get_object_or_404(Pins, pk=kwargs.get('pk'))
        pin_saved_by_user = request.user.username
        print(f"---------> {pin_id} --- {type(pin_id)}")
        pin_data = Pins.objects.get(pk=pin_id.id)
        print(f"######### >> {pin_data}")
        saved = False
        if SavePin.objects.filter(pin=pin_data, user=User.objects.get(username=pin_saved_by_user)).exists():
            instance = SavePin.objects.get(pin=pin_data, user=User.objects.get(username=pin_saved_by_user))
            instance.delete()
            messages.success(request, f'You have unsaved a pin!!')
            saved = False
            return render(request, 'pins/home.html')
        data_needed = SavePin(pin=pin_data, user=User.objects.get(username=pin_saved_by_user))
        data_needed.save()
        saved = True
        messages.success(request, f'Pin Saved!!')
    return render(request, 'pins/home.html')


# TODO -Filter all pins by users and display their saved pins.
# **pinboard_save.html is cerated for only testing I think it is not needed for now.**
class UserSavedPinsView(ListView):
    model = SavePin
    template_name = 'pins/pinboard_save.html'
    context_object_name = 'saved_pins'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        new_var = User.objects.get(username=user).profile.image.url
        # data_required = SavePin.objects.filter(user__username=user.username)

        # For calculating number of followers and followings of a user.
        user_obj = User.objects.get(username=self.kwargs.get('username'))
        session_user = User.objects.get(username=self.request.user.username)
        session_following, create = Followers.objects.get_or_create(user=session_user)
        following, create = Followers.objects.get_or_create(user=session_user.id)
        check_user_followers = Followers.objects.filter(another_user=user_obj)

        data = super().get_context_data(**kwargs)
        data['saved_pins'] = SavePin.objects.filter(user__username=user.username)
        data['user_name'] = user.username
        data['url'] = new_var

        data['followers'] = check_user_followers
        data['following'] = following
        data['session_following'] = session_following

        return data

