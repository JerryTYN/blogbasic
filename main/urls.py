from django.urls import path
from . import views

urlpatterns = [
   path('', views.home, name='home'),
   path('home/', views.home, name='home'),  
   path('sign-up/', views.sign_up, name='sign_up'),  
   path('create-post/', views.create_post, name='create_post'),
   path('profile/', views.profile, name='profile'),
   path('delete-post/<int:id>/', views.delete_post, name='delete_post'),  
   path('edit-post/<int:id>/', views.update_post, name='update_post'),  
   path('update-info/', views.update_profile, name='update_profile'),
   path('post-detail/<int:id>', views.post_detail, name='post_detail'), 
   path('search/', views.search_posts, name='search_posts'),
   path('category/<int:category_id>/', views.posts_by_category, name='posts_by_category'),
   path('like/<int:pk>/', views.LikeView, name='like_post'),
   path('follow/<int:author_id>/', views.follow_author, name='follow_author'),
]
