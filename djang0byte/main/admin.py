# -*- coding: utf-8 -*-
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.



from django.contrib import admin
import models
from django.utils.translation import gettext as _
from main.models import Post, Blog, Profile, Comment, Answer, AnswerVote, UserInBlog,\
    Notify, BlogType, TextPage, MeOn, Statused, Favourite

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username']

class PostAdmin(admin.ModelAdmin):
    search_fields = ['__unicode__']
    list_display = ('title', 'blog', 'author', 'rate', 'favourite_count')

    def favourite_count(self, obj):
        return models.Favourite.objects.filter(post=obj).count()

    favourite_count.admin_order_field = 'fav_count'
    favourite_count.short_description = _('favourite count')

    def queryset(self, request):
        qs = super(PostAdmin, self).queryset(request)
        qs = qs.extra(
            select = {
                'fav_count': """
                    SELECT COUNT(main_favourite.id) AS fav_count
                    FROM main_favourite
                    WHERE main_favourite.post_id = main_post.draft_ptr_id
                """
            }
        )
        return qs


for stuff in ('UserInBlog', 'Notify', 'TextPage', 'MeOn', 'Statused', 'Blog',
               'Comment', 'Answer', 'AnswerVote', 'BlogType', 'Draft', 'Blocks'):
    admin.site.register(getattr(models, stuff))

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post, PostAdmin)
