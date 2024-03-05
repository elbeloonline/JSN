from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.shortcuts import render

from orders.models import Client, UserClient
from orders.utils import OrderUtils

# Create your views here.

@login_required
def index(request, client_id=0, add_id=0):
    current_user = request.user
    if add_id:
        u = UserClient.objects.get_or_create(client_id=client_id, user_id=add_id)
        # u = UserClient(client_id=client_id, user_id=add_id)
        # u.save()

    user_client_id_list = OrderUtils.get_user_client_ids(current_user)
    user_is_superuser = current_user.is_superuser and current_user.is_active

    if not user_is_superuser:
        sql = "Select * from orders_client where client_id IN (%s) order by client_name"
        user_clients_list = Client.objects.raw(sql, [user_client_id_list])
    else:
        user_clients_list = Client.objects.all().order_by('client_name')
    context = {'clients': user_clients_list}

    # only run this if a client has been selected to populate the right-half of the screen
    if client_id:
        User = get_user_model()

        # assigned_users = UserClient.objects.filter(client_id=client_id)
        sql = "select * from users_user INNER JOIN orders_userclient ON orders_userclient.user_id = users_user.id where orders_userclient.client_id = (%s)"
        assigned_users = User.objects.raw(sql, [client_id])
        context['assigned_users'] = assigned_users
        # context['my_perms'] = current_user.user_permissions.all()

        a_ids = []
        for x in assigned_users:
            a_ids.append(x.id)

        users_list = User.objects.filter(is_superuser=0).filter(is_active=1)
        # sql = "select * from users_user INNER JOIN orders_userclient ON orders_userclient.user_id = users_user.id where orders_userclient.client_id = (%s) and orders_userclient.user_id not in (%s)"
        # unassigned_users = User.objects.raw(sql, [client_id, a_ids])
        # context['users'] = unassigned_users
        context['users'] = users_list
        context['selected_client'] = Client.objects.get(id=client_id)

    if not client_id:
        return render(request, 'usermgmt/userclient_edit.html', context)
    else:
        return render(request, 'usermgmt/userclient_useredit.html', context)

def new_user(request):
    from django.contrib.auth import login, authenticate
    from django.contrib import messages
    from django.shortcuts import render, redirect
    from .forms import SignUpForm

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            # login(request, user)  # this will log you in as that user!
            # return redirect('home')
            # @TODO: show success message
            form = SignUpForm()
            messages.success(request, 'User registration for {} was successful'.format(username))
    else:
        form = SignUpForm()
    return render(request, 'usermgmt/signup.html', {'form': form})
