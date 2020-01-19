import peewee
import pymysql
from peewee import *

db = MySQLDatabase('spider',
                   host="127.0.0.1",
                   user="root",
                   password="123456",
                   port=3306,
                   charset="utf8mb4"
                   )


class BaseModel(Model):
    class Meta:
        database = db


class Topic(BaseModel):
    title = CharField()  # 题目
    content = TextField(default="")  # 内容
    id = IntegerField(primary_key=True)  # ID
    author = CharField()  # 作者
    creat_time = DateTimeField()  # 创建时间
    answer_num = IntegerField(default=0)  # 回复数
    click_num = IntegerField(default=0)  # 点击数
    parise_num = IntegerField(default=0)  # 点赞数
    jtl = FloatField(default=0.0)  # 结贴率
    score = IntegerField(default=0)  # 赏分
    status = CharField()  # 状态
    last_time = DateTimeField()  # 最后回复时间


class Answer(BaseModel):
    topic_id = IntegerField()
    author = CharField()
    content = TextField(default="")
    creat_time = DateTimeField()
    parise_num = IntegerField(default=0)


class Author(BaseModel):
    name = CharField(max_length=30)
    id = CharField(primary_key=True)
    desc = TextField(null=True)
    follower_num = IntegerField(default=0)  # 粉丝数
    following_num = IntegerField(default=0)  # 关注数


if __name__ == "__main__":
    # 建表
    db.create_tables([Topic, Author, Answer])
