(function () {
    const container = document.getElementById("dashboardMap");

    if (!container || !Array.isArray(dashboardMapData) || dashboardMapData.length === 0) {
        return;
    }

    if (!window.kakao || !window.kakao.maps) {
        container.classList.add("map_load_error");
        container.innerHTML = "<div>지도를 불러오지 못했습니다.</div>";
        return;
    }

    const firstTarget = dashboardMapData[0];
    const map = new kakao.maps.Map(container, {
        center: new kakao.maps.LatLng(firstTarget.latitude, firstTarget.longitude),
        level: 5,
    });

    const bounds = new kakao.maps.LatLngBounds();
    let openedInfoWindow = null;

    dashboardMapData.forEach(function (target) {
        const currentPosition = new kakao.maps.LatLng(target.latitude, target.longitude);
        bounds.extend(currentPosition);

        let markerOptions = {
            map: map,
            position: currentPosition,
        };

        if (target.image) {
            markerOptions.image = new kakao.maps.MarkerImage(
                dashboardMapImageBaseUrl + target.image,
                new kakao.maps.Size(44, 44)
            );
        }

        const marker = new kakao.maps.Marker(markerOptions);
        const linePath = [];

        (target.logs || []).forEach(function (log) {
            const point = new kakao.maps.LatLng(log.latitude, log.longitude);
            linePath.push(point);
            bounds.extend(point);
        });

        if (linePath.length > 1) {
            new kakao.maps.Polyline({
                map: map,
                path: linePath,
                strokeWeight: 3,
                strokeColor: target.color,
                strokeOpacity: 0.75,
                strokeStyle: "solid",
            });
        }

        const infoWindow = new kakao.maps.InfoWindow({
            content: `
                <div class="dashboard_map_info">
                    <strong>${target.name}</strong>
                    <span>${target.short_description || "탐지 대상"}</span>
                    <small>${target.reg_date || ""}</small>
                </div>
            `,
        });

        kakao.maps.event.addListener(marker, "click", function () {
            if (openedInfoWindow === infoWindow) {
                infoWindow.close();
                openedInfoWindow = null;
                return;
            }

            if (openedInfoWindow) {
                openedInfoWindow.close();
            }

            infoWindow.open(map, marker);
            openedInfoWindow = infoWindow;
        });
    });

    if (dashboardMapData.length > 1) {
        map.setBounds(bounds, 38, 38, 38, 38);
    }

    kakao.maps.event.addListener(map, "idle", function () {
        container.classList.add("is_loaded");
    });
})();
