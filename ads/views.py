from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Ad, Category
from .forms import AdForm



def ad_list(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    category_slug = request.GET.get('category', '')
    categories = Category.objects.all()

    ads = Ad.objects.filter(is_approved=True)

    if query:
        ads = ads.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if location:
        ads = ads.filter(location__icontains=location)
    if min_price:
        ads = ads.filter(price_per_day__gte=min_price)
    if max_price:
        ads = ads.filter(price_per_day__lte=max_price)
    if category_slug:
        ads = ads.filter(categories__slug=category_slug)

    paginator = Paginator(ads, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ads/ad_list.html', {'page_obj': page_obj, 'categories': categories})

def ad_detail(request, pk):
    ad = get_object_or_404(Ad, pk=pk, is_approved=True)

    # Пагинация отзывов (5 на страницу)
    reviews_list = ad.reviews.all().order_by('-created_at')
    paginator = Paginator(reviews_list, 5)  # 5 отзывов на страницу
    page_number = request.GET.get('reviews_page')  # отдельный параметр, чтобы не конфликтовать
    reviews_page_obj = paginator.get_page(page_number)

    return render(request, 'ads/ad_detail.html', {
        'ad': ad,
        'reviews_page_obj': reviews_page_obj,
    })


@login_required
def ad_create(request):
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.author = request.user
            ad.is_approved = False  # на модерацию
            ad.save()
            form.save_m2m()
            messages.success(request, 'Объявление отправлено на модерацию.')
            return redirect('ad_list')
    else:
        form = AdForm()
    return render(request, 'ads/ad_form.html', {'form': form, 'title': 'Создать объявление'})


@login_required
def ad_edit(request, pk):
    ad = get_object_or_404(Ad, pk=pk, author=request.user)
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление обновлено.')
            return redirect('ad_detail', pk=ad.pk)
    else:
        form = AdForm(instance=ad)
    return render(request, 'ads/ad_form.html', {'form': form, 'title': 'Редактировать'})


@login_required
def ad_delete(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    # Разрешить удаление, если пользователь автор или является персоналом (админ/модератор)
    if request.user == ad.author or request.user.is_staff:
        if request.method == 'POST':
            ad.delete()
            messages.success(request, 'Объявление удалено.')
            return redirect('ad_list')
        return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})
    else:
        messages.error(request, 'У вас нет прав на удаление этого объявления.')
        return redirect('ad_detail', pk=ad.pk)


@staff_member_required
def ad_moderation(request):
    pending_ads = Ad.objects.filter(is_approved=False).order_by('-created_at')
    if request.method == 'POST':
        approved_count = 0
        deleted_count = 0

        for ad in pending_ads:
            action = request.POST.get(f'approve_{ad.id}')
            if action == 'approve':
                ad.is_approved = True
                ad.save()
                approved_count += 1
            elif action == 'delete':
                ad.delete()
                deleted_count += 1
            # Если action не передан или имеет другое значение – просто пропускаем

        # Формируем детализированное сообщение
        if approved_count and deleted_count:
            messages.success(
                request,
                f'Модерация выполнена: одобрено {approved_count}, удалено {deleted_count}.'
            )
        elif approved_count:
            messages.success(
                request,
                f'Модерация выполнена: одобрено {approved_count} объявлений.'
            )
        elif deleted_count:
            messages.success(
                request,
                f'Модерация выполнена: удалено {deleted_count} объявлений.'
            )
        else:
            messages.info(request, 'Действий не выполнено.')

        return redirect('ad_moderation')

    return render(request, 'ads/moderation.html', {'ads': pending_ads})


@login_required
def my_ads(request):
    """Список объявлений текущего пользователя"""
    ads_list = Ad.objects.filter(author=request.user).order_by('-created_at')
    paginator = Paginator(ads_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ads/my_ads.html', {'page_obj': page_obj})