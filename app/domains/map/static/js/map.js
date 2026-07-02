// console.log(maps);
// 1. 지도를 띄울 중심좌표
const centerlat = maps[0].latitude;
const centerlng = maps[0].longitude;

//2. 지도 확대 레벨- n-1번 확대된다.
const options = {
        center: new kakao.maps.LatLng(centerlat, centerlng),
        level: 4
};

//3. HTML에서 지도를 담을 컨테이너(div)를 가져와 실제 지도 객체 생성
var container = document.getElementById("map");
var map = new kakao.maps.Map(container, options);




//4. 마커 객체 생성
let openedInfoWindow = null;

maps.forEach(function(target){
        
        // MarkerImage 생성
        const imageSrc = `${imageBaseUrl}${target.image}`;
        
        const imageSize = new kakao.maps.Size(60, 60);
        
        const markerImage = new kakao.maps.MarkerImage(
                imageSrc,
                imageSize
        );

        const marker = new kakao.maps.Marker({
                map: map,
                position: new kakao.maps.LatLng(
                        target.latitude,
                        target.longitude
                ),
                image: markerImage
        });


        //6. Infowindow 내용
        const content = `
        
        <div class = "info-window">
            <img src="${imageBaseUrl}${target.image}">
            <h3>${target.name}</h3>
            <p>나이: ${target.age}</p>
            <p>${target.short_description}</p>
            <p>탐지시간: ${target.reg_date}</p>
        </div>
        
        `;
        
        //7. InfoWindow 생성
        const infoWindow = new kakao.maps.InfoWindow({
                content: content
        });
        //8. 마커 클릭시 열고닫기
        kakao.maps.event.addListener(marker, 'click', function() {
                
                // 이미 해당 마커의 InfoWindow가 열려있다면 닫기
                if(openedInfoWindow === infoWindow){
                        infoWindow.close();
                        openedInfoWindow = null;
                        return;
                }
                // 다른 InfoWindow가 열려있다면 닫기
                if (openedInfoWindow) {
                    openedInfoWindow.close();
                }
                // 현재 InfoWindow 열기
                infoWindow.open(map, marker);
                openedInfoWindow = infoWindow;
        });
});

        

