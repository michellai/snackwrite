function setName(person)
{
    var x;

    if (person!=null)
    {
        x = person;
    }
    else {
        x = "writer one"
    }
    $(".writerone").html(x);
    $(".author").val(x);
    $('.writeronebox').attr('contentEditable',true);
    $('.writeronebox').focus();
    $('.writeronebox').show();
    $('.writeronebox').css('background-color', 'white');
    $('.writeronebox').css('padding', '20px');
    $('.author').css('display', 'none');
    $('.submitName').css('display', 'none');
    $('.writeronebox').addClass('text-left');
    $('.submitSnack').show();
}
