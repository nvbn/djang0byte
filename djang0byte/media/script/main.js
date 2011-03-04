var meons = Array();
var post_type = Array();
var current_reply = -1;
var comment_text = '';
var fast_panel_type = 'all';
var fast_panel_cache = Array();
var fast_list_type = 'list';

function createFast(type, where) {
    $('#fast_' + type).click(function(){
       if (fast_panel_type == type) {
           if (where == "#fast_list_area")
            fast_panel_type = 'list'
           else
            fast_panel_type = 'all';
           $(where).html(fast_panel_cache[fast_panel_type]);
       } else {
           fast_panel_type = type;
           if (fast_panel_cache[fast_panel_type]) {
               $(where).html(fast_panel_cache[fast_panel_type]);
           } else {
                $.ajax({ url: "/action/get_val/" + type + "/", context: document.body, success: function(data, textStatus, XMLHttpRequest) {
                    result = '<ul>';

                    for (i in data) {
                        element = data[i];
                        result = result + '<li class="' + element.type + '"><a href="' + element.url + '">' + element.title + '</a></li>'
                    }
                    result += '</ul>';
                    fast_panel_cache[fast_panel_type] = result;
                    $(where).html(fast_panel_cache[fast_panel_type]);
                }});
           }
       }
    });
}

function initFastPanel() {
    fast_panel_cache[fast_panel_type] = $('#fast_panel_area').html();
    fast_panel_cache[fast_list_type] = $('#fast_list_area').html();
    createFast('posts', '#fast_panel_area');
    createFast('comments', '#fast_panel_area');
    createFast('spies', '#fast_panel_area');
    createFast('favourites', '#fast_panel_area');
    createFast('drafts', '#fast_panel_area');
    createFast('users', '#fast_list_area');
    createFast('blogs', '#fast_list_area');
}

function clearCommentForms(store) {
    if ($("#comment_preview")) {
        $("#comment_preview").remove();
    }
    if (!store) comment_text = '';
    $(".comment_reply_form>form").each(function(){
        if (store && $(this).find('textarea').val()) {
            comment_text = $(this).find('textarea').val();
        }
        $(this).find('textarea').val('');
    });
}

function initCommentPreview(where) {
    where.find('.preview_comment_button').click(function(){
        $("#comment_preview").remove();
        $('<div id="comment_preview"></div>').insertBefore($(this).parent().find('textarea'));
        $.ajax({ url: "/action/preview_comment/", type: 'POST', data: {'text':  $(this).parent().find('textarea').val()}, context: document.body, success: function(data, textStatus, XMLHttpRequest) {
                $('#comment_preview').html(data.text);
        }});
    });
}

function addMeOn() {
    //Add meon input to edit user page
    count = $('#meon_count').val();
    app = $('<p>').attr('id','meonp_'+count);
    input = $('<input>').attr('class', 'meon').attr('type', 'text').attr('value', 'title').attr('name', 'meon[' + count + ']');
    app.append(input);
    input = $('<input>').attr('class', 'meon').attr('type', 'text').attr('value', 'url').attr('name', 'meon_url[' + count + ']');
    app.append(input);
    app.append('<a href="#" id="'+count+'" class="rm_meon">X</a>');
    $('#'+count).bind('click',function(){
          rmMeOn(parseInt($(this).attr('id')));
    });
    $('#meon_area').append(app);
    $('#meon_count').val(parseInt(count) + 1);
}

function rmMeOn(number) {
    //Remove meon input from edit user page
    //number -- element number, if -1 -- delete last
    count = $('#meon_count').val();
    if (number > 0) {
        number = count - 1;
    }
    if (number < 0) return(-1);
    $('#meon_count').val(parseInt(count) - 1);
    $("#meon_area>p#meonp_"+number).remove();
}

function addAnsw() {
    //Add input to creating answer form
    count = $('#count').val();
    app = $('<p>').attr('id','answp_'+count);
    input = $('<input>').attr('type', 'text').attr('name', '' + count + '');
    app.append(input);
    app.append('<a href="#" id="'+count+'" class="rm_answ">X</a>');
    $('#'+count).bind('click',function(){
          rmAnsw(parseInt($(this).attr('id')));
    });
    $('#answ_area').append(app);
    $('#count').val(parseInt(count) + 1);
}

function rmAnsw(number) {
    //Remove input from creating answer form
    //number -- element number, if -1 -- delete last
    count = $('#count').val();
    if (number = -1) {
        number = count - 1;
    }
    if (number < 0) return(-1);
    $('#count').val(parseInt(count) - 1);
    $("#answ_area>p#answp_"+number).remove();
}

function initPostType() {
    $("#post_type>a").each(function(){
        lnk = $(this).attr('href');
        lnk = lnk.replace('?type=', '');
        $(this).attr('href', '#' + lnk);
        $(this).click(function(){
            setPostType($(this).attr('href').split('#')[1]);
        });
    });
}

function initAnswers() {
    $(".rm_answ").each(function(){
       $(this).click(function(){
          rmAnsw(parseInt($(this).attr('id')));
       });
    });
    $("#add_answ").click(function(){
           addAnsw();
    });
    $("#rm_answ").click(function(){
            rmAnsw(-1);
    });
}

function initCommentSubmit(context) {
    if (context == -1) {
        context = ".comment_reply_form>form";
    } else {
        context = context + ">.comment_reply_form>form";
    }
    $(context).submit(function(event){
        $('input[type=submit]', this).attr('disabled', 'disabled');
        event.preventDefault();
        $.ajax({ url: "/newcomment/?json=1", type: 'POST', data: $(this).serialize(),
            context: document.body, success: function(data, textStatus, XMLHttpRequest) {
 
       
            updateComments(data, 1);

            clearCommentForms(false);
            commentReplyForm(-1);
            $('input[type=submit]', this).attr('disabled', '');
        }});
        return false;
    });
}

function updateComments(data, write) {
    if (!write)
            $(".new_comment").each(function(){
                $(this).removeClass('new_comment');
            });
    if (data.count > 0) {
        for (i in data.comments) {
            if (!$("#cmnt" + data.comments[i].id).length){
                if (data.comments[i].placeholder == 0) {
                    $(data.comments[i].content).insertBefore('#main_form');
                } else {
                    $(data.comments[i].content).insertAfter('#cmnt'+data.comments[i].placeholder);
                }
                $(data.comments[i].content).each(function() {
                    initCommentReply('#' + $(this).attr('id'));
                    initCommentRates('#' + $(this).attr('id'));
                });

            } else data.count--;

        }
        if ($("#updated_count").html() == '—' || !write) {
            $("#updated_count").html(data.count);

        }
        else if (parseInt($("#updated_count").html()) > 0 && write)
            $("#updated_count").html(parseInt($("#updated_count").html()) + data.count);

        if (!write || data.count > 1)
                $.jGrowl(data.count + " новых комментариев!");
    } else {
        $("#updated_count").html('—');
        $.jGrowl("Новых комментариев нет!");
    }
    $('#updated_count').attr('href', "#" + $(".new_comment:first").parent().attr('id'));
}

function _get(val, select) {
        try {
            if (select) {
                post_type[val] = $('select[name=' + val + ']').val();
            } else {
                post_type[val] = $('input[name=' + val + ']').val();
            }
        } catch (err) {}
    }
    function _set(val, select) {
        try {
             if (select) {
                 $('select[name=' + val + ']').val(post_type[val]);
             } else {
                 $('input[name=' + val + ']').val(post_type[val]);
             }
        } catch (err) {}
    }
    function set(val) {_set(val, false);}
    function get(val) {_get(val, false);}

function setPostType(type) {

    _get('blog', true);
    get('title');
    get('text');
    get('tags');
    get('link');
    get('addition');
    if (type == '?') type = 'post';
    $.ajax({ url: "/newpost/?type=" + type + "&json=1", context: document.body, success: function(data, textStatus, XMLHttpRequest){
        data = eval('(' + data + ')');
        $('#content').html(data.content);
        initPostType();
        initAnswers();
        _set('blog', true);
        set('title');
        set('text');
        set('tags');
        set('link');
        set('addition');
    }});
}

function commentReplyForm(url) {
    clearCommentForms(true);
    $('.comment_reply_form').each(function() {
        $(this).css('display', 'none');
    });
    $('.comment_reply').each(function() {
        $(this).css('display', 'inline');
    });
    if (url != -1) {
        id = url.split('/')[3];
        current_reply = id;
        $('#main_form_hide').css("display", 'inline');
        $('#cmnt' + id + '>a.comment_reply').css('display', 'none');
        if ($('#comment_reply_form_' + id).length) {
            $('#comment_reply_form_' + id).css('display', 'block');
            $('#comment_reply_form_' + id).find('textarea').val(comment_text);
            document.location.hash = 'cmnt' + id;
            return(0);
        }
        $.ajax({ url: url + "?json=1", context: document.body, success: function(data, textStatus, XMLHttpRequest) {
            data = eval('(' + data + ')');
            id = url.split('/')[3];
            form = $('<div>').attr('class', 'comment_reply_form').attr('id', 'comment_reply_form_' + id).append(data.content);
            form.find('textarea').val(comment_text);
            initCommentPreview(form);
            $('#cmnt' + id).append(form);
            document.location.hash = 'cmnt' + id;
            initCommentSubmit('#cmnt' + id);
        }});
    } else {
        $('#main_form_hide').css("display", 'none');
        $('#main_form').css('display', 'block');
        $('#main_form').find('textarea').val(comment_text);
        current_reply = -1;
    }
}

function initCommentReply(context) {
    if (context == -1) {
        context = ".comment_reply";
    } else {
        context = context + ">.comment_reply";   
    }
    $(context).each(function(){
        lnk = $(this).attr('href')
        $(this).attr('href', '#' + lnk);
        $(this).click(function(){
            commentReplyForm($(this).attr('href').split('#')[1]);
        });
    });
}

function rate(url, type) {
    $.ajax({ url: url + "?json=1", context: document.body, success: function(data, textStatus, XMLHttpRequest) {
            //data = eval('(' + data + ')');
            //alert(data.error);
            if (data.error != '') {
                $.jGrowl(data.error);
            } else {
                if (parseInt(data.rate) > 0) {
                    class = 'plus_rate';
                } else if (parseInt(data.rate) < 0) {
                    class = 'minus_rate';
                } else {
                    class = '';
                }
                if (type == 'comment') {
                    hash = '#cmnt' + data.id + '>div.comment_top>div.comment_rate>span';
                } else if (type == 'post') {
                    hash = '#prate' + data.id + '>span';
                }
                $(hash).html(data.rate).attr('class', class);
            }
    }});
}


function initCommentRates(context) {
    if (context == -1) {
        context = ".comment_rate";
    } else {
        context = context + ">.comment_rate";
    }
    $(context + ">a").each(function(){
        $(this).attr('href', '#' + $(this).attr('href'));
        $(this).click(function(){
            rate($(this).attr('href').split('#')[1], 'comment');
        });
    });
}

function initPostRates(context) {
    if (context == -1) {
        context = ".post_rate";
    } else {
        context = context + ">.post_rate";
    }
    $(context + ">a").each(function(){
        $(this).attr('href', '#' + $(this).attr('href'));
        $(this).click(function(){
            rate($(this).attr('href').split('#')[1], 'post');
        });
    });
}

$(document).ready(function(){
    $("#add").click(function(){
           addMeOn();
    });
    $("#rm").click(function(){
            rmMeOn(-1);
    });
    $(".rm_meon").each(function(){
       $(this).click(function(){
          rmMeOn(parseInt($(this).attr('id'))); 
       });
    });
    $('#main_form_hide').click(function(){
        commentReplyForm(-1);
    })
    $('.comment_reply_form').each(function(){
       initCommentPreview($(this));
    });
    $('#new_post_form').submit(function(){
        $('input[type=submit]', this).attr('disabled', 'disabled');
    });
    $('#update_button').click(function(){
        $.ajax({ url: "/action/get_last_comments/" + document.location.href.split('/')[4] + '/', context: document.body, success: function(data, textStatus, XMLHttpRequest) {
            updateComments(data);
        }});
    });
    $('#updated_count').click(function(){
        $('#updated_count').attr('href', "#" + $(".new_comment:first").parent().attr('id'));
        $(".new_comment:first").removeClass('new_comment');
        cnt = parseInt($('#updated_count').html()) - 1
        if (cnt)
            $('#updated_count').html(cnt);
        else
            $('#updated_count').html('—');
    });
    if ($(".new_comment").length){
        $('#updated_count').html($(".new_comment").length);
    }
    initPostType();
    initAnswers();
    initCommentSubmit(-1);
    initCommentReply(-1);
    initCommentRates(-1);
    initPostRates(-1);
    initFastPanel();
});