from tortoise import fields, Tortoise
from tortoise.models import Model


class GuildConfig(Model):
    id = fields.BigIntField(pk=True)
    mod_log = fields.BigIntField(null=True)
    join_log = fields.BigIntField(null=True)
    theme_color = fields.IntField(min_value=0, max_value=0xffffff, null=True)
    welcome_title = fields.CharField(max_length=100, null=True)
    welcome_description = fields.CharField(max_length=200, null=True)
    welcome_image = fields.CharField(max_length=100, null=True)
    welcome_footer = fields.CharField(max_length=100, null=True)
