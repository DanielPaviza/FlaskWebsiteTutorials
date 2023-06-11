



function ImageClick(container) {

    if(container.classList.contains("open")) {
        CloseAllImages()
    } else {
        container.classList.add("open");
    }
}

function CloseAllImages() {

    let images = document.getElementsByTagName("img");

    for(i = 0; i < images.length; i++) {
        console.log(images[i].parentElement)
        images[i].parentElement.classList.remove("open");
    }
}