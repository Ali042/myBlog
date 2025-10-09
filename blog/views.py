from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post
from .forms import PostForm, ProfileForm
from .forms import CommentForm
from django.contrib.auth import get_user_model
from .models import Like, Comment, Follow

def post_list(request):
    q = request.GET.get("q", "")
    qs = Post.objects.all()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q) | Q(author__username__icontains=q))
    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    liked_ids = []
    if request.user.is_authenticated:
        liked_ids = list(
            Like.objects.filter(user=request.user, post__in=page_obj.object_list)
            .values_list("post_id", flat=True)
        )
    return render(
        request,
        "blog/post_list.html",
        {"page_obj": page_obj, "q": q, "liked_ids": liked_ids},
    )

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Comment submit
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("/admin/login/?next=" + request.path)
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(post=post, author=request.user, content=form.cleaned_data["content"]) 
            return redirect("post_detail", pk=post.pk)
    else:
        form = CommentForm()
    liked = False
    if request.user.is_authenticated:
        liked = Like.objects.filter(post=post, user=request.user).exists()
    return render(request, "blog/post_detail.html", {"post": post, "liked": liked, "comment_form": form})

@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm()
    return render(request, "blog/post_form.html", {"form": form})

def post_random(request):
    post = Post.objects.order_by('?').first()
    if post:
        return redirect("post_detail", pk=post.pk)
    return redirect("post_list")

def profile_view(request):
    user = request.user if request.user.is_authenticated else None
    posts = Post.objects.filter(author=user) if user else Post.objects.none()
    stats = {"posts": posts.count(), "followers": 0, "following": 0}
    if user:
        stats["followers"] = Follow.objects.filter(target=user).count()
        stats["following"] = Follow.objects.filter(user=user).count()
    context = {
        "user_profile": user,
        "posts": posts,
        "stats": stats,
    }
    return render(request, "blog/profile.html", context)

@login_required
def profile_edit(request):
    # Ensure profile exists
    profile = getattr(request.user, "profile", None)
    if profile is None:
        from .models import Profile
        profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "blog/profile_form.html", {"form": form})

def profile_user_view(request, username):
    User = get_user_model()
    target = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=target)
    stats = {
        "posts": posts.count(),
        "followers": Follow.objects.filter(target=target).count(),
        "following": Follow.objects.filter(user=target).count(),
    }
    is_following = False
    if request.user.is_authenticated and request.user != target:
        is_following = Follow.objects.filter(user=request.user, target=target).exists()
    context = {
        "user_profile": target,
        "posts": posts,
        "stats": stats,
        "is_following": is_following,
        "is_self": request.user.is_authenticated and request.user == target,
    }
    return render(request, "blog/profile.html", context)

@login_required
def follow_toggle(request, username):
    if request.method != "POST":
        return HttpResponseForbidden()
    User = get_user_model()
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({"error": "cannot_follow_self"}, status=400)
    obj, created = Follow.objects.get_or_create(user=request.user, target=target)
    following = True
    if not created:
        obj.delete()
        following = False
    counts = {
        "followers": Follow.objects.filter(target=target).count(),
        "following": Follow.objects.filter(user=target).count(),
    }
    return JsonResponse({"following": following, **counts})

def followers_list(request, username):
    User = get_user_model()
    target = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(target=target).select_related("user")
    return render(request, "blog/follow_list.html", {"target": target, "followers": followers, "mode": "followers"})

def following_list(request, username):
    User = get_user_model()
    target = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=target).select_related("target")
    return render(request, "blog/follow_list.html", {"target": target, "following": following, "mode": "following"})

@login_required
def like_toggle(request, pk):
    if request.method != "POST":
        return HttpResponseForbidden()
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    liked = True
    if not created:
        like.delete()
        liked = False
    count = post.likes.count()
    return JsonResponse({"liked": liked, "count": count})
