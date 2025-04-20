from tortoise import fields
from tortoise.models import Model


class GuildTag(Model):
    guild_id = fields.BigIntField()
    name = fields.CharField(max_length=100)
    content = fields.TextField()
    author_id = fields.BigIntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        unique_together = ("guild_id", "name")
