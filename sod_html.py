#!/usr/bin/env/python
#
# More of a reference of using jinaj2 without actual template files.
# This is great for a simple output transformation to standard out.
#
# Of course you will need to "sudo pip install jinja2" first!
#
# I like to refer to the following to remember how to use jinja2 :)
# http://jinja.pocoo.org/docs/templates/
#

HTML_HEADER = """
        <div class="w3-bar w3-theme-d1">
          <div class="w3-bar-item w3-hover-blue"> S O D </div>
        </div> 

"""
HTML_FOOTER = """
        <div class="w3-bar w3-theme-d1">
          <div class="w3-bar-item w3-hover-blue w3-right"> Simple Stream Object Dettection </div>
        </div> 

"""

HTML_WAIT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="{{refresh_rate}}">    
   <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css"> 
   <link rel="stylesheet" href="https://www.w3schools.com/lib/w3-theme-indigo.css">     
    <title>Wait</title>
</head>
<body>
  <div  class="w3-theme-l4">
""" + HTML_HEADER  + """  
    <br>
    Wait please.
    <br>
    {{msg}}    
""" + HTML_FOOTER  + """  
</div">
</body>
</html>
"""

HTML_SOD_MAIN = """
<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css"> 
   <link rel="stylesheet" href="https://www.w3schools.com/lib/w3-theme-indigo.css">     
   <title>SOD Main view</title> 
</head>
<body>
  <div  class="w3-theme-l4">
""" + HTML_HEADER  + """  
     {% for frame in frames %}          
          {% if (loop.index+1)%cameras_in_row == 0 %}
          <br>
              <div class = "w3-cell-row w3-padding w3-container" >          
          {% endif %}
                   <div class = "w3-cell w3-padding w3-card  w3-center">   
                      <div class = "w3-row">   
                         
                              <h1  >
                                  {{frame['camera_name']}}
                                  <h5 class = "datetimes">
                                      SOD {{frame['response_datetime']}} / FRAME {{frame['frame_datetime']}}
                                  </h5>
                              </h1>
                          
                      </div>
                      <div class = "w3-row">   
                         <img class='visible_frame' id={{frame['camera_name']}} src="data:image/jpeg;base64, {{frame['frame']}}"></img>
                      </div>
                      <div class = "w3-row">   
                         <a class = "w3-row w3-margin w3-btn w3-theme-l3" href="/set_regions?camera_name={{frame['camera_name']}}"> SET REGIONS FOR THIS CAMERA </a>
                      </div>
                   </div>  
          {% if (loop.index+2)%cameras_in_row == 0 or loop.index == frames|length %}
              </div>          
          {% endif %}
     {% endfor %}

""" + HTML_FOOTER  + """  

  </div>  
</body>
<script>
const visible_frames = document.getElementsByClassName("visible_frame");
const datetimes = document.getElementsByClassName("datetimes");
async function fetchFrame(camera_name) {
  const res = await fetch('/get_frame?camera_name='+camera_name);
  const data = await res.json();
  return data
}

function refreshFrames() {

    for (let i = 0; i < visible_frames.length; i++) {
        fetchFrame(visible_frames[i].id).then(data => {
                  visible_frames[i].src="data:image/jpeg;base64, " + data.frame ;
                  datetimes[i].innerText = "SOD "+data.response_datetime + " / FRAME " + data.frame_datetime;  
                }, console.error);
    }

    setTimeout(refreshFrames, {{refresh_rate*1000}});
}

refreshFrames()

</script>
</html>
"""


SCRIPT_POST = """    
async function postData(url = "", data = {}) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    return await response.json();
}"""


HTML_SET_REGIONS = """
<!DOCTYPE html>
<html>
<head>
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <script src="https://code.jquery.com/jquery-3.5.1.js" integrity="sha256-QWo7LDvxbWT2tbbQ97B53yJnYU3WhH/C8ycbRAkjPDc=" crossorigin="anonymous"></script>
   <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">   
   <link rel="stylesheet" href="https://www.w3schools.com/lib/w3-theme-indigo.css">   
   <title>Set regions</title>
</head>
<body>
   
   <div class="w3-theme-l4">

""" + HTML_HEADER  + """ 

       <div class = "w3-cell-row w3-padding w3-container w3-center" >          
           <div class = "w3-cell w3-padding w3-card w3-center">   
                 <div class = "w3-row">   
                      <h1>
                          {{frame['camera_name']}}
                      </h1>
                 </div>

                 <div class = "w3-row w3-center">   
                      <canvas id="canvas" width="{{size[0]}}" height="{{size[1]}}" style="background: url('data:image/jpeg;base64, {{frame['frame']}}')"></canvas>
                 </div>
                 <div class = "w3-row w3-center">   
                      <div id="output_statistics"></div>
                 </div>
                 <div class = "w3-row">                    
                    <button type="button" class = "w3-row w3-margin w3-btn w3-theme-l3" onclick="store_regions('{{frame['camera_name']}}');">Store regions to config !</button>                        
                    <button type="button" class = "w3-row w3-margin w3-btn w3-theme-l3" onclick="clear_regions('{{frame['camera_name']}}');">Clear all regions in config !</button>
                    <a class = "w3-row w3-margin w3-btn w3-theme-l3" href="/" > RETURN BACK TO MAIN PAGE </a>            
                 </div>
   
           </div>
       </div>

""" + HTML_FOOTER  + """  

   </div>
   
</body>
<script>
""" + SCRIPT_POST + """
        //Canvas
var canvas = document.getElementById('canvas');
var ctx = canvas.getContext('2d');
//Variables
var canvasx = $(canvas).offset().left;
var canvasy = $(canvas).offset().top;
var last_mousex = last_mousey = 0;
var mousex = mousey = 0;
var mousedown = false;
var region_height = region_width = 0;
var regions = {{regions}};
ctx.fillStyle = '{{regions_color}}'

function store_regions(camera_name){
    postData("/set_regions?camera_name="+camera_name, regions)
            .then((response) => {
                alert(response["message"]);
                location.reload();
                draw_regions();
            })
            .catch((error) => {
                alert(response["message"])
            });
};

function clear_regions(camera_name){
    regions = []; 
    store_regions(camera_name);
};


function draw_regions() {
    for (let i = 0; i < regions.length; i++) {
        ctx.fillRect(regions[i]["x"], regions[i]["y"], regions[i]["w"], regions[i]["h"])
    };
};

function show_output_statistics(){
    $('#output_statistics').html("You have defined " + regions.length + " regions.");
}

//Mousedown
$(canvas).on('mousedown', function(e) {
    last_mousex = parseInt(e.clientX-canvasx);
    last_mousey = parseInt(e.clientY-canvasy);
    mousedown = true;
});

//Mouseup
$(canvas).on('mouseup', function(e) {
    mousedown = false;
    regions.push({'x' : last_mousex, 'y': last_mousey, 'w': region_width, 'h': region_height})
    //ctx.clearRect(0, 0, canvas.width, canvas.height);
});

//Mousemove
$(canvas).on('mousemove', function(e) {
    mousex = parseInt(e.clientX-canvasx);
    mousey = parseInt(e.clientY-canvasy);
    if(mousedown) {
        ctx.clearRect(0,0,canvas.width,canvas.height); //clear canvas
        draw_regions();
        ctx.beginPath();
        region_width = mousex-last_mousex;
        region_height = mousey-last_mousey;
        ctx.rect(last_mousex,last_mousey,region_width,region_height);
        //ctx.fillStyle = "#8ED6FF";
        ctx.fillStyle = 'rgba(164, 221, 249, 0.3)'
        ctx.fill();
        ctx.strokeStyle = '#1B9AFF';
        ctx.lineWidth = 1;
        ctx.fillRect(last_mousex, last_mousey, region_width, region_height)
        ctx.stroke();
    }
    show_output_statistics();    
});

// initial drawing
draw_regions();

</script>

</html>
"""