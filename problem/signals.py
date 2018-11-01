from django.conf import settings
from django.dispatch import receiver
from django.db.models import signals

from problem.models import Problem


@receiver(signals.pre_save, sender=Problem)
def update_difficulty(sender, instance=None, **kwargs):
    """Dynamically update difficulty of problem."""
    # Only submission count bigger than base count will trigger this
    # action.
    base_count = settings.DIFFICULTY_BASE_SUBMISSIONS_COUNT

    # Invalid problem is not in account.
    if getattr(instance, 'pk', None) \
       and instance.is_valid \
       and instance.submission_number >= base_count:
        rate = instance.accepted_number / instance.submission_number
        for difficulty, level in settings.DIFFICULTY_RATE_MAP.items():
            if rate <= level:
                instance.difficulty = difficulty

        return instance
