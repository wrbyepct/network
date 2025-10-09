import logging
from math import ceil

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from network.albums.models import Album, AlbumMedia
from network.posts.models import Post, PostMedia
from network.profiles.models import Profile

from .models import Egg

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=Post)
def invalidate_profile_posts_cache(sender, instance, **kwargs):
    logger.info("Post is changing...")
    user = instance.user
    pages = get_page_num(user.posts.all())
    username = user.profile.username

    for page_num in range(1, pages + 1):
        key = make_template_fragment_key("profile_posts", [username, page_num])
        cache.delete(key)


@receiver([post_save, post_delete], sender=Egg)
def invalidate_profile_nest_cache(sender, instance, **kwargs):
    logger.info("Egg is changing...")
    username = instance.user.profile.username
    key = make_template_fragment_key("profile_nest", [username])

    cache.delete(key)


@receiver([post_save, post_delete], sender=PostMedia)
def invalidate_profile_media_cache(sender, instance, **kwargs):
    pages = get_page_num(instance.post.medias.all())

    username = instance.profile.username
    for page_num in range(1, pages + 1):
        key = make_template_fragment_key("profile_uploads", [username, page_num])
        cache.delete(key)


@receiver([post_save, post_delete], sender=Album)
def invalidate_profile_album_cache(sender, instance, **kwargs):
    profile = instance.profile
    username = profile.username
    pages = get_page_num(instances=profile.albums.all())
    for page_num in range(1, pages + 1):
        albums_paginator_key = make_template_fragment_key(
            "profile_albums_paginator", [username, page_num]
        )
        cache.delete(albums_paginator_key)


@receiver([post_save, post_delete], sender=AlbumMedia)
def invalidate_album_media_cache(sender, instance, **kwargs):
    album = instance.album

    pages = get_page_num(album.medias.all())

    album_id = album.pkid

    for page_num in range(1, pages + 1):
        key = make_template_fragment_key("album_media_paginator", [album_id, page_num])
        cache.delete(key)


@receiver([m2m_changed], sender=Profile.following.through)
def invalidate_followers_paginator_cache(
    sender, instance, action, reverse, pk_set, **kwargs
):
    # A follows B -> A following(reverse field) add B

    if action in ["post_add", "post_remove", "post_clear"] and reverse:
        # B followers haved changed, invalidate for B followers page
        followers_changed_profile = Profile.objects.filter(pk__in=pk_set).first()

        logger.info("Profile follower changed")
        logger.info(f"The profile changed is {followers_changed_profile.username}")
        pages = get_page_num(followers_changed_profile.followers.all())
        for page_num in range(1, pages + 1):
            key = make_template_fragment_key(
                "profile_followers_paginator",
                [followers_changed_profile.username, page_num],
            )
            cache.delete(key)

        # A following has chaged, invalidate for A's following page
        following_changed_profile = instance
        pages = get_page_num(following_changed_profile.following.all())
        for page_num in range(1, pages + 1):
            key = make_template_fragment_key(
                "profile_following_paginator",
                [following_changed_profile.username, page_num],
            )
            cache.delete(key)


def get_page_num(instances):
    instances_count = instances.count()
    return ceil(instances_count / 10)
