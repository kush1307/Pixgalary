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
from datetime import datetime


def home(request):
    """In this view all the Pins are displayed."""
    today = datetime.now()
    context = {
        'today_pins': Pins.objects.filter(date_created__date=datetime.date(today))
    }
    return render(request, 'pins/today_pins.html', context)


def today_pins_list(request):
    """In this view all the Pins are displayed."""
    context = {
        'pins': Pins.objects.all()
    }
    return render(request, 'pins/home.html', context)


class PinCreateView(LoginRequiredMixin, CreateView):
    """This is pin create view."""
    model = Pins
    fields = ['category', 'image', 'title', 'description']
    success_url = reverse_lazy('pin-home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


@login_required
def pin_detail(request, **kwargs):
    """This the detail view of a pin.
    Follow and Unfollow functions are rendered using this view.
    Save and Un-save button are also rendered using this view.
    Queryset for recommended pins are also here."""

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

    curr_obj = Pins.objects.get(pk=kwargs.get('pk')).category.all()
    print([i.topic for i in curr_obj])

    recommended = Pins.objects.filter(category__topic__in=[i.topic for i in curr_obj]).distinct().exclude(pk=kwargs.get('pk'))

    context = {"object": Pins.objects.get(pk=kwargs.get('pk')),
               'saved': saved, 'is_followed': is_followed, 'board_choices': board_choices,
               'form': CommentForm(), 'recommended': recommended}

    return render(request, 'pins/pins_detail.html', context)


class PinUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """This is for pin update functionality."""
    model = Pins
    fields = ['image', 'title', 'description']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """This function is for checking if the user is the one has created this object."""
        pin = self.get_object()
        if self.request.user == pin.user:
            return True
        return False


class PinDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """This view is for deleting pin."""
    model = Pins
    success_url = '/'

    def test_func(self):
        """This function is for checking if the user is the one has created this object."""
        pin = self.get_object()
        if self.request.user == pin.user:
            return True
        return False


@login_required
def SearchResultView(request):
    """This view is for search filter.
    Search is done based on the category given in the pins."""
    topic = request.GET.get('q')
    topic = topic.split(' ')
    qset1 = reduce(operator.__or__,
                   [Q(category__topic__icontains=query) | Q(category__topic__icontains=query) for query in topic if query != ''])
    pi = Pins.objects.filter(qset1).distinct()

    # topic = topic.strip()
    # pi = Pins.objects.filter(category__topic__icontains=topic)

    return render(request, 'pins/search.html', {'topic': topic,
                                                'pins': pi})


class UserBoardView(LoginRequiredMixin, ListView):
    """This view is for user pin-board where user's created pins are displayed.
    Number of followers and followings are also displayed here."""
    model = Pins
    template_name = 'pins/pinboard.html'
    context_object_name = 'pins'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        new_var = User.objects.get(username=user).profile.image.url
        user_name = User.objects.get(username=user).username

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
    """This view contains the logic for saving the pins and un-save pins to user pin-board."""
    my_id = kwargs.get('pk')
    if request.method == "GET":
        pin_id = get_object_or_404(Pins, pk=kwargs.get('pk'))
        pin_saved_by_user = request.user.username
        pin_data = Pins.objects.get(pk=pin_id.id)
        saved = False

        if SavePin.objects.filter(pin=pin_data, user=User.objects.get(username=pin_saved_by_user)).exists():
            instance = SavePin.objects.get(pin=pin_data, user=User.objects.get(username=pin_saved_by_user))
            instance.delete()
            messages.success(request, f'You have unsaved a pin!!')
            saved = False
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
    return redirect('pin-detail', my_id)


# TODO -Filter all pins by users and display their saved pins.
class UserSavedPinsView(ListView, LoginRequiredMixin):
    """This view is for displaying saved pins of user to user's dashboard.
    It also displays number of followers and followings of user."""
    model = SavePin
    template_name = 'pins/pinboard_save.html'
    context_object_name = 'saved_pins'

    def get_context_data(self, **kwargs):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        new_var = User.objects.get(username=user).profile.image.url

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


class BoardCreateView(LoginRequiredMixin, CreateView):
    """This view is for creating board."""
    model = Board
    fields = ['title', 'category', 'image1', 'image2', 'image3', 'image4']
    template_name = 'pins/board_form.html'
    success_url = reverse_lazy('pin-home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


@login_required
def save_pin_board_view(request, p_id, b_id):
    """This view is for saving pins to board(Folder like structure created by user.) """
    pin_id = get_object_or_404(Pins, id=p_id)
    pin_saved_by_user = request.user.username
    board_id = get_object_or_404(Board, id=b_id)

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


class BoardDetailView(LoginRequiredMixin, DetailView):
    """This is for detail view of the board which is created by user."""
    model = Board
    template_name = 'pins/boards_detail.html'


class BoardUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """This view is for updating board which is created by user."""
    model = Board
    fields = ['title', 'image1', 'image2', 'image3', 'image4']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """This function is for checking if the user who is updating is the owner of the object or not."""
        pin = self.get_object()
        if self.request.user == pin.user:
            return True
        return False


class BoardDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """This view is for deleting the board created by user."""
    model = Board
    success_url = '/'

    def test_func(self):
        pin = self.get_object()
        if self.request.user == pin.user:
            return True
        return False


@login_required
def comment_create(request, **kwargs):
    """This view is for adding comments to the detail view of pin."""
    p_id = kwargs.get('pk')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form.instance.pins_id = p_id
            form.instance.name = request.user
            form.save()
            return redirect('pin-detail', p_id)
    else:
        form = CommentForm(request.POST)
    return redirect('pin-detail', p_id)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """This view is for creating Category of user's choice."""
    model = Category
    fields = ['topic']
    template_name = 'pins/categorys_form.html'
    success_url = reverse_lazy('pin-create')

    def form_valid(self, form):
        return super().form_valid(form)
