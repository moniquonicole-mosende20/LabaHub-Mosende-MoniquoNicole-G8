from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import User

from .forms import OrderForm, OrderStatusForm, ServiceForm
from .models import Order, Service


# ---------- Services ----------

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


# ---------- Orders ----------

def _get_order_or_404(request, pk):
    """Admins can open any order; customers only their own (others get a 404)."""
    orders = Order.objects.select_related('customer', 'service')
    if request.user.role != User.Role.ADMIN:
        orders = orders.filter(customer=request.user)
    return get_object_or_404(orders, pk=pk)


@login_required
def order_list(request):
    orders = Order.objects.select_related('customer', 'service')
    if request.user.role != User.Role.ADMIN:
        orders = orders.filter(customer=request.user)
    selected = request.GET.get('status', '')
    if selected in Order.Status.values:
        orders = orders.filter(status=selected)
    context = {'orders': orders, 'statuses': Order.Status.choices, 'selected': selected}
    return render(request, 'orders/order_list.html', context)


@role_required(User.Role.CUSTOMER)
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            order.save()
            messages.success(request, f'Order #{order.pk} placed successfully.')
            return redirect('order_detail', pk=order.pk)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = OrderForm(initial={'service': request.GET.get('service')})
    return render(request, 'orders/order_form.html', {'form': form, 'title': 'Place a laundry order'})


@login_required
def order_detail(request, pk):
    order = _get_order_or_404(request, pk)
    context = {'order': order}
    if request.user.role == User.Role.ADMIN:
        context['status_form'] = OrderStatusForm(instance=order)
    return render(request, 'orders/order_detail.html', context)


@role_required(User.Role.CUSTOMER)
def order_update(request, pk):
    order = _get_order_or_404(request, pk)
    if not order.is_pending:
        messages.error(request, 'Only pending orders can be edited.')
        return redirect('order_detail', pk=order.pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'Order #{order.pk} updated successfully.')
            return redirect('order_detail', pk=order.pk)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = OrderForm(instance=order)
    return render(request, 'orders/order_form.html', {'form': form, 'title': f'Edit order #{order.pk}'})


@role_required(User.Role.CUSTOMER)
@require_POST
def order_cancel(request, pk):
    order = _get_order_or_404(request, pk)
    if not order.is_pending:
        messages.error(request, 'Only pending orders can be cancelled.')
    else:
        order.status = Order.Status.CANCELLED
        order.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Order #{order.pk} was cancelled.')
    return redirect('order_detail', pk=order.pk)


@login_required
@require_POST
def order_delete(request, pk):
    order = _get_order_or_404(request, pk)
    is_admin = request.user.role == User.Role.ADMIN
    if not is_admin and order.status != Order.Status.CANCELLED:
        messages.error(request, 'Only cancelled orders can be deleted. Cancel the order first.')
        return redirect('order_detail', pk=order.pk)
    number = order.pk
    order.delete()
    messages.success(request, f'Order #{number} deleted.')
    return redirect('order_list')


@role_required(User.Role.ADMIN)
@require_POST
def order_status_update(request, pk):
    order = _get_order_or_404(request, pk)
    form = OrderStatusForm(request.POST, instance=order)
    if form.is_valid():
        order = form.save(commit=False)
        order.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Order #{order.pk} is now {order.get_status_display()}.')
    else:
        errors = '; '.join(e for errs in form.errors.values() for e in errs)
        messages.error(request, errors)
    return redirect('order_detail', pk=order.pk)