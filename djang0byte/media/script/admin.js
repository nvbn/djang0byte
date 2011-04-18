function initModal(id) {
    $(id).click(function(event){
         event.preventDefault();
         $.ajax({ url:$(this).attr('href')+'?json=1', context: document.body, success: function(data, textStatus, XMLHttpRequest) {
             data = eval('(' + data + ')');
             $.modal(data.content, {
               overlayClose:true,
               opacity: 80,
               minHeight:100,
	           minWidth: 200
             });
        $('#login_cancel').css('display', 'inline');
        }});
        return false;
    });
}
$(document).ready(function(){
    initModal('#post_options');
    initModal('#delete_post');
});