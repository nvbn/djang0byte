# -*- coding:utf-8 -*-
from django import dispatch

# Creation of a new link between Django user and Loginza identity.
# Parameters:
# - sender - HttpRequest instance
# - user_map - loginza.models.UserMap instance
created = dispatch.Signal(providing_args=['user_map'])

# Loginza athentication returned error
# Parameters:
# - sender - HttpRequest instance
# - error - loginza.authentication.LoginzaError instance
error = dispatch.Signal(providing_args=['error'])

# Successfull completion Loginza authentication
# Parameters:
# - sender: HttpRequest instance
# - user: authenticated (may be newly created) user
# - identity: loginza identity (loginza.models.Identity) used for authentication
#
# A handler may return a HttpRespose instance which will be eventually
# returned from the completion view. If omitted a standard redirect will be
# used.
authenticated = dispatch.Signal(providing_args=['user', 'identity'])

# login_required decorator found that user is not logged in
# Parameters:
# - sender: HttpRequest instance
#
# A handler may return a HttpRespose instance which will be eventually
# returned from called view. If omitted redirect to previous page will be
# used.
login_required = dispatch.Signal()