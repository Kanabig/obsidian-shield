console.log(maps);
// 1. 지도를 띄울 중심좌표와 확대 레벨
const centerlat = maps[0].latitude;
const centerlng = maps[0].longitude;


var options = {
        center: new kakao.maps.LatLng(centerlat, centerlng),
        level: 3
};

//2. HTML에서 지도를 담을 컨테이너(div)를 가져와 실제 지도 객체 생성
var container = document.getElementById("map");
var map = new kakao.maps.Map(container, options);


//3. 마커 객체 생성
maps.forEach(function(target){
        const marker = new kakao.maps.Marker({
                map: map,
                position: new kakao.maps.LatLng(
                        target.latitude,
                        target.longitude
                )
        });


        //4. Infowindow 내용
        const content = `
        
        <div class = "info-window">
            <img src="/static/images/${target.images}">
            <h3>${target.name}</h3>
            <p>나이: ${target.age}</p>
            <p>${target.short_description}</p>
            <p>탐지시간: ${target.reg_date}</p>
        </div>
        
        `;
        
        //5. InfoWindow 생성
        const infoWindow = new kakao.maps.InfoWindow({
                content: content
        });
        //6. 마커 클릭시 열기
        kakao.maps.event.addListener(marker, 'click', function() {
                infoWindow.open(map, marker);
        });
});

        

