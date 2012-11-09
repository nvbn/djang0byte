class AlreadySubscribedError(Exception):
    """Already subscribed error"""


class NotSubscribedError(Exception):
    """Not subscribed error"""


class AlreadyStarredError(Exception):
    """Already starred error"""


class NotStarredError(Exception):
    """Not starred error"""


class AlreadyAnsweredError(Exception):
    """Already answered error"""


class NotSeveralQuizError(Exception):
    """Not several quiz error"""


class AlreadyIgnoredError(Exception):
    """Already ignored error"""


class VoteForIgnoredError(Exception):
    """Answer for ignored error"""


class IgnoreForVotedError(Exception):
    """Ignore for voted error"""


class NotQuestionError(Exception):
    """Not question error"""


class SolutionAlreadyExistError(Exception):
    """Solution already exist error"""


class SoulutionDoesNotExistError(Exception):
    """Solution does not exist error"""


class WrongSolutionHolderError(Exception):
    """Wrong solution holder error"""
