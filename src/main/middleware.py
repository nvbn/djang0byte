from django.shortcuts import render_to_response


class BansMiddleware(object):
    """
    Middleware that handles bans.
    """

    def process_request(self, request):
        if request.user.is_authenticated():
            profile = request.user.get_profile()
            block = profile.get_block()
            if block and block.check() and request.path != '/sorry/':
                return render_to_response('sorry.html', {
                    'user': request.user,
                    'block': block,
                })
        
