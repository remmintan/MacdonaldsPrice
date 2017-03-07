from macprice import models as db


def get_chats():
    chats = db.Chat.objects.filter(chatType='private').order_by('-lastRequest')
    users = []

    def get_date(date): str(date) if date > 9 else "0" + str(date)

    i = 0

    for chat in chats:
        i += 1
        user = db.User.objects.get(pk=chat.id)
        name = "%s %s" % (user.name, user.surname)
        last = "%s %s %i %s:%s" % (
            get_date(chat.lastRequest.day), get_date(chat.lastRequest.month), chat.lastRequest.year,
            get_date(chat.lastRequest.hour), get_date(chat.lastRequest.minute)
        )

        users.append({
            'num': i,
            'name': name,
            'id': user.pk,
            'req': chat.requests,
            'last': last
        })

    return users
