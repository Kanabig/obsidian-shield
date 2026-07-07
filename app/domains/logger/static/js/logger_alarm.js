// SSE 연결
const source = new EventSource("/event_log/stream_log");

// 알림음
const audio = new Audio("/static/audio/ding.mp3");

// 마지막으로 받은 로그 ID
let lastLogId = null;


// 페이지 최초 로드
window.addEventListener("load", function() {

    const firstEventId = document.querySelector(".event_id");

    if(firstEventId) {
        lastLogId = firstEventId.innerText.trim();
    }
});


// SSE 수신
source.onmessage = async function() {

    console.log("새 로그 발생");

    audio.play().catch(function(err) {
        console.log("알림음 재생 실패", err);
    });

    showToast("새 로그가 발생했습니다.");

    if(lastLogId === null){
        return;
    }

    const response = await fetch(`/event_log/new?after=${lastLogId}`);

    if (!response.ok) {
        return;
    }

    const logs = await response.json();

    logs.forEach(function(log) {

        addLogRow(log);

        increaseBadge();
    });

    if(logs.length > 0) {
        lastLogId = logs[logs.length-1].ID;
    }
};


function addLogRow(log) {
    const tbody = document.getElementById("event_log_body");

    if(!tbody){
        return;
    }

    const tr = document.createElement("tr");

    tr.classList.add("new_log");

    tr.innerHTML = `
        <td>
            <input class="log_check" type="checkbox" value="${log.ID}">
        </td>
        <td></td>

        <td class="event_id">
            {{log.ID}}
        </td>
        <td>${log.REG_DATE}</td>
        <td>${log.latitude}</td>
        <td>${log.longitude}</td>
        <td>${log.TARGET_ID}</td>
        <td>
            <span class="unchecked">
                읽지 않음
            </span>        
        </td>
    `;

    tbody.prepend(tr);

    refreshRowNumber();

    setTimeout(function() {

        tr.classList.remove("new_log");

    }, 3000);
}


function showToast(text) {
    const container = document.getElementById("toast_container");

    if(!container) {
        return;
    }

    const div = document.createElement("div");

    div.className = "toast";

    div.innerText = text;

    container.appendChild(div);
    
    setTimeout(function() {

        div.remove();

    },3000);
}


function increaseBadge() {
    const badge = document.getElementById("log_badge");

    if(!badge)
        return;

    badge.innerText = Number(badge.innerText) + 1;
}