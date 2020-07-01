# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader, Context

from mvc.models import User, Area, Category, Note
from twitterDemo.settings import PAGE_SIZE, FRIEND_LIST_MAX
from utils import function, mailer, formatter


def __check_login(_username, _password):
    _state = {
        'success': True,
        'message': 'none',
        'userid': -1,
        'realname': '',
    }

    try:
        _user = User.objects.get(username=_username)

        # to decide password
        if (_user.password == function.md5_encode(_password)):
            _state['success'] = True
            _state['userid'] = _user.id
            _state['realname'] = _user.realname
        else:
            # password incorrect
            _state['success'] = False
            _state['message'] = 'Password incorrect.'
    except (User.DoesNotExist):
        # user not exist
        _state['success'] = False
        _state['message'] = 'User does not exist.'

    return _state


def __do_login(request, _username, _password):
    _state = __check_login(_username, _password)
    if _state['success']:
        # save login info to session
        request.session['islogin'] = True
        request.session['userid'] = _state['userid']
        request.session['username'] = _username
        request.session['realname'] = _state['realname']

    return _state


def __is_login(request):
    return request.session.get('islogin', False)


def __result_message(request,
                     _title='Message',
                     _message='Unknow error,processing interrupted.',
                     _go_back_url=''):
    _islogin = __is_login(request)

    if _go_back_url == '':
        _go_back_url = function.get_referer_url(request)

    # body content
    _template = loader.get_template('result_message.html')

    _context = Context({
        'page_title': _title,
        'message': _message,
        'go_back_url': _go_back_url,
        'islogin': _islogin
    })

    _output = _template.render(_context.flatten())

    return HttpResponse(_output)


def signin(request):
    # get user login status
    _islogin = __is_login(request)

    try:
        # get post params
        _username = request.POST['username']
        _password = request.POST['password']
        _is_post = True
    except (KeyError):
        _is_post = False

    # check username and password
    if _is_post:
        _state = __do_login(request, _username, _password)

        if _state['success']:
            return __result_message(request, 'Login successed',
                                    'You are logied now.')
    else:
        _state = {'success': False, 'message': 'Please login first.'}

    # body content
    _template = loader.get_template('signin.html')
    _context = {
        'page_title': 'Signin',
        'state': _state,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)


def __check_username_exist(_username):
    _exist = True

    try:
        _user = User.objects.get(username=_username)
        _exist = True
    except (User.DoesNotExist):
        _exist = False

    return _exist


def __do_signup(request, _userinfo):
    _state = {
        'success': False,
        'message': '',
    }

    # check username exist
    if (_userinfo['username'] == ''):
        _state['success'] = False
        _state['message'] = '"Username" have not inputed.'
        return _state

    if (_userinfo['password'] == ''):
        _state['success'] = False
        _state['message'] = '"Password" have not inputed.'
        return _state

    if (_userinfo['realname'] == ''):
        _state['success'] = False
        _state['message'] = '"Real Name" have not inputed.'
        return _state

    if (_userinfo['email'] == ''):
        _state['success'] = False
        _state['message'] = '"Email" have not inputed.'
        return _state

    # check username exist
    if (__check_username_exist(_userinfo['username'])):
        _state['success'] = False
        _state['message'] = '"Username" have existed.'
        return _state

    # check password & confirm password
    if (_userinfo['password'] != _userinfo['confirm']):
        _state['success'] = False
        _state['message'] = '"Confirm Password" have not match.'
        return _state

    _user = User(
        username=_userinfo['username'],
        realname=_userinfo['realname'],
        password=_userinfo['password'],
        email=_userinfo['email'],
        area=Area.objects.filter().all()[0])
    # try:
    _user.save()
    _state['success'] = True
    _state['message'] = 'Successed.'
    # except:
    # _state['success'] = False
    # _state['message'] = '程序异常,注册失败.'

    # send regist success mail
    mailer.send_regist_success_mail(_userinfo)

    return _state


def signup(request):
    # check is login
    _islogin = __is_login(request)

    if (_islogin):
        return HttpResponseRedirect('/')

    _userinfo = {
        'username': '',
        'password': '',
        'confirm': '',
        'realname': '',
        'email': '',
    }

    try:
        # get post params
        _userinfo = {
            'username': request.POST['username'],
            'password': request.POST['password'],
            'confirm': request.POST['confirm'],
            'realname': request.POST['realname'],
            'email': request.POST['email'],
        }
        _is_post = True
    except (KeyError):
        _is_post = False

    if (_is_post):
        _state = __do_signup(request, _userinfo)
    else:
        _state = {'success': False, 'message': 'Signup'}

    if (_state['success']):
        return __result_message(request, 'Signup successed',
                                'Your account was registed success.')

    _result = {
        'success': _state['success'],
        'message': _state['message'],
        'form': {
            'username': _userinfo['username'],
            'realname': _userinfo['realname'],
            'email': _userinfo['email'],
        }
    }

    # body content
    _template = loader.get_template('signup.html')
    _context = {
        'page_title': 'Signup',
        'state': _result,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)


def __user_id(request):
    return request.session.get('userid', -1)


def __user_name(request):
    return request.session.get('username', '')


def index_user_page(request, _username, _page_index):
    # get user login status
    _islogin = __is_login(request)
    _page_title = 'Home'

    try:
        # get post params
        _message = request.POST['message']
        _is_post = True
    except (KeyError):
        _is_post = False

    # save message
    if _is_post:
        # check login
        if not _islogin:
            return HttpResponseRedirect('/signin/')

        # save messages
        (_category,
         _is_added_cate) = Category.objects.get_or_create(name='网页')

        try:
            _user = User.objects.get(id=__user_id(request))
        except:
            return HttpResponseRedirect('/signin/')

        _note = Note(message=_message, category=_category, user=_user)
        _note.save()

        return HttpResponseRedirect('/user/' + _user.username)

    _userid = -1
    # get message list
    _offset_index = (int(_page_index) - 1) * PAGE_SIZE
    _last_item_index = PAGE_SIZE * int(_page_index)

    _login_user_friend_list = None
    if _islogin:
        # get friend messages if user is logined
        _login_user = User.objects.get(username=__user_name(request))
        _login_user_friend_list = _login_user.friend.all()
    else:
        _login_user = None

    _friends = None
    _self_home = False
    if _username != '':
        # there is get user's messages
        _user = get_object_or_404(User, username=_username)
        _userid = _user.id
        _notes = Note.objects.filter(user=_user).order_by('-addtime')
        _page_title = u'%s' % _user.realname
        # get friend list
        # _friends = _user.friend.get_query_set().order_by("id")[0:FRIEND_LIST_MAX]
        _friends = _user.friend.order_by("id")[0:FRIEND_LIST_MAX]
        print("................", _friends)
        if (_userid == __user_id(request)):
            _self_home = True

    else:
        # get all messages
        _user = None

        if _islogin:
            _query_users = [_login_user]
            _query_users.extend(_login_user.friend.all())
            _notes = Note.objects.filter(
                user__in=_query_users).order_by('-addtime')
        else:
            # can't get  message
            _notes = []  # Note.objects.order_by('-addtime')

    # page bar
    _page_bar = formatter.pagebar(request, _notes, _page_index, _username)

    # get current page
    _notes = _notes[_offset_index:_last_item_index]

    _context = {
        'page_title': _page_title,
        'notes': _notes,
        'islogin': _islogin,
        'userid': __user_id(request),
        'self_home': _self_home,
        'user': _user,
        'page_bar': _page_bar,
        'friends': _friends,
        'login_user_friend_list': _login_user_friend_list,
    }

    return render(request, 'index.html', _context)



def index_page(request, _page_index):
    return index_user_page(request, '', _page_index)


def index_user(request, _username):
    return index_user_page(request, _username, 1)


def index_user_self(request):
    _user_name = __user_name(request)
    return index_user(request, _user_name)


def index(request):
    return index_user(request, '')
    _user_name = __user_name(request)
    return index_user(request, _user_name)


def detail(request, _id):
    # get user login status
    _islogin = __is_login(request)

    _note = get_object_or_404(Note, id=_id)

    # body content
    _template = loader.get_template('detail.html')

    _context = {
        'page_title': _('%s\'s message %s') % (_note.user.realname, _id),
        'item': _note,
        'islogin': _islogin,
        'userid': __user_id(request),
    }

    _output = _template.render(_context)

    return HttpResponse(_output)


def friend_remove(request, _username):
    """
    summary:
        解除与某人的好友关系
    """
    # check is login
    _islogin = __is_login(request)

    if (not _islogin):
        return HttpResponseRedirect('/signin/')

    _state = {
        "success": False,
        "message": "",
    }

    _user_id = __user_id(request)
    try:
        _user = User.objects.get(id=_user_id)
    except:
        return __result_message(request, _('Sorry'),
                                _('This user dose not exist.'))

    # check friend exist
    try:
        _friend = User.objects.get(username=_username)
        _user.friend.remove(_friend)
        return __result_message(request, 'Successed',
                                'Friend "%s" removed.' % _friend.realname)
    except:
        return __result_message(request, 'Undisposed',
                                'He/She dose not your friend,undisposed.')