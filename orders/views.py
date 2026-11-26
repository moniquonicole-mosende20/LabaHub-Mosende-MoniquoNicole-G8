from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import User

from .forms import ServiceForm
from .models import Service


@login_required
def service_list(request):
    if request.user.role == User.Role.ADMIN:
        services = Service.objects.all()
    else:
        services = Service.objects.filter(is_active=True)
    return render(request, 'orders/service_list.html', {'services': services})


@role_required(User.Role.ADMIN)
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service added successfully.')
            return redirect('service_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = ServiceForm()
    return render(request, 'orders/service_form.html', {'form': form, 'title': 'Add service'})


@role_required(User.Role.ADMIN)
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully.')
            return redirect('service_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'orders/service_form.html', {'form': form, 'title': 'Edit service'})


@role_required(User.Role.ADMIN)
@require_POST
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    try:
        service.delete()
        messages.success(request, f'Service "{service.name}" deleted.')
    except ProtectedError:
        messages.error(
            request,
            'This service already has orders, so it cannot be deleted. '
            'Edit it and untick "Available to customers" instead.',
        )
    return redirect('service_list')