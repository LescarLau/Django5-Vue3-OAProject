def get_responser(request):
    user = request.user
    if user.department.leader.uid == user.uid:
        if user.department.name == '董事会':
            responser = None
        else:
            responser = user.department.manager
    else:
        responser = user.department.leader
    return responser