// 1. 지도를 띄울 중심좌표와 확대 레벨
const lat = 36.332326;
const lng = 127.434211;


var options = {
        center: new kakao.maps.LatLng(lat, lng),
        level: 3
};

//2. HTML에서 지도를 담을 컨테이너(div)를 가져와 실제 지도 객체 생성
var container = document.getElementById('map');
var map = new kakao.maps.Map(container, options);

//3. HTML에서 지도를 담을 컨테이너(div)를 가져와 실제 지도 객체 생성
var markerpostion = new kakao.maps.LatLng(lat, lng);

//4. 마커 객체 생성
var marker = new kakao.maps.Marker({position: markerpostion});

//5. 마커를 생성한 지도 위에 표시
marker.setMap(map);
