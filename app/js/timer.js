function startTimer() {
  var beginTime = new Date();
  var center = 100,
      backColor = "rgba(250,250,250,.4)",
      alpha = 0.9,
      backgroundCheck = false,
      canvas = document.getElementById("myCanvas"),
      ctx = canvas.getContext("2d"),
      shadow = {
        color:"rgba(35,242,250,1)",
        offsetX:0,
        offsetY:0,
        blur:1
      },
      secSetup = {
        radie:66,
        lineWidth:65,
        back:66,
        color:"rgba(250,250,250," + alpha + ")",
        counter:0,
        old:0,
        limit:15 //number of seconds to wait
      },
      check = function(diff, count, setup, ctx) {
        if (count < setup.old){
          setup.counter++
        }
        if(setup.counter % 2 === 0){
          draw(setup.radie, setup.color, setup.lineWidth, 0, count, ctx);
        } else{
          draw(setup.radie, setup.color, setup.lineWidth, count, 0, ctx);
        }
      },
      draw = function(radie, color, lineWidth, firstCount, secondCount, ctx) {
        ctx.beginPath();
        ctx.arc(center, center, radie, firstCount * Math.PI, secondCount * Math.PI, false);
        ctx.lineWidth = lineWidth;
        ctx.shadowColor = shadow.color;
        ctx.shadowOffsetX = shadow.offsetX;
        ctx.shadowOffsetY = shadow.offsetY;
        ctx.shadowBlur = shadow.blur;
        ctx.strokeStyle = color;
        ctx.stroke();
      },
      background = function() {
        draw(secSetup.radie, backColor, secSetup.back, 0, 2, ctx);
        draw(secSetup.radie, backColor, secSetup.lineWidth, 0, 2, ctx);
      };

  $("body").click(function() {
    backgroundCheck = !backgroundCheck;
  });

  window.updateSeconds = function() {
        canvas.width = canvas.width;
        background();
        var d = new Date(),
            diff = d.getTime() - beginTime.getTime(),
            diffSec = diff/1000;
            secCount = (Math.abs(diffSec)/30)%2;
        if (diffSec >= secSetup.limit) {
            /* disable this for now...
            if ($('.writeronebox').val() == '') {
                alert('Need more time?');
                beginTime = new Date()
                drawTime = setInterval('updateSeconds()', 200)
            }
            else {
                $('#snacktext').submit();
            }*/
            clearInterval(drawTime);
            $('#snacktext').submit();
        }
        check(diff, secCount, secSetup, ctx);
        secSetup.old = secCount - 0.01;
  };
  var drawTime = setInterval('updateSeconds()', 200);
}
