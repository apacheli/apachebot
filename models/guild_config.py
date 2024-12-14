from tortoise import fields, Tortoise
from tortoise.models import Model


class GuildConfig(Model):
    id = fields.BigIntField(pk=True)
    mod_log = fields.BigIntField(null=True)
    join_log = fields.BigIntField(null=True)
    welcome_title = fields.TextField()
    welcome_description = fields.TextField(null=True)
    welcome_image = fields.CharField(max_length=200, null=True)
    welcome_footer = fields.TextField(null=True)
