

// const para = document.createElement("p");
// const node = document.createTextNode("This is Twitch insight");
// para.appendChild(node);

window.addEventListener ("load", myMain, false);

function myMain (evt) {
    let channel_name = window.location.toString().split(".tv/")[1];
    console.log(channel_name)
    // let element = document.getElementsByClassName("CoreText-sc-1txzju1-0 ScTitleText-sc-d9mj2s-0 bthLuv iaMqYH InjectLayout-sc-1i43xsx-0 kuBPOn tw-title");
    // console.log(element);
    // element.innerHTML = "I am the title now!!!!";
    let mainRoot = document.getElementById("root");
    let mainDiv = mainRoot.firstChild;



    let insight = document.createElement("div");
    // insight.innerHTML = "Chat status: &#129395;";
    insight.style.position = "absolute";
    insight.style.color = "white";
    insight.style.top = "60px";
    insight.style.padding = "10px";
    insight.style.borderRadius = "10px";
    insight.style.border = "2px white solid";
    insight.style.borderRadius = "10px";
    insight.style.borderRadius = "10px";

    insight.style.left = "965px";
    insight.style.zIndex = "2000";
    insight.style.fontSize = "25px";
    insight.style.background = "rgba(0, 0, 0, 0.6)";

    mainDiv.appendChild(insight);

    
    setInterval(function() {
        let xhr = new XMLHttpRequest();
        xhr.open("GET", " http://127.0.0.1:5000");
        xhr.send();
        xhr.responseType = "json";
        xhr.onload = () => {
            if (xhr.readyState == 4 && xhr.status == 200) {
              const sentiment_data = xhr.response;
              console.log(sentiment_data);
              switch(sentiment_data.sentiment)
              {
                case 'neutral':
                    insight.innerHTML = "Chat status: &#128578;";
                    break;
                case 'positive':
                    insight.innerHTML = "Chat status: &#129395;";
                    break;
                case 'negative':
                    insight.innerHTML = "Chat status: &#128545;";
                    break;
                default:
                    insight.innerHTML = "Chat status: &#128578;";
              }
            } else {
              console.log(`Error: ${xhr.status}`);
            }
          };
    }, 1000);
}



