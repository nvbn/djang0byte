var meons = Array();
var post_type = Array();
var current_reply = -1;

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
    if (number = -1) {
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
        event.preventDefault();
        $.ajax({ url: "/newcomment/?json=1", type: 'POST', data: $(this).serialize(),
            context: document.body, success: function(data, textStatus, XMLHttpRequest) {
            data = eval('(' + data + ')');
            if (current_reply == -1) {
                $(data.content).insertBefore('#main_form');
            } else {
                $(data.content).insertAfter('#cmnt'+current_reply);
            }
            $(data.content).each(function() {
                initCommentReply('#' + $(this).attr('id'));
            });
            commentReplyForm(-1);
        }});
        return false;
    });
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
    get('source');
    if (type == '?') type = 'post';
    $.ajax({ url: "newpost/?type=" + type + "&json=1", context: document.body, success: function(data, textStatus, XMLHttpRequest){
        data = eval('(' + data + ')');
        $('#content').html(data.content);
        initPostType();
        initAnswers();
        _set('blog', true);
        set('title');
        set('text');
        set('tags');
        set('link');
        set('source');
    }});
}

function commentReplyForm(url) {
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
            document.location.hash = 'cmnt' + id;
            return(0);
        }
        $.ajax({ url: url + "?json=1", context: document.body, success: function(data, textStatus, XMLHttpRequest) {
            data = eval('(' + data + ')');
            id = url.split('/')[3];
            form = $('<div>').attr('class', 'comment_reply_form').attr('id', 'comment_reply_form_' + id).append(data.content);
            $('#cmnt' + id).append(form);
            document.location.hash = 'cmnt' + id;
            initCommentSubmit('#cmnt' + id);
        }});
    } else {
        $('#main_form_hide').css("display", 'none');
        $('#main_form').css('display', 'block');
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
    initPostType();
    initAnswers();
    initCommentSubmit(-1);
    initCommentReply(-1);
    initCommentRates(-1);
    initPostRates(-1);
});