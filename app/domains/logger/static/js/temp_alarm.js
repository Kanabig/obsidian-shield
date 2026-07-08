// ===========================================================
// logger_alarm.js
// 이벤트 로그 실시간 알림(SSE)
// ===========================================================



// ===========================================================
// 1. 전역 변수
// ===========================================================

// SSE 연결
const source = new EventSource("/event_log/stream_log");

// 알림음
const audio = new Audio("/static/audio/ding.wav");

// 마지막으로 받은 로그 ID
let lastLogId = null;



// ===========================================================
// 2. 페이지 최초 로드
// ===========================================================

console.log("logger_alarm.js 로드 완료");

window.addEventListener("load", function () {

    console.log("window.load 실행");

    const tbody =
        document.getElementById("event_log_body");

    console.log("tbody =", tbody);

    const firstEventId =
        document.querySelector(".event_id");

    console.log("event_id =", firstEventId);

    if (firstEventId) {
        lastLogId = firstEventId.innerText.trim();
    }

    console.log("초기 lastLogId =", lastLogId);
});



// ===========================================================
// 3. SSE 수신
// ===========================================================

source.onmessage = async function (event) {

    console.log("★★★★ SSE 수신 ★★★★");
    console.log(event.data);

    // ----------------------------
    // 알림음
    // ----------------------------

    audio.play().catch(function (err) {
        console.log("알림음 재생 실패", err);
    });


    // ----------------------------
    // Toast
    // ----------------------------

    showToast("새 로그가 발생했습니다.");


    // ----------------------------
    // 마지막 로그 확인
    // ----------------------------

    if (lastLogId === null) {
        return;
    }

    console.log("현재 lastLogId =", lastLogId);


    // ----------------------------
    // 서버에서 새 로그 요청
    // ----------------------------

    const response =
        await fetch(`/event_log/new?after=${lastLogId}`);

    console.log("response =", response);

    const logs =
        await response.json();

    console.log("받은 logs =", logs);


    // ----------------------------
    // 화면에 추가
    // ----------------------------

    logs.forEach(function (log) {

        console.log("추가할 로그 =", log);

        addLogRow(log);

        increaseBadge();

    });


    // ----------------------------
    // 마지막 로그 ID 갱신
    // ----------------------------

    if (logs.length > 0) {
        lastLogId = logs[logs.length - 1].ID;
    }

    console.log("새 lastLogId =", lastLogId);

};



// ===========================================================
// 4. 로그 행 추가
// ===========================================================

function addLogRow(log) {

    console.log("addLogRow 실행");
    console.log(log);

    const tbody =
        document.getElementById("event_log_body");

    console.log("tbody =", tbody);

    if (!tbody) {

        console.log("tbody 없음");

        return;
    }


    // 이미 존재하면 추가하지 않음
    if (document.querySelector(`input[value="${log.ID}"]`)) {

        console.log("이미 존재하는 로그");

        return;
    }

    console.log("행 추가 시작");

    const tr = document.createElement("tr");

    tr.classList.add("new_log");

    tr.innerHTML = `
        <td>
            <input
                class="log_check"
                type="checkbox"
                value="${log.ID}">
        </td>

        <td></td>

        <td class="event_id">
            ${log.ID}
        </td>

        <td>${log.REG_DATE}</td>

        <td>${log.latitude}</td>

        <td>${log.longitude}</td>

        <td>${log.TARGET_ID}</td>

        <td>
            <span class="unchecked">
                읽지않음
            </span>
        </td>
    `;

    tbody.prepend(tr);

    console.log("행 추가 완료");

    refreshRowNumber();

    setTimeout(function () {

        tr.classList.remove("new_log");

    }, 3000);

}



// ===========================================================
// 5. Toast 출력
// ===========================================================

function showToast(text) {

    const container =
        document.getElementById("toast_container");

    if (!container) {
        return;
    }

    const div =
        document.createElement("div");

    div.className = "toast";

    div.innerText = text;

    container.appendChild(div);

    setTimeout(function () {

        div.remove();

    }, 3000);

}



// ===========================================================
// 6. Badge 증가
// ===========================================================

function increaseBadge() {

    const badge =
        document.getElementById("log_badge");

    if (!badge) {
        return;
    }

    badge.innerText =
        Number(badge.innerText) + 1;

}