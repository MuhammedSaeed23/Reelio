const faqItems = document.querySelectorAll(".faq-item");

faqItems.forEach(item => {
    item.addEventListener("click", () => {

        faqItems.forEach(faq => {
            if (faq !== item) {
                faq.classList.remove("open");
            }
        });

        item.classList.toggle("open");

    });
});
// button click function 
const link=document.querySelector(".download")
const urls=document.querySelector("input")
link.addEventListener("click",()=>{
  reset()
  const url=urls.value;
  if (!instalinkcheck(url)) {
    showError("Please enter a valid Instagram Reel URL.");
    return;

}  
const move=document.querySelector(".r-time")
move.scrollIntoView({
    behavior:"smooth"
    })

  fetchurl(url)
  console.log(url)
});
// fetch function 
let uid=null
function fetchurl(link){
    const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
    fetch("/download/",{
        method:"POST",
        headers:{
         "Content-Type":"application/json",
         "X-CSRFToken":csrf,
        },
    body:JSON.stringify({

     url:link,
     old_uid:localStorage.getItem("uid")

     }),

    })
    .then((response) => response.json())
        .then((result) => {
            console.log(result);
             uid=result.video_id
             localStorage.setItem("uid",uid)
             progressing()

        })
        .catch((error) => {
    console.error("Download error:", error);
});
}
const down_btn=document.querySelector(".down")
down_btn.addEventListener("click", async () => {
    const response = await fetch(`/Get_vedio/${uid}/`);
    console.log(response.status);
console.log(response.headers.get("content-type"));
    const blob = await response.blob();

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "video.mp4";
    link.click();

    URL.revokeObjectURL(link.href);
});

function processing(thumbnail,user_name,caption){
    const loader=document.querySelector(".rotate")
    const thumb=document.querySelector(".highlight")
    if(thumbnail){
    loader.style.display="none"
    thumb.style.display="flex"    
    thumb.src=thumbnail
    }
    const creator=document.querySelector(".video-title")
    if(user_name){
    creator.innerText=user_name
    }
    const capt=document.querySelector(".creator")
    if(caption){
    capt.innerText=caption
    }
}
async function checkVideoStatus(uid) {

    const response = await fetch(`/status/${uid}/`);
    const data = await response.json();
        const ready=document.querySelector(".v-download")
        setTimeout(()=>{
        ready.scrollIntoView({
          behavior:"smooth"
        })
        },2000)
    if (data.status != "ready") {

        setTimeout(() => {
            checkVideoStatus(uid);
        }, 2000);

        return;
    }

    console.log("Video ready");
    const pla = document.querySelector(".pla");
    pla.style.display="none"
    const load = document.querySelector(".load");
    load.style.display="none"
    const preview = document.querySelector(".player");
    preview.style.display="flex"
    preview.src = `/preview/${uid}/`;
    preview.load();
    

    console.log("🎥 Preview URL:", preview.src);
    const down_btn=document.querySelector(".down")
    down_btn.disabled=false
    await meta_data()
}
    
const copybtn=document.querySelector(".copy")
copybtn.addEventListener("click",async()=>{
    const preview = document.querySelector(".player");
    await navigator.clipboard.writeText(preview.src)
    copybtn.textContent="Copied!"
    setTimeout(()=>{
        copybtn.textContent="Copy link"
    },1500)


})
function progressing(){
    fetch(`/progress/${uid}`)
        .then(response=>response.json())
         .then(data=>{
            if(data.error){
                console.log("Error:", data.error);
                document.querySelector(".rotate").style.display = "none";
                document.querySelector(".highlight").style.display = "none";
                document.querySelector(".error").style.display = "flex";

                document.querySelector(".video-title").textContent = "Unable to process reel";
                
                document.querySelector(".video-title").style.color = "#f35b1f";

                document.querySelector(".creator").textContent = data.error;
                document.querySelector(".creator").style.color = "#ee1515";

                document.querySelector(".meta").style.display = "none";

                return
            }
            console.log(data)
            sta=data.status
            
            percent=data.percent
            thumbnail=data.thumbnail
            user_name=data.user_name
            caption=data.caption

            loading_bar(sta,percent)
            processing(thumbnail,user_name,caption)

            if(sta === "complete"){
               checkVideoStatus(uid);

            }
            else{
            setTimeout(progressing, 500);
            }
        
         })
}
const boxes = document.querySelectorAll(".box")
const observer= new IntersectionObserver((entries)=>{
    entries.forEach((entries)=>{
        if (entries.isIntersecting){
            entries.target.classList.add("showing")
        }
        else{
            entries.target.classList.remove("showing")
        }
    })
})
boxes.forEach((box)=>{
    observer.observe(box);
})
function loading_bar(status,percent){
    const bar=document.querySelector(".progress-fill")
    const tags=document.querySelectorAll(".comp")
    const remain=document.querySelector(".percentage")
    remain.innerText=percent+"%"
    bar.style.width=percent+"%";
// sab se reset
    tags.forEach(tag => {
        tag.classList.remove("glow");
        tag.classList.remove("focus");
    });

    let currentIndex;

    if (status === "browser") {
        currentIndex = 0;
    }
    else if (status === "page_goto") {
        currentIndex = 1;
    }
    else if (status === "media") {
        currentIndex = 2;
    }
    else if (
        status === "thumbnail" ||
        status === "user_name" ||
        status === "caption" ||
        status === "complete"
    ) {
        currentIndex = 3;
    }

    // current + previous completed
    for (let i = 0; i <= currentIndex; i++) {
        tags[i].classList.add("focus");
    }

    // sirf current par shadow
    tags[currentIndex].classList.add("glow");
}
const faq=document.querySelector(".faq_btn")
faq.addEventListener("click",()=>{
    const faq_session=document.querySelector(".faq")
    faq_session.scrollIntoView({
        behavior:"smooth",
        block:"center"
    })
})
const works=document.querySelector(".works_btn")
works.addEventListener("click",()=>{
    const works_session=document.querySelector(".work")
    works_session.scrollIntoView({
        behavior:"smooth",
        block:"center"
    })
})
const feature=document.querySelector(".feature_btn")
feature.addEventListener("click",()=>{
    const feature_session=document.querySelector(".why")
    feature_session.scrollIntoView({
        behavior:"smooth",
        block:"center"
    })
})
const another=document.querySelector(".another")
another.addEventListener("click",()=>{
    const hero_session=document.querySelector(".hero")
    hero_session.scrollIntoView({
        behavior:"smooth",
        })
})
function instalinkcheck(url){
 try{
    const prased=new URL(url);
    const validhost=prased.hostname==="instagram.com" ||
            prased.hostname === "www.instagram.com";
    const validpath=prased.pathname.startsWith("/reel/")
         return prased.protocol === "https:" &&
               validhost &&
               validpath;
 }
 catch{
    return false;
 }


}
async function meta_data(){
 const response = await fetch(`/metadata/${uid}/`);
    const data = await response.json();
    const stat=data.status
    if( stat !=="ready"){
       setTimeout(()=>{
        meta_data()
       },500)
    }
    console.log("METADATA:", data);
    const length=data.duration
    const resolucte=data.resolution
    const size=data.size
    const minutes = Math.floor(length / 60);
    const seconds = Math.floor(length % 60);
    const formatted = `${minutes}:${seconds.toString().padStart(2, "0")}`;
    const resoluction=document.querySelectorAll(".resolution")
    resoluction.forEach((res)=>{
        res.innerText=resolucte
    })
    const range=document.querySelectorAll(".size")
    range.forEach((res)=>{
        res.innerText=size
    })
    const Duration=document.querySelectorAll(".duration")
    Duration.forEach((res)=>{
        res.innerText=formatted
    })

}
function reset(){
    document.querySelector(".error").style.display = "none";
    const loader=document.querySelector(".rotate")
    const thumb=document.querySelector(".highlight")
    loader.style.display="flex"
    thumb.style.display="none"    
    const creator=document.querySelector(".video-title")
    creator.innerText="Sunset sessions 🌅"
    const capt=document.querySelector(".creator")
    capt.innerText="by vibes.daily"
    const bar=document.querySelector(".progress-fill")
    const remain=document.querySelector(".percentage")
    remain.innerText="0%"
    bar.style.width=0+"%";
    const pla = document.querySelector(".pla");
    pla.style.display="flex"
    const load = document.querySelector(".load");
    load.style.display="flex"
    const preview = document.querySelector(".player");
    preview.style.display="none"

}
let hideTimer;

