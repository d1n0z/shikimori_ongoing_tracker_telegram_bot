from peewee import SqliteDatabase, Model, IntegerField, TextField, BigIntegerField

from config import DATABASE

dbhandle = SqliteDatabase(DATABASE)


class Track(Model):
    shikiid = IntegerField(index=True, unique=True)
    nextep = BigIntegerField(null=True)
    name = TextField(null=True)
    photo = TextField(null=True)

    class Meta:
        database = dbhandle
        table_name = 'track'


class NotUpdatedTrack(Model):
    shikiid = IntegerField(index=True, unique=True)
    nextupdate = BigIntegerField(null=True)

    class Meta:
        database = dbhandle
        table_name = 'notupdatedtrack'


class UsersTrack(Model):
    shikiid = IntegerField()
    uid = IntegerField()

    class Meta:
        database = dbhandle
        table_name = 'userstrack'


class UsersTimezone(Model):
    uid = IntegerField()
    timezone = TextField(default='Europe/Moscow')

    class Meta:
        database = dbhandle
        table_name = 'userstimezone'


class UsersShikimoriTokens(Model):
    uid = IntegerField()
    access = TextField(null=True)
    refresh = TextField(null=True)
    expires_at = BigIntegerField(null=True)

    class Meta:
        database = dbhandle
        table_name = 'usersshikimoritokens'


dbhandle.create_tables(Model.__subclasses__())
