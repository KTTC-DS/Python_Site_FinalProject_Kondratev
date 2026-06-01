from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ads.models import Ad
from .models import Review
from .forms import ReviewForm


@login_required
def add_review(request, ad_pk):
    ad = get_object_or_404(Ad, pk=ad_pk, is_approved=True)
    if Review.objects.filter(ad=ad, author=request.user).exists():
        messages.error(request, 'Вы уже оставляли отзыв на это объявление.')
        return redirect('ad_detail', pk=ad.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.ad = ad
            review.author = request.user
            review.save()
            messages.success(request, 'Спасибо за отзыв!')
            return redirect('ad_detail', pk=ad.pk)
    else:
        form = ReviewForm()
    return render(request, 'reviews/review_form.html', {'form': form, 'ad': ad})