from django.shortcuts import redirect

class my_mid:
    def __init__(self, get_response):
        print('--------------init')
        self.get_response = get_response

    def __call__(self,request):
        print('--------------request')
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        print("request is", request)
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, *view_args, **view_kwargs):
        # session = request.session.get("user_account")
        # if session:
        #     pass
        # else:
        #     return redirect("/login")
        print('--------------view',view_func.__doc__)

    def process_response(self,request, response):
        print('--------------response')
        return response