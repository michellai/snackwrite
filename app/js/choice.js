

$(function ()
{
    $(".pushme").mouseenter(function () {
        $(this).animate({top:'+=2%'}, 'fast')
    }).mouseleave(function ()
    {
        $(this).animate({top:'-=2%'}, 'fast')
    });
});
