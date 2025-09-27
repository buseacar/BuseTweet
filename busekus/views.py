from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, Meep
from .forms import MeepForm, SignUpForm, ProfilePicForm, MeepSearchForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


def home(request):
    if request.user.is_authenticated:
        form = MeepForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            meep = form.save(commit=False)
            meep.user = request.user
            meep.save()
            messages.success(request, "Tweet Başarıyla Paylaşıldı.")
            return redirect('home')
        
        meeps = Meep.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"meeps": meeps, "form": form})
    else:
        meeps = Meep.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"meeps": meeps})


def profile_list(request):
    if request.user.is_authenticated:  
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {'profiles': profiles})
    else:
        messages.warning(request, "Bu sayfaya erişebilmek için giriş yapmanız gerekiyor.")
        return redirect('home')


def unfollow(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        request.user.profile.follows.remove(profile)
        request.user.profile.save()
        messages.success(request, f"Takipten çıkıldı: {profile.user.username}")
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.warning(request, "Takipten çıkmak için giriş yapmalısınız.")
        return redirect('home')
    
def follow(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        request.user.profile.follows.add(profile)
        request.user.profile.save()
        messages.success(request, f"Takipe Alındı: {profile.user.username}")
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.warning(request, "Takipten çıkmak için giriş yapmalısınız.")
        return redirect('home')




def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")

        if request.method == "POST":
            current_user_profile = request.user.profile
            action = request.POST.get('follow')
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)
            current_user_profile.save()
    
        return render(request, "profile.html", {"profile": profile, "meeps": meeps})
    else:
        messages.warning(request, "Bu sayfaya erişebilmek için giriş yapmanız gerekiyor.")
        return redirect('home')

def followers(request, pk):
    if request.user.is_authenticated: 
        if request.user.id == pk: 
            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'followers.html', {'profiles': profiles})
        else:
            messages.warning(request, "Sadece Kendi Takipçilerinizi Görebilirsiniz...")
            return redirect('home')
    else:
        messages.warning(request, "Bu sayfaya erişebilmek için giriş yapmanız gerekiyor.")
        return redirect('home')
    

def follows(request, pk):
    if request.user.is_authenticated: 
        if request.user.id == pk: 
            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'follows.html', {'profiles': profiles})
        else:
            messages.warning(request, "Sadece Kendi Takipçilerinizi Görebilirsiniz...")
            return redirect('home')
    else:
        messages.warning(request, "Bu sayfaya erişebilmek için giriş yapmanız gerekiyor.")
        return redirect('home')




def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password) 
        if user is not None:
            login(request, user)
            messages.success(request, "Giriş başarılı!")
            return redirect('home')
        else:
            messages.error(request, "Hatalı giriş, tekrar deneyin.")
            return redirect('login')
    return render(request, "login.html", {})


def logout_user(request):
    logout(request)
    messages.success(request, "Çıkış yapıldı.")
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']  # Düzeltildi: password1 alanı
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Kayıt başarılı, giriş yapıldı.")
            return redirect('home')
    return render(request, "register.html", {'form': form})


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)

        user_form = SignUpForm(request.POST or None, request.FILES or None, instance=current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            login(request, current_user)
            messages.success(request, "Güncelleme başarılı.")
            return redirect('home')

        return render(request, "update_user.html", {'user_form': user_form, 'profile_form': profile_form})
    else:
        messages.warning(request, "Sayfayı görüntülemek için giriş yapmalısınız.")
        return redirect('home')


def meep_like(request, pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        if request.user in meep.likes.all():
            meep.likes.remove(request.user)
        else:
            meep.likes.add(request.user)
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.warning(request, "Sayfayı görüntülemek için giriş yapmalısınız.")
        return redirect('home')


def meep_show(request, pk):
    meep = get_object_or_404(Meep, id=pk)
    return render(request, "show_meep.html", {'meep': meep})


def delete_meep(request, pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        if meep.user == request.user:  # Sadece meep'in sahibi silebilir
            meep.delete()
            messages.success(request, "Tweetiniz silinmiştir.")
        else:
            messages.warning(request, "Bu tweet'i silme yetkiniz yok.")
        return redirect(request.META.get("HTTP_REFERER", 'home'))
    else:
        messages.warning(request, "Tweet silebilmek için giriş yapmanız gerekiyor.")
        return redirect('home')


def meep_search(request):
    form = MeepSearchForm(request.GET or None)
    meeps = []

    if form.is_valid():
        query = form.cleaned_data.get('query')
        meeps = Meep.objects.filter(body__icontains=query).order_by('-created_at')

    return render(request, 'meep_search.html', {'form': form, 'meeps': meeps})

def user_search(request):
    query = request.GET.get('query', '')
    results = []
    if query:
        results = User.objects.filter(username__icontains=query)
    return render(request, 'user_search_results.html', {'results': results, 'query': query})
