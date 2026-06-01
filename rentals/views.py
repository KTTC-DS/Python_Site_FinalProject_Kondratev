from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from ads.models import Ad
from .models import RentalRequest, Transaction
from .forms import RentalRequestForm


@login_required
def create_rental_request(request, ad_pk):
    ad = get_object_or_404(Ad, pk=ad_pk, is_approved=True)

    # Проверка: автор не может арендовать своё объявление
    if request.user == ad.author:
        messages.error(request, 'Вы не можете арендовать собственное объявление.')
        return redirect('ad_detail', pk=ad.pk)

    if request.method == 'POST':
        # Передаём в форму объект ad для проверок
        form = RentalRequestForm(request.POST, ad=ad)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.ad = ad
            rental.renter = request.user
            rental.save()
            messages.success(request, 'Запрос на аренду отправлен владельцу.')
            return redirect('my_rental_requests')
        # Если форма невалидна, она уже содержит ошибки, которые будут отображены в шаблоне
    else:
        form = RentalRequestForm(ad=ad)

    return render(request, 'rentals/rental_request_form.html', {'form': form, 'ad': ad})

@login_required
def my_rental_requests(request):
    """Мои запросы (арендатор)"""
    requests_list = RentalRequest.objects.filter(renter=request.user).order_by('-created_at')
    paginator = Paginator(requests_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'rentals/my_rental_requests.html', {'page_obj': page_obj})

@login_required
def incoming_rental_requests(request):
    """Входящие запросы (владелец объявления)"""
    requests_list = RentalRequest.objects.filter(ad__author=request.user).order_by('-created_at')
    paginator = Paginator(requests_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'rentals/incoming_requests.html', {'page_obj': page_obj})

@login_required
def update_rental_request_status(request, pk, status):
    """Изменение статуса запроса (одобрить/отклонить/отменить)"""
    rental = get_object_or_404(RentalRequest, pk=pk)
    if request.user == rental.ad.author and status in ['approved', 'rejected']:
        rental.status = status
        rental.save()
        messages.success(request, f'Статус изменён на {rental.get_status_display()}.')
    elif request.user == rental.renter and status == 'cancelled':
        rental.status = status
        rental.save()
        messages.success(request, 'Запрос отменён.')
    else:
        messages.error(request, 'Недостаточно прав.')
    return redirect('incoming_rental_requests' if request.user == rental.ad.author else 'my_rental_requests')

@login_required
def mark_transaction_paid(request, rental_pk):
    """Имитация оплаты: создаёт транзакцию и помечает оплаченной"""
    rental = get_object_or_404(RentalRequest, pk=rental_pk, renter=request.user, status='approved')
    if not hasattr(rental, 'transaction'):
        days = (rental.end_date - rental.start_date).days
        amount = rental.ad.price_per_day * days * rental.quantity
        Transaction.objects.create(
            rental_request=rental,
            amount=amount,
            is_paid=True,
            transaction_id=f"SIM_{rental.pk}_{request.user.id}"
        )
        messages.success(request, 'Оплата прошла успешно (имитация).')
    else:
        messages.warning(request, 'Транзакция уже существует.')
    return redirect('my_rental_requests')
