Event.py
event_fun_dict = {}

def add_event2dict(event_name):
    '''
    将事件名和对应函数名添加到字典的装饰器
    '''
    def set_fun(fun):
        global event_fun_dict
        event_fun_dict[event_name] = fun  # 这一步只有装饰的时候才会被调用
        def call_fun(*args, **kwargs):
            return fun(*args, **kwargs)
        return call_fun
    return set_fun


@add_event2dict("example_event")  # 相当于 @setfun
def example_event(socket,  header_dict, body, *args):
    print("收到example事件", header_dict, body)
    respond_dict = {}
    respond_body = 'example_event respond'
    return respond_dict, respond_body


@add_event2dict("example_event2")  # 相当于 @setfun
def example_event2(socket,  header_dict, body, *args):
    print("收到example2事件", header_dict, body)
    respond_dict = {}
    respond_body = ''
    return respond_dict, respond_body
