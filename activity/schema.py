import graphene
from .models import *
from django.contrib.auth.models import User
from datetime import date, datetime
from django.conf import settings
from graphql_jwt.decorators import login_required
from graphene_django import DjangoObjectType

class TagType(DjangoObjectType):
    class Meta:
        model = Tags
class NewsObj(graphene.ObjectType):
    title = graphene.String(required=True)
    slug = graphene.String(required=True)
    author = graphene.String(required=True)
    date = graphene.Date(required=True)
    categories = graphene.String(required=True)
    tag_list = graphene.List(TagType)
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
    def resolve_tag_list(self):
        return self.tags.all()

class Query(graphene.ObjectType):
    news = graphene.List(NewsObj)
    @login_required
    def resolve_news(self, info, **kwargs):
        return News.objects.values().all()

schema = graphene.Schema(query=Query)
