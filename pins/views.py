from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Pins, Category, SavePin, Board, Comment
from users.models import Profile, Followers
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
import operator
from functools import reduce
from django.db.models import Q
from .forms import CommentForm


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


@login_required
def pin_detail(request, **kwargs):
    # For save button functionality if already saved then unsave button will be render else save button.
    pin_id = get_object_or_404(Pins, pk=kwargs.get('pk'))
    pin_owner = pin_id.user.username
    pin_saved_by_user = request.user.username
    pin_data = Pins.objects.get(pk=pin_id.id)

    saved = False
    if Board.objects.filter(user__username=pin_saved_by_user, pins=pin_id).exists():
        board_id = Board.objects.get(user__username=pin_saved_by_user, pins=pin_id)
        b_id = board_id.id

        condition1 = SavePin.objects.filter(pin=pin_data, user=User.objects.get(username=pin_saved_by_user)).exists()
        items = board_id.pins.all()
        condition2 = pin_data in items

        if condition1 or condition2:
            saved = True

    else:
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

    board_choices = Board.objects.filter(user__username=pin_saved_by_user)

    print(saved)
    print(is_followed)
    context = {"object": Pins.objects.get(pk=kwargs.get('pk')),
               'saved': saved, 'is_followed': is_followed, 'board_choices': board_choices, 'form': CommentForm()}

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


@login_required
def SearchResultView(request):
    """
     ** Optimized search filter **
     import operator
     queries = 'superman avengers'
     queries = queries.split(' ')
     from functools import reduce
     from django.db.models import Q
     qset1 =  reduce(operator.__or__, [Q(category__topic__icontains=query) | Q(category__topic__icontains=query) for query in queries])
     results = Pins.objects.filter(qset1).distinct()
    """
    topic = request.GET.get('q')
    topic = topic.split(' ')
    qset1 = reduce(operator.__or__,
                   [Q(category__topic__icontains=query) | Q(category__topic__icontains=query) for query in topic if query != ''])
    pi = Pins.objects.filter(qset1).distinct()

    # topic = topic.strip()
    # pi = Pins.objects.filter(category__topic__icontains=topic)

    return render(request, 'pins/search.html', {'topic': topic,
                                                'pins': pi})


class UserBoardView(ListView, LoginRequiredMixin):
    model = Pins
    template_name = 'pins/pinboard.html'
    context_object_name = 'pins'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        new_var = User.objects.get(username=user).profile.image.url
        user_name = User.objects.get(username=user).username

        # For calculating number of followers and followings of a user.
        # user_obj = User.objects.get( username=self.kwargs.get('username'))
        # session_user = User.objects.get(username=self.request.user.username)
        # session_following, create = Followers.objects.get_or_create(user=session_user)
        # following, create = Followers.objects.get_or_create(user=session_user.id)
        # check_user_followers = Followers.objects.filter(another_user=user_obj)

        is_user_ex = Followers.objects.filter(user__username=self.kwargs.get('username')).exists()
        if not is_user_ex:
            us = User.objects.get(username=self.kwargs.get('username'))
            Followers.objects.create(user=us)

        re = Followers.objects.get(user__username=self.kwargs.get('username'))
        check_user_followers = re.another_user.count()
        print(f"->>>>>>>>>>>>>>>>>>> {check_user_followers}")
        count_following = 0
        for i in Followers.objects.filter():
            if i.another_user.filter(username=re.user.username).exists():
                count_following += 1
        print(f"--->>>>>>>>>>>>>>>>>>>>>>>>{count_following}")

        print(new_var)
        data = super().get_context_data(**kwargs)
        data['url'] = new_var
        data['user_name'] = user_name
        data['pins'] = Pins.objects.filter(user=user)

        data['followers'] = check_user_followers
        # data['following'] = following
        data['count_following'] = count_following

        return data


# TODO -get username who has clicked on the save button.
# TODO -get the pin id from the url and save that pin object and username to SavePin model.
@login_required
def save_pin_view(request, **kwargs):
    my_id = kwargs.get('pk')
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
            print("***********************")
            messages.success(request, f'You have unsaved a pin!!')
            saved = False
            # return render(request, 'pins/home.html')
            # return reverse('pin-detail', my_id)
            return redirect('pin-detail', my_id)

        if Board.objects.filter(user__username=pin_saved_by_user, pins=pin_id).exists():
            board_id = Board.objects.get(user__username=pin_saved_by_user, pins=pin_id)
            b_id = board_id.id
            items = board_id.pins.all()
            condition = pin_data in items

            if condition:
                board_id.pins.remove(pin_id)
                saved = False
                messages.success(request, f'You have unsaved a pin from your board!!')
                return redirect('pin-detail', my_id)

        data_needed = SavePin(pin=pin_data, user=User.objects.get(username=pin_saved_by_user))
        data_needed.save()
        saved = True
        messages.success(request, f'Pin Saved!!')
    # return render(request, 'pins/home.html')
    # return reverse('pin-detail', my_id)
    return redirect('pin-detail', my_id)


# TODO -Filter all pins by users and display their saved pins.
# **pinboard_save.html is cerated for only testing I think it is not needed for now.**
class UserSavedPinsView(ListView, LoginRequiredMixin):
    model = SavePin
    template_name = 'pins/pinboard_save.html'
    context_object_name = 'saved_pins'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        new_var = User.objects.get(username=user).profile.image.url
        # data_required = SavePin.objects.filter(user__username=user.username)

        # For calculating number of followers and followings of a user.
        # user_obj = User.objects.get(username=self.kwargs.get('username'))
        # session_user = User.objects.get(username=self.request.user.username)
        # session_following, create = Followers.objects.get_or_create(user=session_user)
        # following, create = Followers.objects.get_or_create(user=session_user.id)
        # check_user_followers = Followers.objects.filter(another_user=user_obj)

        is_user_ex = Followers.objects.filter(user__username=self.kwargs.get('username')).exists()
        if not is_user_ex:
            us = User.objects.get(username=self.kwargs.get('username'))
            Followers.objects.create(user=us)

        re = Followers.objects.get(user__username=self.kwargs.get('username'))
        check_user_followers = re.another_user.count()
        print(f"->>>>>>>>>>>>>>>>>>> {check_user_followers}")
        count_following = 0
        for i in Followers.objects.filter():
            if i.another_user.filter(username=re.user.username).exists():
                count_following += 1
        print(f"--->>>>>>>>>>>>>>>>>>>>>>>>{count_following}")

        data = super().get_context_data(**kwargs)
        data['saved_pins'] = SavePin.objects.filter(user__username=user.username)
        data['user_name'] = user.username
        data['url'] = new_var

        data['followers'] = check_user_followers
        # data['following'] = following
        data['count_following'] = count_following

        data['user_boards'] = Board.objects.filter(user__username=user.username)

        return data


# Board create form
class BoardCreateView(LoginRequiredMixin, CreateView):
    model = Board
    fields = ['title', 'category', 'image1', 'image2', 'image3', 'image4']
    template_name = 'pins/board_form.html'
    success_url = reverse_lazy('pin-home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


def save_pin_board_view(request, p_id, b_id):
    pin_id = get_object_or_404(Pins, id=p_id)
    pin_saved_by_user = request.user.username
    board_id = get_object_or_404(Board, id=b_id)

    print(pin_id)
    print(board_id)

    condition1 = SavePin.objects.filter(pin=pin_id, user=User.objects.get(username=pin_saved_by_user)).exists()
    items = board_id.pins.all()
    condition2 = pin_id in items
    saved = False

    Board.objects.filter(user__username='elon', pins=pin_id)

    if condition1 or condition2:
        if condition1:
            instance = SavePin.objects.get(pin=pin_id, user=User.objects.get(username=pin_saved_by_user))
            instance.delete()
            saved = False
            messages.success(request, f'You have unsaved a pin!!')
            return redirect('pin-detail', p_id)

        elif condition2:
            board_id.pins.remove(pin_id)
            saved = False
            messages.success(request, f'You have unsaved a pin from your board!!')
            return redirect('pin-detail', p_id)

    board_id.pins.add(pin_id)
    saved = True
    messages.success(request, f'Pin saved to board!!')

    return redirect('pin-detail', p_id)


class BoardDetailView(DetailView):
    model = Board
    template_name = 'pins/boards_detail.html'


class BoardUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Board
    fields = ['title', 'image1', 'image2', 'image3', 'image4']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        pin = self.get_object()
        if self.request.user == pin.user:
            return True
        return False


class BoardDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Board
    success_url = '/'

    def test_func(self):
        pin = self.get_object()
        if self.request.user == pin.user:
            return True
        return False


def comment_create(request, **kwargs):
    p_id = kwargs.get('pk')
    if request.method == 'POST':
        print("hellooooo")
        form = CommentForm(request.POST)
        if form.is_valid():
            form.instance.pins_id = p_id
            form.instance.name = request.user
            form.save()
            return redirect('pin-detail', p_id)
    else:
        form = CommentForm(request.POST)
    return redirect('pin-detail', p_id)




