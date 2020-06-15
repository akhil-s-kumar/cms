import graphene
from .models import *
from graphql_jwt.decorators import login_required
from framework.api.user import UserBasicObj


class TagObj(graphene.ObjectType):
    name = graphene.String()
    author = graphene.Field(UserBasicObj)

    def resolve_name(self, info):
        return self['name']

    def resolve_author(self, info):
        return User.objects.values().get(id=self['member_id'])


class NewsObj(graphene.ObjectType):
    title = graphene.String(required=True)
    slug = graphene.String(required=True)
    author = graphene.String(required=True)
    date = graphene.Date(required=True)
    categories = graphene.String(required=True)
    tags = graphene.List(TagObj)
    description = graphene.String(required=True)

    def resolve_title(self, info):
        return self['title']

    def resolve_slug(self, info):
        return self['slug']

    def resolve_author(self, info):
        return self['author']

    def resolve_date(self, info):
        return self['date']

    def resolve_categories(self, info):
        return self['categories']

    @graphene.resolve_only_args
    def resolve_tags(self):
        return self.tags.all()


class Query(graphene.ObjectType):
    news = graphene.List(NewsObj)
    @login_required
    def resolve_news(self, info):
        return News.objects.values().all()


schema = graphene.Schema(query=Query)
