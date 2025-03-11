let num = 0;
const imageBaseUrl = 'https://vrcimg.hatsune.app/';
const imageExtension = '.png';
let retryCount = 0;
const maxRetries = 3;

function changepic() {
    num = (num + 1) % 7;
    updateImage(num);
}

function showPreviousImage() {
    num = (num - 1 + 7) % 7;
    updateImage(num);
}

function updateImage(num) {
    const imgTag = document.getElementById('photo');
    const timestamp = new Date().getTime();

    const newImageUrl = num === 6
        ? `${imageBaseUrl}jd${imageExtension}?${timestamp}`
        : `${imageBaseUrl}${num}${imageExtension}?${timestamp}`;

    imgTag.onerror = function() {
        if (retryCount < maxRetries) {
            retryCount++;
            console.warn(`Failed to load image. Retrying ${retryCount}/${maxRetries}...`);
            setTimeout(() => updateImage(num), 1000); // 2초 후에 다시 시도
        } else {
            console.error("Failed to load image after multiple attempts.");
            retryCount = 0; // 재시도 횟수 초기화
        }
    };

    imgTag.onload = function() {
        retryCount = 0; // 성공 시 초기화
    };

    imgTag.setAttribute('src', newImageUrl);
}

document.getElementById('changeButton').addEventListener('click', changepic);
document.getElementById('photo').addEventListener('click', changepic);
document.getElementById('prevButton').addEventListener('click', showPreviousImage);
