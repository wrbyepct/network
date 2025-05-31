"""User factory."""

import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """User factory."""

    class Meta:
        model = User

    email = factory.Sequence(
        lambda n: f"username{n}@example.com"
    )  # Expect it to fail and find out why
    password = factory.Faker("password")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):  # noqa: ANN206
        """Override the create method to use custom user manager."""
        manager = cls._get_manager(model_class)
        if "is_superuser" in kwargs:
            return manager.create_superuser(*args, **kwargs)
        return manager.create_user(*args, **kwargs)
