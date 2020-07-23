from django.db import models

from fb_post_clean_arch.constants.enums import ReactionType
from fb_post_clean_arch.models.comment import Comment
from fb_post_clean_arch.models.post import Post
from fb_post_clean_arch.models.user import User


class Reactions(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE,
                                default=None, null=True,
                                related_name='reactions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default=None,
                             null=True, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='reactions')
    Reaction_Choice = (
        (ReactionType.LIKE.value, ReactionType.LIKE.value),
        (ReactionType.WOW.value, ReactionType.WOW.value),
        (ReactionType.HAHA.value, ReactionType.HAHA.value),
        (ReactionType.DISLIKE.value, ReactionType.DISLIKE.value),
        (ReactionType.SAD.value, ReactionType.SAD.value),
        (ReactionType.ANGRY.value, ReactionType.ANGRY.value)
    )
    reaction_type = models.CharField(max_length=10, choices=Reaction_Choice,
                                     default=None, null=True)

    def __str__(self):
        return self.reaction_type
