const maxRetries = 3;

let selectedPhotos = [];
let currentIndex = 0;
let totalImages = 0;
let retryCount = 0;

const POLL_INTERVAL_MS = 10000;
let pollingTimer = null;

function updateImage(index) {
    const imgTag = document.getElementById('photo');
    const newImageUrl = `/photo/${index}?${new Date().getTime()}`;
    
    imgTag.onerror = function() {
        if (retryCount < maxRetries) {
            retryCount++;
            console.warn(`Failed to load image. Retrying ${retryCount}/${maxRetries}...`);
            setTimeout(() => updateImage(index), 1000);
        } else {
            console.error("Failed to load image after multiple attempts.");
            retryCount = 0;
        }
    };
    
    imgTag.onload = function() {
        retryCount = 0;
    };
    
    imgTag.setAttribute('src', newImageUrl);
}

function showNextImage() {
    currentIndex = (currentIndex + 1) % totalImages;
    updateImage(currentIndex);
}

function showPreviousImage() {
    currentIndex = (currentIndex - 1 + totalImages) % totalImages;
    updateImage(currentIndex);
}

function showImage(){
    // 새 탭에서 현재 이미지를 열기 (저장 목적)
    window.open(`/photo/${currentIndex}`, '_blank');
}

function pollImageList() {
    fetch('/api/images')
        .then(response => response.json())
        .then(data => {
            const newPhotos = data.images;

            const changed =
                newPhotos.length !== selectedPhotos.length ||
                newPhotos.some((path, i) => path !== selectedPhotos[i]);

            if (changed) {
                console.log('A change has been detected in the image list. Reloading images.');
                selectedPhotos = newPhotos;
                totalImages = selectedPhotos.length;
                if(currentIndex >= totalImages){
                    currentIndex = 0;
                }
                updateImage(currentIndex);
            }
        })
        .catch(error => console.error('Polling error: ', error));
}


function fetchImageList() {
    fetch('/api/images')
        .then(response => response.json())
        .then(data => {
            selectedPhotos = data.images;
            totalImages = selectedPhotos.length;
            if (totalImages > 0) {
                updateImage(currentIndex);
                pollingTimer = setInterval(pollImageList, POLL_INTERVAL_MS); 
            }
        })
        .catch(error => console.error('Error fetching image list:', error));
}

document.getElementById('changeButton').addEventListener('click', showNextImage);
document.getElementById('prevButton').addEventListener('click', showPreviousImage);
document.getElementById('photo').addEventListener('click', showImage);

fetchImageList();
