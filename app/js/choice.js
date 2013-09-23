
$(function ()
{
    $("#logo").mouseenter(function () {
        $(this).animate({width:'+=1%',
                         height:'+=1%'}, 'medium')
    }).mouseleave(function ()
    {
        $(this).animate({width:'-=1%',
                         height:'+=1%'}, 'medium')
    });
});

$(function ()
{
    $(".pushme").mouseenter(function () {
        $(this).animate({top:'+=2%'}, 'fast')
    }).mouseleave(function ()
    {
        $(this).animate({top:'-=2%'}, 'fast')
    });
});
