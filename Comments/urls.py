from django.conf.urls import url, patterns
from Comments import views

urlpatterns = patterns(
    '',
    url(r'^feed/$', views.feed, name='feed'),
    url(r'^bookmarks/$', views.bookmarks, name='bookmarks'),
    url(r'^post_comment/$', views.post_comment, name='post_comment'),
    url(r'^delete_comment/$', views.delete_comment, name='delete_comment'),
    url(r'^promote_comment/$', views.promote_comment, name='promote_comment'),
    url(r'^bookmark_comment/$', views.bookmark_comment, name='bookmark_comment'),
    url(r'^edit_comment/$', views.edit_comment, name='edit_comment'),
    url(r'^post_reply/$', views.post_reply, name='post_reply'),
    url(r'^vote_on_comment/$', views.vote_on_comment, name='vote_on_comment'),
    url(r'^update_comments/$', views.update_comments, name='update_comments'),
    url(r'^comment_list_page/$', views.comment_list_page, name='comment_list_page'),
)
