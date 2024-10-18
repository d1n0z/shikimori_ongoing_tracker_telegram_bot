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


dbhandle.create_tables(Model.__subclasses__())
