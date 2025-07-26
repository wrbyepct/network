from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from network.posts.models import Post


@pytest.mark.django_db
def test_post_create_view_sets_random_publish_at(client):
    """Test that PostCreateView automatically sets a future publish_at."""
    user = baker.make(settings.AUTH_USER_MODEL)
    client.force_login(user)

    post_data = {
        "content": "This is a test post content.",
    }
    response = client.post(reverse("post_create"), post_data)
    assert response.status_code == HTTPStatus.FOUND  # Should redirect on success

    created_post = Post.objects.get(content="This is a test post content.")
    assert created_post.publish_at is not None
    assert created_post.publish_at > timezone.now()
    assert created_post.is_published is False


@pytest.mark.django_db
def test_post_list_view_filters_by_is_published(client):
    """Test that PostListView only shows posts with is_published=True."""
    user = baker.make(settings.AUTH_USER_MODEL)

    total_posts = 2
    # Create a published post
    published_post = baker.make(Post, user=user, is_published=True)

    # Create an incubating post
    incubating_post = baker.make(Post, user=user, is_published=False)

    response = client.get(reverse("index"))
    assert response.status_code == HTTPStatus.OK

    # Check that only the published_post is visible
    posts_in_context = response.context["posts"]
    assert posts_in_context.count() == 1
    assert posts_in_context.first() == published_post

    # Simulate the incubating post being published
    incubating_post.is_published = True
    incubating_post.save()

    response_after_publish = client.get(reverse("index"))
    assert response_after_publish.status_code == HTTPStatus.OK
    posts_in_context_after_publish = response_after_publish.context["posts"]
    assert (
        posts_in_context_after_publish.count() == total_posts
    )  # Both posts should now be visible
    assert published_post in posts_in_context_after_publish
    assert incubating_post in posts_in_context_after_publish


@pytest.mark.django_db
def test_post_modal_view_only_shows_published_posts(client):
    """Test that PostModalView only shows published posts."""
    user = baker.make(settings.AUTH_USER_MODEL)

    published_post = baker.make(Post, user=user, is_published=True)
    incubating_post = baker.make(Post, user=user, is_published=False)

    # Try to access published post
    response_published = client.get(reverse("post_modal", args=[published_post.id]))
    assert response_published.status_code == HTTPStatus.OK
    assert response_published.context["post"] == published_post

    # Try to access incubating post
    response_incubating = client.get(reverse("post_modal", args=[incubating_post.id]))
    assert (
        response_incubating.status_code == HTTPStatus.NOT_FOUND
    )  # Should return 404 for unpublished post
