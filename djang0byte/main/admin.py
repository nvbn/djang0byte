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
from main.models import Post, Blog, Profile, Comment, Answer, AnswerVote, UserInBlog, Notify, BlogType, TextPage


admin.site.register(Post)
admin.site.register(Blog)
admin.site.register(BlogType)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Answer)
admin.site.register(AnswerVote)
admin.site.register(UserInBlog)
admin.site.register(Notify)
admin.site.register(TextPage)
