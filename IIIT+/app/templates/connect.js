var c=document.getElementById("myCanvas");
var ctx= c.getContext("2d");
var x1=-40;
var x2=430;
function draw(){
	ctx.fillStyle = "white";
ctx.fillRect(0, 0, c.width, c.height);
	//ctx.fill(0,0,0);
	//ctx.textSize(35);
	ctx.font = "1vw Arial";
    ctx.fillStyle = "#0095DD";
    ctx.fillText("con" ,x1,200);
    ctx.fillText("nect" ,x2,200);
    if(x2-x1>33){	
		x1+=1.5;
		x2-=1.5;	
	}
}
setInterval(draw,10)
