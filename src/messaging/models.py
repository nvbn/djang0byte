from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.db import models
from messaging.exceptions import RemoveNotPermittedError
from tools.exceptions import AlreadyRemovedError


class Message(models.Model):
    """Private message"""
    REMOVED_NO = 0
    REMOVED_SENDER = 1
    REMOVED_RECEIVER = 2
    REMOVED_TOGETHER = 3
    REMOVED = (
        (REMOVED_NO, _('not removed')),
        (REMOVED_SENDER, _('removed by sender')),
        (REMOVED_RECEIVER, _('removed by receiver')),
        (REMOVED_TOGETHER, _('removed together')),
    )

    sender = models.ForeignKey(
        User, related_name='sended', verbose_name=_('sender'),
    )
    receiver = models.ForeignKey(
        User, related_name='received', verbose_name=_('receiver'),
    )
    title = models.CharField(max_length=300, verbose_name=_('title'))
    content = models.TextField(verbose_name=_('content'))
    showed = models.BooleanField(
        default=False, verbose_name=_('showed'),
    )
    removed_status = models.PositiveSmallIntegerField(
        default=REMOVED_NO, choices=REMOVED,
    )

    def remove(self, user):
        """Remove message by user"""
        if user not in (self.sender, self.receiver):
            raise RemoveNotPermittedError(self)
        if self.is_removed(user):
            raise AlreadyRemovedError(self)
        if self.sender == user:
            if self.removed_status == Message.REMOVED_NO:
                self.removed_status = Message.REMOVED_SENDER
            else:
                self.removed_status = Message.REMOVED_TOGETHER
        else:
            if self.removed_status == Message.REMOVED_NO:
                self.removed_status = Message.REMOVED_RECEIVER
            else:
                self.removed_status = Message.REMOVED_TOGETHER

    def is_removed(self, user):
        """Check message is removed"""
        if self.removed_status == Message.REMOVED_TOGETHER or \
            self.sender == user and self.removed_status == Message.REMOVED_SENDER or \
            self.receiver == user and self.removed_status == Message.REMOVED_RECEIVER:
            return True
        else:
            return False

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __unicode__(self):
        return self.title    
