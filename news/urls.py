from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('work/', views.init_data, name='init'),
    path('<int:page_id>/', views.index_page, name='index_page'),
    path('detail/<int:news_id>/', views.detail, name='detail'),
    path('tag/<str:tag_string>/', views.category, name='category'),
    path('abstract/', views.get_abstract, name='abstract'),
    path('fenci/', views.fenci, name='fenci'),
]