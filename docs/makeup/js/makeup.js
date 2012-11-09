$(function(){
    $('.fast-panel').each(function(index, item){
        var $item = $(item);
        $item.find('.fast-panel-buttons').css('height', $item.find('.fast-panel-content').height() - 10 + 'px');
        console.log($item);
    });
});
