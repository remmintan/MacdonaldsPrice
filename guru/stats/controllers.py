from macprice import models as db


def getChats():
    chats = db.Chat.objects.filter(chatType='private').order_by('-lastRequest')
    users = []

    getDate = lambda date: str(date) if date > 9 else "0" + str(date)

    i = 0

    for chat in chats:
        i += 1
        user = db.User.objects.get(pk=chat.id)
        name = "%s %s" % (user.name, user.surname)
        last = "%s %s %i %s:%s" % (
        getDate(chat.lastRequest.day), getDate(chat.lastRequest.month), chat.lastRequest.year,
        getDate(chat.lastRequest.hour), getDate(chat.lastRequest.minute))

        users.append({
            'num': i,
            'name': name,
            'id': user.pk,
            'req': chat.requests,
            'last': last
        })

    return users
