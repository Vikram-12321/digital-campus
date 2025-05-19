from django.db import models

# ------------------------------------------------------------------
# Enum of types (keep as TEXT for readability)
# ------------------------------------------------------------------
class NotificationType(models.TextChoices):
    FOLLOW             = "FOLLOW",             "started following you"
    FOLLOW_REQUEST     = "FOLLOW_REQUEST",     "requested to follow you"
    ACCEPT_FOLLOW_REQ  = "ACCEPT_FOLLOW_REQ",  "accepted your follow request"

    EVENT_REQUEST      = "EVENT_REQUEST",      "requested to attend your event"
    EVENT_ACCEPT       = "EVENT_ACCEPT",       "accepted your event request"
    EVENT_ATTEND       = "EVENT_ATTEND",       "is attending your event"

    CLUB_JOIN_REQUEST  = "CLUB_JOIN_REQUEST",  "requested to join your club"
    CLUB_JOIN          = "CLUB_JOIN",          "joined your club"
    CLUB_JOIN_ACCEPT   = "CLUB_JOIN_ACCEPT",   "accepted your club-join request"

    @classmethod
    def get_dynamic_verb(cls, notification_type, actor, target=None):
        
        actor_name = getattr(actor, "username", "Someone")

        if notification_type == cls.FOLLOW:
            return f"{actor_name} started following you"
        elif notification_type == cls.FOLLOW_REQUEST:
            return f"{actor_name} has requested to follow you"
        elif notification_type == cls.ACCEPT_FOLLOW_REQ:
            return f"{actor_name} accepted your follow request"
        elif notification_type == cls.CLUB_JOIN_REQUEST:
            return f"{actor_name} has requested to join {getattr(target, 'name', 'your club')}"
        elif notification_type == cls.CLUB_JOIN:
            return f"{actor_name} has joined {getattr(target, 'name', 'your club')}"
        elif notification_type == cls.CLUB_JOIN_ACCEPT:
            return f"{actor_name} accepted your request to join {getattr(target, 'name', 'your club')}"
        elif notification_type == cls.EVENT_REQUEST:
            return f"{actor_name} has requested to attend {getattr(target, 'title', 'your event')}"
        elif notification_type == cls.EVENT_ATTEND:
            return f"{actor_name} is now attending {getattr(target, 'title', 'your event')}"
        elif notification_type == cls.EVENT_ACCEPT:
            return f"{actor_name} accepted your request to attend {getattr(target, 'title', 'your event')}"

        return f"{actor_name} did something"
