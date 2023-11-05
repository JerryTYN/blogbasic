from django.shortcuts import render, redirect, get_object_or_404
from .form import RegisterForm, PostForm, UserUpdate, CommentForm, AuthorFollow
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Post, Category, Comment
from django.contrib import messages
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



# Create your views here.

def home(request):
    posts_per_page = 6
    all_posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(all_posts, posts_per_page)
    page = request.GET.get('page')
    try:
        # Lấy danh sách bài viết cho trang hiện tại
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Nếu 'page' không phải là số nguyên, trả về trang đầu tiên
        posts = paginator.page(1)
    except EmptyPage:
        # Nếu 'page' lớn hơn số trang có sẵn, trả về trang cuối cùng
        posts = paginator.page(paginator.num_pages)
    # posts = Post.objects.all().order_by('-created_at')
    
    return render(request, 'main/home.html', {'posts': posts})

def profile(request):
    user = request.user
    if user.is_authenticated:
        user_posts = Post.objects.filter(author=user)
        post_count = user_posts.count()
        
        has_avatar = hasattr(user, 'userprofile') and user.userprofile.avatar

        # Truy cập URL của avatar nếu có
        avatar_url = user.userprofile.avatar.url if has_avatar else None
    else:
        user_posts = None

    context = {
        'user': user,
        'avatar_url': avatar_url,
        'has_avatar': has_avatar,

        'user_posts': user_posts,
        'post_count': post_count
    }
    return render(request, 'main/profile.html', context=context)

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()
    return render(request, 'registration/sign_up.html', {"form": form})

@login_required(login_url='/login')
def LikeView(request, pk):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    
    if request.user in post.likes.all():
        # Đã thích bài viết, nên hủy thích
        post.likes.remove(request.user)
    else:
        # Chưa thích bài viết, thêm vào danh sách thích
        post.likes.add(request.user)

    return HttpResponseRedirect(reverse('post_detail', args=[str(pk)]))



@login_required(login_url='/login')
def post_detail(request, id):
    allpost = Post.objects.all().order_by('-view_count')
    
    # if request.user.is_authenticated:
    post_detail = Post.objects.get(id = id)
    author_posts = Post.objects.filter(author = post_detail.author)
    categories = Category.objects.annotate(post_count=Count('post'))
    comments=Comment.objects.filter(post=post_detail).order_by("-id")
    post_count = author_posts.count()
    author_id = post_detail.author
    like_count = post_detail.number_of_likes()
    user_has_liked = post_detail.likes.filter(id=request.user.id).exists()
    is_following = AuthorFollow.objects.filter(user=request.user, author=post_detail.author).exists()
    post_detail.view_count += 1
    post_detail.save()
    followers = AuthorFollow.objects.filter(author=post_detail.author).count()
    # print(followers)
    # print(allpost)
    view_number = post_detail.view_count
    # print(view_number, like_count)
    form = CommentForm(request.POST or None)
    if request.method=="POST":
        
        if form.is_valid():
            content = request.POST.get('content')
            comment = Comment.objects.create(post = post_detail, user = request.user, content = content)
            comment.save()
            return redirect(post_detail.get_absolute_url())
        else:
            form =CommentForm()
    
    context = {
        'followers': followers,
        'image_cover': post_detail.image_cover,
        'created_at': post_detail.created_at,
        'content': post_detail.content,
        'title': post_detail.title,
        'author': post_detail.author,
        'post_count': post_count,
        'allpost': allpost,
        'categories': categories,
        'form': form,
        'comments': comments,
        'post_detail_id': post_detail.id,
        'like_count': like_count,
        'user_has_liked': user_has_liked,
        'view_number':view_number,
        'is_following': is_following,
        'author_id': author_id
    }
    return render(request, 'main/detail_post.html', context=context)





def follow_author(request, author_id):
    user = request.user  # Người dùng đang thao tác
    author = User.objects.get(id=author_id)  # Bài viết mà người dùng muốn theo dõi tác giả của nó
    # post = Post.objects.get(id= id)
    if user.is_authenticated:
        # Kiểm tra xem người dùng đã theo dõi tác giả chưa
        if AuthorFollow.objects.filter(user=user, author=author).exists():
            # Người dùng đã follow, nên chúng ta sẽ unfollow
            AuthorFollow.objects.filter(user=user, author=author).delete()
            messages.success(request, "See You Again :(")
            
        else:
            # Người dùng chưa follow, chúng ta sẽ follow
            AuthorFollow.objects.create(user=user, author=author)
            messages.success(request, "You will receive an email notification about new Post from this Author")

        referrer = request.META.get('HTTP_REFERER', '')
        post_id = None

        # Xác định post_id dựa trên URL trang chi tiết
        if '/post-detail/' in referrer:
            parts = referrer.split('/')
            index = parts.index('post-detail')
            print(index)
            if index + 1 < len(parts):
                post_id = parts[index + 1]

        if post_id:
            # Redirect đến trang chi tiết của bài viết tương ứng
            # return redirect(post_id.get_absolute_url())
            return HttpResponseRedirect(reverse('post_detail', args=[post_id]))

          
    return HttpResponseRedirect(reverse('home'))
   

# //======CRUD=======//

@login_required(login_url='/login')
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, "Post Created!")
            
            send_new_post_notification(post)
            return redirect(post.get_absolute_url())
        else:
            messages.error(request, "Somethings wrong!")
            print(form.non_field_errors())  
    
    else:
        form = PostForm()

    return render(request, 'main/create_post.html', {'form': form})

def send_new_post_notification(post):
    # Lấy danh sách người theo dõi tác giả
    followers = AuthorFollow.objects.filter(author=post.author)
    subject = f'Thông báo bài viết mới từ {post.author.username}'
    message = f'Tác giả {post.author.username} đã đăng bài viết mới: {post.title} tại DangCapNhat'
    from_email = 'thinguyen280601@gmail.com'  # Email của bạn
    for follower in followers:
        to_email = follower.user.email
        send_mail(subject, message, from_email, [to_email])

@login_required(login_url='/login')
def delete_post(request, id):
    if request.user.is_authenticated:
        post = Post.objects.get(id=id)
        if request.user == post.author:
            post.delete()
            messages.success(request, "Post deleted!")
            return redirect('profile')
        else:
            messages.error(request, "You are not own this post!")
            return redirect ('login')
               
    else:
        return redirect ('login')

@login_required(login_url='/login')
def update_post(request, id):
    if request.user.is_authenticated:
        current_post = Post.objects.get(id=id)
        if request.user == current_post.author:
            if request.method == 'POST':
                form = PostForm(request.POST or None, request.FILES, instance=current_post, )
                if form.is_valid():
                    form.save()
                    messages.success(request, "Post Updated!")
                    return redirect('profile')  # Redirect to profile or detail page as needed.
            else:
                form = PostForm(instance=current_post)
            return render(request, 'main/edit_post.html', {'form': form})
        else:
            messages.error(request, "You do not own this post!")
            return redirect('login')  # Redirect to the login page if the user does not own the post.
    else:
        return redirect('login')


@login_required(login_url='/login')
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdate(request.POST,request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')  # Điều hướng đến trang cá nhân hoặc trang khác nếu cần thiết.
    else:
        form = UserUpdate(instance=request.user)
    return render(request, 'main/update_profile.html', {'form': form})


# def search_posts(request):  
#     query = request.GET.get('q') 
#     if query:
#         posts = Post.objects.filter(title__icontains=query) 
#     else:
#         posts = Post.objects.all()

#     context = {
#         'query': query,
#         'posts': posts,
#     }

#     return render(request, 'main/search_results.html', context)
def search_posts(request):
    query = request.GET.get('q')
    page_number = request.GET.get('page')  # Lấy số trang từ tham số 'page' trong URL
    if not page_number:
        page_number = 1  # Mặc định hiển thị trang 1 nếu không có tham số 'page'

    if query:
        posts = Post.objects.filter(title__icontains=query)
    else:
        posts = Post.objects.all()

    # Số bài viết trên mỗi trang (thay đổi số bài viết trên trang tùy ý)
    posts_per_page = 6 
    paginator = Paginator(posts, posts_per_page)

    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(1)  # Hiển thị trang 1 nếu số trang không hợp lệ

    context = {
        'query': query,
        'posts': page,  # Truyền page thay vì posts
    }

    return render(request, 'main/search_results.html', context)

# def posts_by_category(request, category_id):
#     category = get_object_or_404(Category, id=category_id)
#     posts = Post.objects.filter(categories=category)

#     context = {
#         'category': category,
#         'posts': posts,
#     }

#     return render(request, 'main/search_results.html', context)

def posts_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(categories=category)

    page_number = request.GET.get('page')  # Lấy số trang từ tham số 'page' trong URL
    if not page_number:
        page_number = 1  # Mặc định hiển thị trang 1 nếu không có tham số 'page'

    # Số bài viết trên mỗi trang (thay đổi số bài viết trên trang tùy ý)
    posts_per_page = 6
    paginator = Paginator(posts, posts_per_page)

    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = paginator.page(1)  # Hiển thị trang 1 nếu số trang không hợp lệ

    context = {
        'category': category,
        'posts': page,  # Truyền page thay vì posts
    }

    return render(request, 'main/search_results.html', context)

